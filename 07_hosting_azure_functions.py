# 07 — Hosting an Agent with Azure Functions
# Deploy your agent so users and other agents can interact with it.
# This example uses AgentFunctionApp to expose an HTTP endpoint via
# the Durable Functions extension.
#
# Prerequisites:
#   uv add agent-framework-azurefunctions
#   az login
#   Set AZURE_OPENAI_ENDPOINT in .env
#
# Run locally with Azure Functions Core Tools:
#   func start
#
# Then invoke:
#   curl -X POST http://localhost:7071/api/agents/Joker/run \
#     -H "Content-Type: text/plain" \
#     -d "Tell me a short joke about cloud computing."

import os
from typing import Any

from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.azure import AgentFunctionApp
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()


def _create_agent() -> Any:
    """Create the Joker agent."""
    return Agent(
        client=OpenAIChatCompletionClient(
            model="gpt-5.4-mini",
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version="2024-12-01-preview",
            credential=AzureCliCredential(),
        ),
        name="Joker",
        instructions="You are good at telling jokes.",
    )


app = AgentFunctionApp(agents=[_create_agent()], enable_health_check=True, max_poll_retries=50)
