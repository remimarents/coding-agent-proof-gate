# Positioning

The narrow claim:

> A coding-agent task is not complete until external evidence supports the completion claim.

This project should stay small. Its job is not to plan, code, chat, browse, remember, or orchestrate a whole agent system. Its job is to say yes or no after an agent says done.

Good integrations:

- OpenHands completion checks
- CrewAI task callbacks or guardrails
- LangGraph final verification nodes
- GitHub Actions after an AI-generated PR
- local coding-agent wrappers

Non-goals:

- agent reputation
- cryptographic identity
- payment settlement
- browser automation
- private memory or personal assistant features
