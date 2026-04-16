# Agent Framework Python Lab

> **Stack:** Python 3.13 / `agent-framework` SDK 1.0.1 / Azure OpenAI / uv
> **Purpose:** Hands-on learning examples for the Microsoft Agent Framework Python SDK

---

## Setup

```bash
uv sync
az login
cp .env.example .env   # set AZURE_OPENAI_ENDPOINT
```

## Project Conventions

- **Package manager:** `uv` (`uv add`, `uv run`, `uv sync`)
- **Env vars:** Loaded via `python-dotenv` (`load_dotenv()`) from `.env`
- **Examples are self-contained:** Each file includes its own client setup — no shared modules
- **Run any example:** `uv run python <example>.py`

## Examples

| File | Pattern | Key Concepts |
|---|---|---|
| `01_hello_world.py` | Single agent, one-shot | `OpenAIChatCompletionClient`, `.as_agent()`, `.run()` |
| `02_agent_with_tools.py` | Function calling | `Annotated` + `Field` for tool params, `tools=[fn]` |
| `03_multi_turn_session.py` | Conversation memory | `.create_session()`, `session=` on `.run()` |
| `04_two_agent_handoff.py` | Multi-agent routing | `HandoffBuilder`, `.add_handoff()`, `.with_autonomous_mode()` |
| `05_memory.py` | Context providers | `ContextProvider`, `SessionContext`, `extend_instructions()`, session state |
| `06_first_workflow.py` | Executor workflows | `Executor`, `WorkflowBuilder`, `@executor`, `@handler`, `send_message()`, `yield_output()` |
| `07_hosting_azure_functions.py` | Azure Functions hosting | `AgentFunctionApp`, Durable Functions, HTTP endpoint |

## Key SDK Patterns

```python
# Create a client + agent
from agent_framework.openai import OpenAIChatCompletionClient

agent = OpenAIChatCompletionClient(
    model="gpt-5.4-mini",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-12-01-preview",
    credential=AzureCliCredential(),
).as_agent(instructions="...", tools=[...])

# Run
result = await agent.run("prompt")
print(result.text)

# Handoff workflow
from agent_framework_orchestrations import HandoffBuilder
workflow = (
    HandoffBuilder(name="my-workflow")
    .participants([agent_a, agent_b])
    .add_handoff(source=agent_a, targets=[agent_b])
    .with_start_agent(agent_a)
    .with_autonomous_mode()
    .build()
)
result = await workflow.run("prompt")
```

## Key References

| Resource | URL |
|---|---|
| Agent Framework Docs | https://learn.microsoft.com/en-us/agent-framework/ |
| Python SDK (PyPI) | https://pypi.org/project/agent-framework/ |
| Function Tools (Python) | https://learn.microsoft.com/en-us/agent-framework/agents/tools/function-tools?pivots=programming-language-python |
| GitHub Repo | https://github.com/microsoft/agent-framework |
| Samples | https://github.com/microsoft/Agent-Framework-Samples |

## Tips

- **Handoff agents** require `require_per_service_call_history_persistence=True`
- **Tool descriptions matter:** Use `Annotated[str, Field(description="...")]` for params and docstrings for the function
- **Workflow results** use `result.get_outputs()`, not `result.text`
- **Auth:** `AzureCliCredential` from `azure-identity` — uses `az login`
