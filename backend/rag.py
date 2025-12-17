import os
import uuid
from typing import Optional, Tuple, List

from dotenv import load_dotenv
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

load_dotenv()

class RAGPipeline:
    def __init__(self) -> None:
        # Qdrant setup
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("QDRANT_COLLECTION", "hackathon-book")

        if not qdrant_url or not qdrant_api_key:
            print("Warning: Qdrant not configured")
            self.qdrant: Optional[QdrantClient] = None
        else:
            self.qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            print(f"Connected to Qdrant: {qdrant_url}")

        # Gemini setup
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY missing!")

        genai.configure(api_key=gemini_api_key)

        # Get available models and find a working one
        env_model = os.getenv("GEMINI_MODEL")
        preferred_models = []
        if env_model:
            # Remove 'models/' prefix if present
            clean_env_model = env_model.replace('models/', '')
            preferred_models.append(clean_env_model)
        
        # Add fallback models
        preferred_models.extend(["gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro"])
        
        # Try to find an available model
        self.chat_model_name = None
        try:
            models = genai.list_models()
            available_model_names = []
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    model_name = model.name.replace('models/', '') if model.name.startswith('models/') else model.name
                    available_model_names.append(model_name)
            
            # Find first preferred model that's available
            for preferred in preferred_models:
                if preferred in available_model_names:
                    self.chat_model_name = preferred
                    break
            
            # If no preferred model found, use first available
            if not self.chat_model_name and available_model_names:
                self.chat_model_name = available_model_names[0]
                print(f"Warning: Using first available model: {self.chat_model_name}")
        except Exception as e:
            print(f"Warning: Could not list models, using default: {e}")
            # Fallback to default if listing fails
            self.chat_model_name = preferred_models[0] if preferred_models else "gemini-pro"
        
        if not self.chat_model_name:
            raise RuntimeError("No available Gemini models found!")
        
        self.embedding_model_name = os.getenv('GEMINI_EMBEDDING_MODEL', 'text-embedding-004')
        # Add 'models/' prefix if not present
        if not self.embedding_model_name.startswith('models/'):
            self.embedding_model_name = 'models/' + self.embedding_model_name

        self.chat_model = genai.GenerativeModel(
            self.chat_model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,  # Increased for better responses
            },
            safety_settings=[
                {"category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH},
                {"category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH},
                {"category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH},
                {"category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH},
            ]
        )
        print(f"Gemini model ready: {self.chat_model_name}")

    def embed(self, text: str) -> List[float]:
        result = genai.embed_content(
            model=self.embedding_model_name,
            content=text,
            task_type="retrieval_query",
        )
        return result["embedding"]

    def retrieve(self, query: str, limit: int = 10) -> List[str]:
        if not self.qdrant:
            print("Warning: Qdrant not configured, cannot retrieve context")
            return []
        try:
            import time
            start_time = time.time()
            query_vector = self.embed(query)
            embed_time = time.time() - start_time
            print(f"Embedding generated in {embed_time:.2f} seconds")
            
            print(f"Searching in collection: {self.collection_name}")
            search_start = time.time()
            results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True,
            )
            search_time = time.time() - search_start
            print(f"Qdrant search completed in {search_time:.2f} seconds")
            
            retrieved_texts = [hit.payload.get("text", "") for hit in results if hit.payload and hit.payload.get("text")]
            print(f"Retrieved {len(retrieved_texts)} results from Qdrant")
            if not retrieved_texts:
                print(f"Warning: No results found for query: {query[:50]}...")
            return retrieved_texts
        except Exception as e:
            print(f"Retrieval error: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def answer_question(
        self,
        question: str,
        selected_text: Optional[str] = None,
        conversation_id: Optional[str] = None,
        use_selection_only: bool = False,
    ) -> Tuple[str, str]:
        conversation_id = conversation_id or str(uuid.uuid4())

        # If use_selection_only is True, only use selected_text (don't search Qdrant)
        if use_selection_only:
            if selected_text and selected_text.strip():
                context = selected_text.strip()
                context_source = "selected_text_only"
                print(f"Using only selected text (length: {len(context)})")
            else:
                # This should not happen if frontend validation works, but handle it
                context = None
                context_source = "none"
                print("Warning: use_selection_only=True but no selected_text provided")
        elif selected_text and selected_text.strip():
            # Use selected text as additional context along with Qdrant results
            selected_context = selected_text.strip()
            retrieved = self.retrieve(question)
            if retrieved:
                context = f"Selected text:\n{selected_context}\n\n---\n\nBook content:\n" + "\n\n---\n\n".join(retrieved)
                context_source = "selected_text_and_qdrant"
                print(f"Using selected text + {len(retrieved)} chunks from Qdrant")
            else:
                context = selected_context
                context_source = "selected_text_fallback"
                print("Using selected text (no Qdrant results)")
        else:
            # No selected text, use Qdrant only
            retrieved = self.retrieve(question)
            if retrieved:
                context = "\n\n---\n\n".join(retrieved)
                context_source = "qdrant"
                print(f"Retrieved {len(retrieved)} chunks from Qdrant")
            else:
                context = None
                context_source = "none"
                print("Warning: No context retrieved from Qdrant")

        # Build prompt based on whether context is available
        # Limit context length to avoid token limits and speed up processing
        max_context_length = 8000  # Limit context to ~8000 chars
        if context and len(context) > max_context_length:
            context = context[:max_context_length] + "\n\n[Context truncated...]"
            print(f"Context truncated to {max_context_length} characters")
        
        if context:
            prompt = f"""You are a helpful assistant for the Physical AI & Humanoid Robotics textbook.

Answer the question using the provided context. Use clear, professional English. Be concise.

Context:
{context}

Question: {question}

Provide a clear, concise answer based on the context."""
        else:
            # If no context, still try to answer but note the limitation
            prompt = f"""You are a helpful assistant for the Physical AI & Humanoid Robotics textbook.

Question: {question}

Note: No specific context was retrieved from the book for this question. Please provide a helpful answer based on general knowledge about Physical AI and Humanoid Robotics, but mention that specific book content was not available.

Answer in clear, professional English."""

        try:
            import time
            start_time = time.time()
            print(f"Calling Gemini API with model: {self.chat_model_name}")
            print(f"Prompt length: {len(prompt)} characters")
            
            # Use generate_content (timeout handled by client library)
            response = self.chat_model.generate_content(prompt)
            
            elapsed_time = time.time() - start_time
            print(f"Gemini API response received in {elapsed_time:.2f} seconds")
            
            if response and hasattr(response, 'text') and response.text:
                answer = response.text.strip()
            else:
                print("Warning: Empty or invalid response from Gemini")
                answer = "I apologize, but I couldn't generate a response. Please try again."
        except Exception as e:
            print(f"Gemini error: {e}")
            import traceback
            traceback.print_exc()
            answer = f"I encountered an error while processing your question: {str(e)}. Please try again later."

        return answer, conversation_id