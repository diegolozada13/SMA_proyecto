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
    ERES UN MOTOR DE EJECUCIÓN AUTÓNOMO. 
    TU OBJETIVO ES CONECTAR AL USUARIO CON EL AGENTE QUE PUEDA RESOLVER SU PETICIÓN.
    
    DEFINICIÓN DE "HECHO":
    - Solo terminas cuando tengas la respuesta del agente final.
    - Si solo tienes un JSON con agentes -> NO HAS TERMINADO.
    - Si solo sabes quién puede ayudar -> NO HAS TERMINADO.

    REGLAS DE COMPORTAMIENTO (LEELAS ANTES DE RESPONDER):
    1. EL USUARIO ES CIEGO A LOS PASOS INTERMEDIOS. No le muestres JSONs ni le digas "voy a contactar...". ¡HAZLO DIRECTAMENTE!
    2. SI RECIBES DATOS DEL BROKER: Tu reacción inmediata OBLIGATORIA es llamar a la herramienta `call_a2a_agent`.
    3. PROHIBIDO PEDIR CONFIRMACIÓN ("¿Quieres que llame a este agente?"). Asume que la respuesta es SI y llama.

    TU FLUJO MENTAL:
    Paso 1: Llamo a Broker -> Recibo JSON.
    Paso 2: (Sin hablar al usuario) Extraigo URL del JSON y llamo a `call_a2a_agent`.
    Paso 3: Recibo info del viaje -> SE LA MUESTRO AL USUARIO.
    """,
    sub_agents=[broker],
    tools=[call_a2a_agent],
)