# 02 — Agent with Tools (Function Calling)
# The agent calls a local Python function when it needs external data.
# The framework handles tool schema generation and the call roundtrip automatically.
# Define a function with the @tool decorator and pass it to `tools=`.

import asyncio
import os
from random import randint
from typing import Annotated

from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from pydantic import Field

from agent_framework import Agent, tool
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()


# NOTE: approval_mode="never_require" is for sample brevity.
# Use "always_require" in production for user confirmation before tool execution.
@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


client = OpenAIChatCompletionClient(
    model="gpt-5.4-mini",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-12-01-preview",
    credential=AzureCliCredential(),
)

agent = Agent(
    client=client,
    name="WeatherAgent",
    instructions="You are a helpful weather assistant.",
    tools=[get_weather],
)


async def main():
    result = await agent.run("What's the weather like in La Paz?")
    print(f"Agent: {result}")


asyncio.run(main())
