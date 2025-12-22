# Physical AI & Humanoid Robotics

**Live Demo:** [https://physical-ai-humanoid-robotics-ubaid.vercel.app/](https://physical-ai-humanoid-robotics-ubaid.vercel.app/)

This project is an interactive **AI-powered Book Assistant** for the topic *Physical AI & Humanoid Robotics*. It allows users to ask questions related to the subject and get instant, detailed answers from a dedicated backend powered by **Hugging Face Spaces**.

### Features

- **Ask Questions:** Type any question about Physical AI or Humanoid Robotics and get an instant AI-generated response.  
- **Selected Text Mode:** Highlight text in the book and ask questions specifically about the selected content.  
- **Conversation Tracking:** Maintains a conversation ID for follow-up questions.  
- **Interactive UI:** User-friendly chat interface with real-time typing indicators.  
- **Backend Integration:** Connects seamlessly with a deployed Hugging Face Space backend (`/chat` endpoint) for AI responses.  

### Tech Stack

- **Frontend:** Next.js + React + TypeScript  
- **Styling:** CSS Modules  
- **Backend:** FastAPI deployed on Hugging Face Spaces  
- **AI:** RAG Pipeline for question answering  

### How to Use

1. Open the [Live Demo](https://physical-ai-humanoid-robotics-ubaid.vercel.app/).  
2. Type your question in the chat box.  
3. Optionally, select any text from the book and enable “Answer only from selected text.”  
4. Press **Ask** and get a detailed AI-generated answer.

Locally:
Frontend Run in physical-ai-book(powershell)
npm run start

Backend Run in backend folder (cmd prompt)
.\venv\Scripts\Activate

uvicorn main:app --reload


