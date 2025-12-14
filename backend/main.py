from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import RAGPipeline

# Auth is completely optional - don't import if it causes issues
AUTH_AVAILABLE = False
auth_router = None
get_current_user_optional = None
User = None
DATABASE_URL = None

# Try to import auth modules only if needed (commented out for now)
# try:
#     from auth_routes import router as auth_router, get_current_user_optional
#     from database import User, init_db, DATABASE_URL
#     AUTH_AVAILABLE = True
# except Exception as e:
#     print(f"Warning: Authentication modules not available: {e}")
#     AUTH_AVAILABLE = False

app = FastAPI(title="Physical AI RAG Backend")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

rag = RAGPipeline()

# Authentication routes disabled for now (can be enabled later if needed)
# if AUTH_AVAILABLE and auth_router:
#     try:
#         if DATABASE_URL:
#             app.include_router(auth_router)
#             print("Authentication routes enabled")
#         else:
#             print("Warning: DATABASE_URL not set. Authentication routes disabled.")
#     except Exception as e:
#         print(f"Warning: Could not load authentication routes: {e}")
# else:
print("Authentication routes disabled. Chat endpoint works without auth.")


class ChatRequest(BaseModel):
  question: str
  selected_text: Optional[str] = None
  conversation_id: Optional[str] = None
  use_selection_only: Optional[bool] = False


class ChatResponse(BaseModel):
  answer: str
  conversation_id: str


@app.get("/health")
async def health() -> dict:
  return {"status": "ok"}


@app.get("/check-qdrant")
async def check_qdrant() -> dict:
  """
  Check Qdrant connection and collection status.
  """
  try:
    if not rag.qdrant:
      return {
        "status": "error",
        "message": "Qdrant not configured",
        "qdrant_configured": False,
      }
    
    # Check if collection exists
    try:
      collection_info = rag.qdrant.get_collection(rag.collection_name)
      return {
        "status": "success",
        "qdrant_configured": True,
        "collection_name": rag.collection_name,
        "collection_points_count": collection_info.points_count,
        "collection_config": {
          "vector_size": collection_info.config.params.vectors.size if hasattr(collection_info.config.params, 'vectors') else None,
        },
        "message": f"Qdrant connected. Collection '{rag.collection_name}' has {collection_info.points_count} points.",
      }
    except Exception as e:
      return {
        "status": "error",
        "qdrant_configured": True,
        "collection_name": rag.collection_name,
        "error": str(e),
        "message": f"Qdrant connected but collection '{rag.collection_name}' not found or error accessing it.",
      }
  except Exception as e:
    return {
      "status": "error",
      "error": str(e),
      "error_type": type(e).__name__,
      "message": "Error checking Qdrant status.",
    }


@app.get("/list-models")
async def list_models() -> dict:
  """
  List all available Gemini models.
  """
  try:
    import google.generativeai as genai
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
      return {
        "status": "error",
        "error": "GEMINI_API_KEY not found",
        "message": "GEMINI_API_KEY missing in .env file.",
      }
    
    genai.configure(api_key=gemini_api_key)
    
    # List available models
    models = genai.list_models()
    model_list = []
    for model in models:
      if 'generateContent' in model.supported_generation_methods:
        model_list.append({
          "name": model.name,
          "display_name": model.display_name,
          "description": model.description,
        })
    
    return {
      "status": "success",
      "models": model_list,
      "count": len(model_list),
    }
  except Exception as e:
    return {
      "status": "error",
      "error": str(e),
      "error_type": type(e).__name__,
      "message": "Failed to list models.",
    }


@app.get("/test-gemini")
async def test_gemini() -> dict:
  """
  Quick Gemini connectivity test.
  """
  try:
    import google.generativeai as genai
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
      return {
        "status": "error",
        "error": "GEMINI_API_KEY not found in environment",
        "error_type": "ConfigurationError",
        "message": "GEMINI_API_KEY missing in .env file.",
      }
    
    genai.configure(api_key=gemini_api_key)
    
    # First, get list of available models
    try:
      models = genai.list_models()
      available_models = []
      for model in models:
        if 'generateContent' in model.supported_generation_methods:
          # Extract model name (remove 'models/' prefix if present)
          model_name = model.name.replace('models/', '') if model.name.startswith('models/') else model.name
          available_models.append(model_name)
    except Exception as e:
      return {
        "status": "error",
        "error": f"Failed to list models: {str(e)}",
        "error_type": type(e).__name__,
        "message": "Could not fetch available models from Gemini API.",
      }
    
    if not available_models:
      return {
        "status": "error",
        "error": "No models found",
        "message": "No available models found. Check your API key permissions.",
      }
    
    # Try models in order: env var, then available models
    env_model = os.getenv("GEMINI_MODEL")
    model_names_to_try = []
    if env_model:
      # Remove 'models/' prefix if present
      clean_env_model = env_model.replace('models/', '')
      if clean_env_model in available_models:
        model_names_to_try.append(clean_env_model)
    
    # Add other available models
    for model in available_models:
      if model not in model_names_to_try:
        model_names_to_try.append(model)
    
    # Try each model
    last_error = None
    for test_model_name in model_names_to_try:
      try:
        test_model = genai.GenerativeModel(test_model_name)
        response = test_model.generate_content("Say hello in one word.")
        
        return {
          "status": "success",
          "model": test_model_name,
          "response": response.text if hasattr(response, "text") else str(response),
          "message": "Gemini API is working correctly!",
          "available_models": available_models,
        }
      except Exception as e:
        last_error = e
        continue
    
    # If all models failed, return error with available models list
    return {
      "status": "error",
      "error": str(last_error) if last_error else "All models failed",
      "error_type": type(last_error).__name__ if last_error else "ModelError",
      "message": f"Gemini API test failed. Tried {len(model_names_to_try)} models.",
      "tried_models": model_names_to_try,
      "available_models": available_models,
    }
  except Exception as e:
    return {
      "status": "error",
      "error": str(e),
      "error_type": type(e).__name__,
      "message": "Gemini API test failed. Check your GEMINI_API_KEY in .env file.",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
  import time
  start_time = time.time()
  
  if not req.question.strip():
    raise HTTPException(status_code=400, detail="Question is empty")

  # If use_selection_only is True but no selected_text, return error
  if req.use_selection_only and not req.selected_text:
    raise HTTPException(
      status_code=400, 
      detail="Please select some text first when using 'Answer only from selected text' mode"
    )

  try:
    answer, conv_id = await rag.answer_question(
      question=req.question,
      selected_text=req.selected_text,
      conversation_id=req.conversation_id,
      use_selection_only=req.use_selection_only,
    )
    elapsed = time.time() - start_time
    print(f"Total request time: {elapsed:.2f} seconds")
    return ChatResponse(answer=answer, conversation_id=conv_id)
  except Exception as e:
    elapsed = time.time() - start_time
    print(f"Request failed after {elapsed:.2f} seconds: {e}")
    raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
  import uvicorn

  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

