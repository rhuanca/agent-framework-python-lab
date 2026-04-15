# Microsoft Agent Framework — Python Equivalents

Python implementations of the patterns from Microsoft's [Agent Framework](https://github.com/microsoft/agent-framework), using the [`agent-framework`](https://pypi.org/project/agent-framework/) Python SDK with Azure OpenAI.

Based on the [Agent Framework Samples](https://github.com/microsoft/Agent-Framework-Samples) and the [official docs](https://learn.microsoft.com/en-us/agent-framework/).

## Setup

```bash
# Install dependencies
uv sync

# Authenticate with Azure
az login

# Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI endpoint
```

## Examples

| Example | Description | Run |
|---|---|---|
| `01_hello_world.py` | Single agent, one question, one answer | `uv run python 01_hello_world.py` |
| `02_agent_with_tools.py` | Agent with function calling (tool-call roundtrip) | `uv run python 02_agent_with_tools.py` |
| `03_multi_turn_session.py` | Interactive chat loop with conversation memory | `uv run python 03_multi_turn_session.py` |
| `04_two_agent_handoff.py` | Triage agent routes to specialist agents | `uv run python 04_two_agent_handoff.py` |
