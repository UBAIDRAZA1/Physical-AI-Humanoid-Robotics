# Quickstart Guide: AI Textbook Platform

**Branch**: `1-ai-textbook-platform` | **Date**: 2025-12-10 | **Spec**: specs/1-ai-textbook-platform/spec.md

## Overview

This guide provides instructions to set up and run the AI Textbook Platform locally for development and testing. The project consists of a frontend (Docusaurus/React) and a backend (FastAPI).

## Prerequisites

*   Git
*   Node.js (LTS version) & npm or yarn
*   Python 3.10+ & pip
*   Docker (Optional, for running external services like Qdrant/Postgres locally)

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/ai-textbook-platform.git
cd ai-textbook-platform
```

## 2. Backend Setup (FastAPI)

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```
2.  **Create a Python virtual environment and activate it**:
    ```bash
    python -m venv .venv
    # On Windows:
    .\.venv\Scripts\activate
    # On macOS/Linux:
    source ./.venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    (Note: `requirements.txt` will be generated during implementation, containing FastAPI, Better-Auth, OpenAI SDK, psycopg, etc.)

4.  **Set up environment variables**:
    Create a `.env` file in the `backend/` directory based on a `.env.example` (which will be provided during implementation).
    Example variables will include:
    ```
    DATABASE_URL="postgresql://user:password@host:port/dbname"
    QDRANT_URL="http://localhost:6333"
    OPENAI_API_KEY="your_openai_api_key"
    BETTER_AUTH_SECRET_KEY="your_secret_key"
    ```

5.  **Run database migrations**:
    (Command will be specified during implementation, likely `alembic upgrade head` for SQLAlchemy or similar for other ORMs)

6.  **Start the backend server**:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

## 3. Frontend Setup (Docusaurus/React)

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```
2.  **Install dependencies**:
    ```bash
    npm install # or yarn install
    ```
3.  **Set up environment variables**:
    Create a `.env` file in the `frontend/` directory based on a `.env.example`.
    Example variables will include:
    ```
    VITE_BACKEND_API_URL="http://localhost:8000"
    ```

4.  **Start the frontend development server**:
    ```bash
    npm start # or yarn start
    ```
    The Docusaurus site will be available at `http://localhost:3000`.

## 4. Running External Services (Optional, via Docker)

For local development, you might need to run PostgreSQL and Qdrant. A `docker-compose.yml` will be provided during implementation.
```bash
docker-compose up -d postgres qdrant
```
