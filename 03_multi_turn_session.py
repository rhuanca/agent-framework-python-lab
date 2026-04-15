# 03 — Multi-Turn Conversation (Session State)
# Interactive chat loop where the agent remembers context across turns.
# A session keeps conversation history so follow-up questions work naturally.

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
    instructions="You are a helpful data engineering tutor.",
)

session = agent.create_session()


async def main():
    print("Chat with the agent (type 'exit' to quit)")

    while True:
        user_input = input("You: ")
        if not user_input or user_input == "exit":
            break

        result = await agent.run(user_input, session=session)
        print(f"Agent: {result.text}")


asyncio.run(main())
