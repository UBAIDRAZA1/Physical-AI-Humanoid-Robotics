# Implementation Plan: 1-ai-textbook-platform

**Branch**: `1-ai-textbook-platform` | **Date**: 2025-12-10 | **Spec**: specs/1-ai-textbook-platform/spec.md

## Summary

We will ship an **AI-native Physical AI & Humanoid Robotics textbook** that pairs a Docusaurus v3 frontend with a FastAPI backend. Core feature set: Better-Auth login with onboarding survey, per-chapter personalization button, Roman Urdu toggle, and a RAG chatbot grounded in the book (OpenAI + Qdrant + Neon Postgres). Content tracks the 13-week course (ROS 2 → Gazebo/Unity → NVIDIA Isaac → VLA capstone). Frontend deploys to GitHub Pages; backend to Render.

### Feature snapshot (user-visible)

- RAG chatbot pinned in the book, with “answer from selection only” mode.
- Login/Signup via Better-Auth; capture hardware/software background at signup.
- Chapter-level **Personalize** button that rewrites explanations/lab hints to the user profile.
- Chapter-level **Roman Urdu** button that toggles chapter text and chatbot replies.
- Progress-aware labs, MCQs, and capstone checklist.

## Technical Context

**Language/Version**: Frontend: TypeScript/JavaScript (React, Docusaurus v3); Backend: Python (FastAPI).
**Primary Dependencies**:
*   Frontend: Docusaurus v3, MDX, Tailwind CSS, React.
*   Backend: FastAPI, Better-Auth, OpenAI Python SDK, Qdrant client, Psycopg (for Neon Postgres).
**Storage**: Neon Postgres (primary database), Qdrant (vector database for RAG).
**Testing**: NEEDS CLARIFICATION (specific testing frameworks and strategy for both frontend and backend).
**Target Platform**: Web browsers (frontend), Linux server (backend on Render).
**Project Type**: Web (frontend) + API (backend).
**Performance Goals**: Production-ready, implying high responsiveness and throughput, specific metrics NEEDS CLARIFICATION.
**Constraints**: Qdrant free tier, GitHub Pages for frontend deployment, Render for backend deployment. Production-ready quality.
**Scale/Scope**: Comprehensive textbook content, user authentication, personalization, RAG chatbot, Urdu translation, assessments, capstone projects.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Accessibility and Bilingualism**: Does the design account for both Simple English and Roman Urdu content?
- [x] **II. Comprehensive and Practical Learning**: Does the plan include theory, diagrams, code, labs, and MCQs?
- [x] **III. Interactive and Personalized Experience**: Is there a plan for the RAG chatbot and user personalization features?
- [x] **IV. Open and Automated Deployment**: Is the deployment strategy aligned with GitHub Pages automation?
- [x] **V. Secure and User-Centric Authentication**: Does the plan incorporate Better-Auth and a signup survey?
- [x] **VI. Modularity and Reusability**: Is the proposed architecture modular and components reusable?

## Project Structure

### Documentation (this feature)

```text
specs/1-ai-textbook-platform/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: The project will adopt a split web application structure with separate `backend/` and `frontend/` directories, aligning with the distinct technology stacks (FastAPI for backend, Docusaurus/React for frontend). This promotes clear separation of concerns and independent deployment.
