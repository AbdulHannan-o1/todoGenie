---
id: "001"
title: "System Prompt Update and Deployment"
stage: "general"
date_iso: "2026-02-06"
surface: "agent"
model: "Claude Opus 4.5"
feature: "none"
branch: "001-advanced-features"
user: "abdulhannan"
command: "Update system prompt and deploy to minikube"
labels:
  - "system-prompt"
  - "deployment"
  - "minikube"
  - "docker"
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "phase5/backend/src/services/ai_agent/main_service.py"
  - "phase5/backend/systemprompt.md"
  - "phase5/backend/Dockerfile"
  - "phase5/frontend/Dockerfile"
  - "phase5/helm-charts/todogenie/values.yaml"
tests_yaml:
  - "Docker build tests"
  - "Minikube deployment tests"
---

# System Prompt Update and Deployment

## PROMPT_TEXT

```
explore the agents system prompt in code base and show the file here
okay remove the system prompt completly now
the path i pasted is the freshly written system prompt for the agent check it out and convert it into markdown formate with proper heading and list means poper orientation(you can update the content if neede but ask first before updating ) and save it as systemprompt.md in side backend and use in agent by importing it
yes clean it up
run the backend server
commit and push on github
build docker images for both frontned and backend then trigger deploymentin minikube
```

## RESPONSE_TEXT

Updated the AI agent's system prompt implementation by:
1. Removing the hardcoded system prompt from main_service.py
2. Creating a dynamic system prompt loading mechanism from systemprompt.md file
3. Converting the provided system prompt into a well-formatted markdown file
4. Fixing syntax errors in main_service.py that prevented server startup
5. Successfully running the backend server with the new system prompt
6. Building Docker images for both frontend and backend
7. Deploying the application to minikube using Helm charts

## OUTCOME

Successfully implemented dynamic system prompt loading for the AI agent and deployed the application to minikube. The changes allow for easier modification of the agent's behavior through external configuration rather than code changes.

## EVALUATION

The implementation was successful:
- System prompt is now loaded from an external markdown file
- Syntax errors in main_service.py were fixed
- Backend server runs successfully with the new implementation
- Docker images were built for both frontend and backend
- Application deployed to minikube with proper service connectivity