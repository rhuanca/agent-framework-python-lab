import os

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from openai import AzureOpenAI

load_dotenv()


def get_client() -> AzureOpenAI:
    credential = AzureCliCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_ad_token=token.token,
        api_version="2024-12-01-preview",
    )


client = get_client()

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[
        {"role": "system", "content": "You are a friendly assistant. Keep answers brief."},
        {"role": "user", "content": "What is the largest city in France?"},
    ],
)

print(response.choices[0].message.content)
