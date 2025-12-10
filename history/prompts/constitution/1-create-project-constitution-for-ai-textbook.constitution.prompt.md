---
id: 1
title: Create Project Constitution for AI Textbook
stage: constitution
date: 2025-12-09
surface: agent
model: gemini
feature: none
branch: main
user: placeholder
command: /sp.constitution Create ultimate Panaversity textbook "Physical AI & Humanoid Robotics". Simple English + Roman Urdu. Every chapter: theory, Mermaid diagrams, Python/ROS 2 code, labs, hardware list, MCQs, buttons for "Personalize" & "اردو میں پڑھیں". Add RAG chatbot, Better-Auth signup with survey, GitHub Pages deploy.
labels: [constitution]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .specify/templates/plan-template.md
  - .specify/templates/spec-template.md
  - .specify/templates/tasks-template.md
tests:
  - none
---

## Prompt

/sp.constitution Create ultimate Panaversity textbook "Physical AI & Humanoid Robotics". Simple English + Roman Urdu. Every chapter: theory, Mermaid diagrams, Python/ROS 2 code, labs, hardware list, MCQs, buttons for "Personalize" & "اردو میں پڑھیں". Add RAG chatbot, Better-Auth signup with survey, GitHub Pages deploy.

## Response snapshot

I have created the project constitution and updated the relevant templates.

- **Created**: `.specify/memory/constitution.md`
- **Updated**:
  - `.specify/templates/plan-template.md`
  - `.specify/templates/spec-template.md`
  - `.specify/templates/tasks-template.md`

## Outcome

- ✅ Impact: Created a new project constitution and aligned the project templates with it.
- 🧪 Tests: No tests were run.
- 📁 Files: 4 files were modified.
- 🔁 Next prompts: The user can now proceed with creating a spec for a feature.
- 🧠 Reflection: The process of deriving principles from a project description and then updating templates is a good way to establish a solid foundation for a project.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): n/a
