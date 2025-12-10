# Research: 1-ai-textbook-platform

**Branch**: `1-ai-textbook-platform` | **Date**: 2025-12-10 | **Spec**: specs/1-ai-textbook-platform/spec.md

## Phase 0 Research Tasks and Findings

### 1. Research specific testing frameworks and strategies for Frontend (Docusaurus/React/TypeScript) and Backend (FastAPI/Python)

**Task**: Investigate best practices and suitable frameworks for unit, integration, and end-to-end testing for Docusaurus/React/TypeScript frontend and FastAPI/Python backend applications.

**Decision**:
*   **Frontend Testing**:
    *   Unit/Integration: React Testing Library with Jest.
    *   End-to-End (E2E): Playwright (for cross-browser compatibility and robust automation).
*   **Backend Testing**:
    *   Unit/Integration: Pytest with FastAPI's TestClient.
    *   API Contract Testing: Pydantic models for request/response validation.
**Rationale**: These frameworks are widely adopted, well-documented, and provide comprehensive features for ensuring code quality across both frontend and backend. Playwright offers superior E2E capabilities compared to alternatives, and Pydantic provides strong typing and validation for API contracts.
**Alternatives considered**:
*   Frontend E2E: Cypress (chosen Playwright for better cross-browser support and tracing).
*   Backend Unit: unittest (chosen Pytest for its simplicity and rich plugin ecosystem).

### 2. Define specific performance metrics and goals for "Production-ready"

**Task**: Research common performance benchmarks and goals for educational web applications and API services to define concrete metrics for responsiveness, throughput, and concurrent users, considering the constraints of GitHub Pages (frontend) and Render (backend) free tiers, and Qdrant free tier.

**Decision**:
*   **Frontend (User Experience)**:
    *   Largest Contentful Paint (LCP): < 2.5 seconds (mobile & desktop).
    *   First Input Delay (FID): < 100 milliseconds.
    *   Cumulative Layout Shift (CLS): < 0.1.
    *   Lighthouse Performance Score: > 85.
*   **Backend (API & RAG)**:
    *   API Response Time (p95): < 200 milliseconds for core textbook content retrieval.
    *   API Response Time (p95): < 500 milliseconds for RAG chatbot responses.
    *   Concurrency: Support 100 concurrent active users.
    *   Throughput: Handle 500 requests per minute (RPM).
    *   RAG Retrieval Latency: Qdrant vector search < 50ms.
**Rationale**: These metrics provide a balanced view of user experience and backend efficiency, aligning with typical "production-ready" expectations for a modern web application. The targets are ambitious but achievable within the specified free-tier constraints with careful optimization, and the RAG-specific latency ensures a responsive chatbot experience.
**Alternatives considered**: More aggressive performance targets (rejected due to free-tier constraints and the nature of an educational platform not requiring ultra-low latency for all operations). Simpler metrics (rejected for not providing enough detail for robust performance monitoring).
