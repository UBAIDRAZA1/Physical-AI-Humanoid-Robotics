# Spec-Kit Plus Integration Guide

This project uses **Spec-Kit Plus** for AI/Spec-Driven book creation as required by the hackathon.

## What is Spec-Kit Plus?

Spec-Kit Plus is a tool for creating AI-native technical textbooks using specification-driven development. It helps you:

- Generate book content from specifications
- Maintain consistency across chapters
- Use AI to assist in content creation
- Follow a structured workflow for book development

## Spec-Kit Plus Commands

These commands are used in Claude Code (or compatible AI coding environments):

### `/sp.constitution`
Initialize project principles and guidelines.

### `/sp.specify [chapter or section name]`
Define detailed requirements for a section.

### `/sp.clearify [question]`
Clarify ambiguous requirements.

### `/sp.plan [section or task]`
Create a structured implementation plan.

### `/sp.tasks [plan or section]`
Generate actionable task lists.

### `/sp.implement [task or section]`
Generate markdown/MDX content based on specs.

## Workflow for this project

1) `/sp.constitution`  
2) `/sp.specify` each module (ROS 2, Gazebo/Unity, Isaac, VLA)  
3) `/sp.plan` whole book  
4) `/sp.tasks` modules  
5) `/sp.implement` chapters  

## Docusaurus placement

Place generated markdown/MDX in `physical-ai-book/docs/`:
```
physical-ai-book/docs/
├── intro.md
├── module-1-ros2/
├── module-2-gazebo/
├── module-3-isaac/
└── module-4-vla/
```

## Current book structure

- Introduction (course overview, features, RAG/auth/personalization/Urdu)
- Module 1: ROS 2
- Module 2: Gazebo & Unity
- Module 3: NVIDIA Isaac
- Module 4: Vision-Language-Action
- Capstone: Autonomous Humanoid

Resources:
- Spec-Kit Plus: https://github.com/panaversity/spec-kit-plus
- Docusaurus MDX: https://docusaurus.io/docs/markdown-features/react
- Claude Code docs: https://code.claude.com/docs

