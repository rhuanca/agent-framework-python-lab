# 04 — Two-Agent Handoff Workflow
# A triage agent routes questions to specialized agents.
# The handoff pattern is decentralized — agents transfer control to each other
# via tool calls, and the full conversation history follows along.

import asyncio
import os

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework_orchestrations import HandoffBuilder

load_dotenv()

client = OpenAIChatCompletionClient(
    model="gpt-5.4-mini",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-12-01-preview",
    credential=AzureCliCredential(),
)

triage_agent = client.as_agent(
    name="TriageAgent",
    instructions=(
        "You are a triage agent. Determine if the user's question is about "
        "data engineering or code review, and hand off to the appropriate specialist."
    ),
    require_per_service_call_history_persistence=True,
)

data_expert = client.as_agent(
    name="DataExpert",
    instructions="You are a senior Data Engineer. Answer data questions in depth.",
    require_per_service_call_history_persistence=True,
)

code_reviewer = client.as_agent(
    name="CodeReviewer",
    instructions="You are a code review expert. Analyze and improve code snippets.",
    require_per_service_call_history_persistence=True,
)

workflow = (
    HandoffBuilder(name="triage-workflow")
    .participants([triage_agent, data_expert, code_reviewer])
    .add_handoff(source=triage_agent, targets=[data_expert, code_reviewer])
    .add_handoff(source=data_expert, targets=[triage_agent])
    .add_handoff(source=code_reviewer, targets=[triage_agent])
    .with_start_agent(triage_agent)
    .build()
)


async def main():
    result = await workflow.run(
        "Can you review this PySpark join and tell me if it has performance issues?"
    )
    for output in result.get_outputs():
        print(output.text)


asyncio.run(main())
