import os
import uuid
from typing import Optional, Tuple

from dotenv import load_dotenv
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels


load_dotenv()


class RAGPipeline:
  """
  Minimal RAG helper around Qdrant Cloud + Gemini (Google Generative AI).
  """

  def __init__(self) -> None:
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    self.collection_name = os.getenv("QDRANT_COLLECTION", "physical-ai-book")

    if not qdrant_url or not qdrant_api_key:
      self.qdrant: Optional[QdrantClient] = None
    else:
      self.qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
      raise RuntimeError("GEMINI_API_KEY is required")

    genai.configure(api_key=gemini_api_key)

    chat_model = os.getenv("GEMINI_MODEL", "gemini-pro")
    if chat_model.startswith("models/"):
      chat_model = chat_model.replace("models/", "", 1)
    self.chat_model_name = chat_model

    embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    if not embedding_model.startswith("models/"):
      embedding_model = f"models/{embedding_model}"
    self.embedding_model_name = embedding_model
    self.chat_model = genai.GenerativeModel(self.chat_model_name)

  def ensure_collection(self, vector_size: int = 768) -> None:
    if self.qdrant is None:
      return

    collections = self.qdrant.get_collections().collections
    existing = {c.name for c in collections}
    if self.collection_name in existing:
      return

    self.qdrant.create_collection(
      collection_name=self.collection_name,
      vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
    )

  def embed(self, text: str) -> list[float]:
    result = genai.embed_content(
      model=self.embedding_model_name,
      content=text,
      task_type="retrieval_document",
    )
    return result["embedding"]  # type: ignore[no-any-return]

  def upsert_documents(self, chunks: list[str]) -> None:
    if self.qdrant is None:
      raise RuntimeError("Qdrant client not configured")

    vectors = [self.embed(c) for c in chunks]
    points = [
      qmodels.PointStruct(id=str(uuid.uuid4()), vector=v, payload={"text": c})
      for v, c in zip(vectors, chunks)
    ]
    self.qdrant.upsert(collection_name=self.collection_name, points=points)

  def retrieve(self, query: str, limit: int = 4) -> list[str]:
    if self.qdrant is None:
      return []

    try:
      query_vector = self.embed(query)
      results = self.qdrant.search(
        collection_name=self.collection_name,
        query_vector=query_vector,
        limit=limit,
      )
      return [hit.payload.get("text", "") for hit in results if hit.payload]
    except Exception as e:  # pragma: no cover - diagnostic path
      print(f"Warning: Retrieval failed: {e}")
      return []

  async def answer_question(
    self,
    question: str,
    selected_text: Optional[str] = None,
    conversation_id: Optional[str] = None,
  ) -> Tuple[str, str]:
    if not conversation_id:
      conversation_id = str(uuid.uuid4())

    if selected_text and selected_text.strip():
      context_blocks = [selected_text.strip()]
    else:
      context_blocks = self.retrieve(question)

    context = "\n\n---\n\n".join(context_blocks) if context_blocks else "No additional context available."

    system_prompt = (
      "You are an AI assistant helping the reader of an online technical book. "
      "Answer questions strictly based on the provided context. "
      "If the answer is not in the context, say that you cannot find it in the book."
    )

    prompt = f"{system_prompt}\n\nBook context:\n{context}\n\nQuestion: {question}"

    try:
      response = self.chat_model.generate_content(prompt)
      if hasattr(response, "text") and response.text:
        answer = response.text
      elif hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
          answer = candidate.content.parts[0].text if candidate.content.parts else ""
        else:
          answer = str(candidate)
      else:
        answer = str(response) if response else "No response generated."

      if not answer or not answer.strip():
        answer = "I received an empty response from the AI model. Please try again."

    except Exception as e:  # pragma: no cover - diagnostic path
      error_msg = str(e)
      print(f"Error generating response: {error_msg}")
      print(f"Error type: {type(e).__name__}")

      if "404" in error_msg or "not found" in error_msg.lower():
        answer = (
          f"Model configuration error: The AI model '{self.chat_model_name}' was not found. "
          "Please check your GEMINI_MODEL setting in .env file. "
          "Valid models include: gemini-1.5-flash, gemini-1.5-pro, gemini-pro"
        )
      elif "401" in error_msg or "unauthorized" in error_msg.lower() or "api key" in error_msg.lower():
        answer = (
          "Authentication error: Invalid or missing GEMINI_API_KEY. "
          "Please check your .env file and ensure the API key is correct."
        )
      elif "timeout" in error_msg.lower() or "network" in error_msg.lower():
        answer = (
          "Network timeout: Could not connect to the AI service. "
          "Please check your internet connection and try again."
        )
      else:
        answer = (
          f"I encountered an error: {error_msg[:200]}. "
          "Please check your API configuration and try again."
        )

    return answer, conversation_id

