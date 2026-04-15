# 01 — Hello World
# Single agent, one question, one answer.
# Validates that auth, packages, and the model deployment all work.

import asyncio
import os

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()

agent = OpenAIChatCompletionClient(
    model="gpt-5.4-mini",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-12-01-preview",
    credential=AzureCliCredential(),
).as_agent(
    instructions="You are a friendly assistant. Keep answers brief.",
)


async def main():
    result = await agent.run("What is the largest city in France?")
    print(result.text)


asyncio.run(main())
