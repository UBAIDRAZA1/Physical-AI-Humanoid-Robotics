from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import RAGPipeline


app = FastAPI(title="Physical AI RAG Backend")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

rag = RAGPipeline()


class ChatRequest(BaseModel):
  question: str
  selected_text: Optional[str] = None
  conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
  answer: str
  conversation_id: str


@app.get("/health")
async def health() -> dict:
  return {"status": "ok"}


@app.get("/test-gemini")
async def test_gemini() -> dict:
  """
  Quick Gemini connectivity test.
  """
  try:
    import google.generativeai as genai

    test_model_name = "gemini-pro"
    test_model = genai.GenerativeModel(test_model_name)
    response = test_model.generate_content("Say hello in one word.")

    return {
      "status": "success",
      "model": test_model_name,
      "response": response.text if hasattr(response, "text") else str(response),
      "message": "Gemini API is working correctly!",
    }
  except Exception as e:  # pragma: no cover - diagnostic path
    return {
      "status": "error",
      "error": str(e),
      "error_type": type(e).__name__,
      "message": "Gemini API test failed. Check your GEMINI_API_KEY in .env file.",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
  if not req.question.strip():
    raise HTTPException(status_code=400, detail="Question is empty")

  answer, conv_id = await rag.answer_question(
    question=req.question,
    selected_text=req.selected_text,
    conversation_id=req.conversation_id,
  )
  return ChatResponse(answer=answer, conversation_id=conv_id)


if __name__ == "__main__":
  import uvicorn

  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

