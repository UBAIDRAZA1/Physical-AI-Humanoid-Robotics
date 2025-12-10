# Hackathon I: Physical AI & Humanoid Robotics Textbook

This repo combines the Docusaurus 3 book, the FastAPI RAG backend, and Spec-Kit Plus outputs.

- **Book (frontend)**: `physical-ai-book/` (Docusaurus 3)
- **RAG backend**: `backend/` (FastAPI + Qdrant + Gemini + Neon)
- **Chatbot UI**: `physical-ai-book/src/components/Chatbot/Chatbot.tsx`
- **Specs**: see `specs/` for Spec-Kit Plus artifacts

## Run the Docusaurus book locally

```bash
cd physical-ai-book
npm install
npm run start
```

## Run the RAG backend locally

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate  # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

Create `.env` in `backend/`:

```
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro
GEMINI_EMBEDDING_MODEL=text-embedding-004
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION=physical-ai-book
DATABASE_URL=postgresql://user:password@host/dbname
```

Start the API:

```bash
uvicorn main:app --reload --port 8000
```

Endpoints:
- `GET /health`
- `GET /test-gemini`
- `POST /chat`

## How the RAG chatbot works

- Frontend sends `{ question, selected_text?, conversation_id? }` to `/chat`.
- Backend uses selected text when present; otherwise embeds and retrieves from Qdrant, then calls Gemini to answer strictly from context.

## Deploy

- Frontend: GitHub Pages or Netlify (build `physical-ai-book`, publish `physical-ai-book/build`).
- Backend: Railway/Render/Fly.io. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
