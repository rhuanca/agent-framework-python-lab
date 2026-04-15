# 02 — Agent with Tools (Function Calling)
# The agent calls a local Python function when it needs external data.
# The framework handles tool schema generation and the call roundtrip automatically.
# Just define a function with type annotations and pass it to `tools=`.

import asyncio
import os
from typing import Annotated

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework.openai import OpenAIChatCompletionClient
from pydantic import Field

load_dotenv()


def get_weather(
    city: Annotated[str, Field(description="The city name, e.g. 'La Paz'")],
) -> str:
    """Get the current weather for a given city."""
    return f"It is sunny and 18°C in {city}."


agent = OpenAIChatCompletionClient(
    model="gpt-5.4-mini",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-12-01-preview",
    credential=AzureCliCredential(),
).as_agent(
    instructions="You are a helpful weather assistant.",
    tools=[get_weather],
)


async def main():
    result = await agent.run("What's the weather like in La Paz?")
    print(result.text)


asyncio.run(main())
