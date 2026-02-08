# root_agent.py
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)
from google.adk.models.lite_llm import LiteLlm

from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from a2a.client import A2AClient
import requests  
import json
import httpx
import uuid
#from a2a.types import Message, TextContent, MessageRole



def call_a2a_agent(agent_card_url: str, user_request: str) -> dict:
    """Dynamic A2A call compatible with your ADK remote agent."""

    card = requests.get(agent_card_url, timeout=10).json()
    service_url = card["url"]

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "conversationId": str(uuid.uuid4()),
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [
                    {"type": "text", "text": user_request}
                ]
            }
        }
    }

    resp = requests.post(service_url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # 4) intentar extraer artifacts (respuesta útil)
    result = data.get("result", {})
    artifacts = result.get("artifacts", [])

    if artifacts:
        parts = artifacts[0].get("parts", [])
        for p in parts:
            if p.get("kind") == "text" and not p.get("metadata", {}).get("adk_thought"):
                return {
                    "agent": card["name"],
                    "response": p["text"]
                }

    return {
        "agent": card["name"],
        "response": data
    }



broker = RemoteA2aAgent(
    name="travel_broker",
    description="Agent broker",
    agent_card="http://localhost:8001/.well-known/agent-card.json",
)


root_agent = Agent(
    name="client_agent",
    model=LiteLlm(model="openai/gpt-oss-120b", api_base="https://api.poligpt.upv.es/", api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"),
    instruction="""
You MUST follow this workflow:

1. Ask the travel broker for agents matching the user's requirement.
2. You will receive a JSON list of agents.
3. Select the FIRST agent from the list.
4. Call the tool `call_a2a_agent` using:
   - agent_card from the selected agent
   - the original user request
5. Return the tool result to the user.

You CANNOT invoke agents yourself.
You MUST use the tool.
""",
    sub_agents=[broker],
    tools=[call_a2a_agent],
)