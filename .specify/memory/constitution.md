<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- New principles:
  - I. Accessibility and Bilingualism
  - II. Comprehensive and Practical Learning
  - III. Interactive and Personalized Experience
  - IV. Open and Automated Deployment
  - V. Secure and User-Centric Authentication
  - VI. Modularity and Reusability
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
- Follow-up TODOs: None
-->
# Physical AI & Humanoid Robotics Constitution

## Core Principles

### I. Accessibility and Bilingualism
Content MUST be authored in both Simple English and Roman Urdu. The user interface MUST provide a seamless mechanism for users to toggle between languages. All content, including theoretical explanations, practical labs, and UI text, MUST be fully translated and culturally adapted for both target audiences to ensure the material is approachable and easy to understand for a global audience.

### II. Comprehensive and Practical Learning
Every chapter MUST provide a multi-faceted learning experience. This includes:
- Clear theoretical explanations of core concepts.
- Illustrative Mermaid diagrams to visualize complex systems and processes.
- Functional Python and ROS 2 code examples that are well-documented and directly applicable to the theory.
- Hands-on labs that guide the user through practical application of the concepts.
- A curated list of required or recommended hardware for the labs.
- Multiple-choice questions (MCQs) to allow self-assessment and knowledge reinforcement.

### III. Interactive and Personalized Experience
The platform MUST be interactive and adapt to the user's needs. This will be achieved through:
- A RAG (Retrieval-Augmented Generation) chatbot to answer user questions in context.
- A "Personalize" feature that allows users to tailor their learning path, driven by data from an initial signup survey.
- User-centric design that prioritizes ease of use and engagement.

### IV. Open and Automated Deployment
The project MUST be continuously integrated and deployed to GitHub Pages. All development practices should support this automated workflow, ensuring that the main branch is always in a deployable state. This embraces open-access principles, making the textbook freely available to a wide audience.

### V. Secure and User-Centric Authentication
User authentication MUST be handled by a secure and reliable service like Better-Auth. The signup process MUST be simple and include a user survey to gather information for personalizing the learning experience. User data privacy and security are paramount.

### VI. Modularity and Reusability
The codebase MUST be designed with modularity and reusability in mind. Features should be developed as loosely-coupled components, making them easier to test, maintain, and potentially reuse in other contexts. This applies to both front-end UI components and back-end services.

## Governance

This constitution is the single source of truth for all development principles and practices. All code contributions, architectural decisions, and feature implementations must align with it. Amendments to this constitution require a documented proposal, review by project maintainers, and a clear migration plan for any affected components. All pull requests and reviews must verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09