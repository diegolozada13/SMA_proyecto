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




def call_a2a_agent(agent_card_url: str, user_request: str) -> dict:

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



brokerAgent = RemoteA2aAgent(
    name="Broker",
    description="Agent broker",
    agent_card="http://localhost:8005/.well-known/agent-card.json",
)


root_agent = Agent(
    name="client_agent",
    model=LiteLlm(model="openai/gpt-oss-120b", api_base="https://api.poligpt.upv.es/", api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"),
    instruction="""
DEBES seguir estrictamente este flujo de trabajo:

1. Consulta al brokerAgent: Solicita al brokerAgent los agentes que coincidan con los requisitos del usuario.
2. Recepción de Datos: Recibirás una lista de agentes en formato JSON.
3. Selección: Selecciona el PRIMER agente de la lista recibida.
4. Invocación de Herramienta: Llama a la herramienta call_a2a_agent utilizando:
   - La agent_card del agente seleccionado.
   - La solicitud original del usuario.
5. Respuesta: Devuelve el resultado de la herramienta directamente al usuario.

RESTRICCIONES CRÍTICAS:
NO PUEDES invocar agentes por tu cuenta mediante lenguaje natural.
Es OBLIGATORIO el uso de la herramienta proporcionada para cualquier comunicación externa.
""",

    sub_agents=[brokerAgent],
    tools=[call_a2a_agent],
)