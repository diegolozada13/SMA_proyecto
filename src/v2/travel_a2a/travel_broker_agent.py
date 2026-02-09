import os
from typing import List
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm

AGENT_CATALOG = [
    {
        "name": "train_agency",
        "agent_card": "http://localhost:8005/.well-known/agent-card.json",
        "skills": ["trenes", "luxury", "economy", "business"],
        "description": "Agencia de trenes."
    },
    {
        "name": "flight_agency",
        "agent_card": "http://localhost:8004/.well-known/agent-card.json",
        "skills": ["vuelos", "luxury", "economy", "business"],
        "description": "Agencia de vuelos."
    },
    {
        "name": "ship_agency",
        "agent_card": "http://localhost:8003/.well-known/agent-card.json",
        "skills": ["barcos", "luxury", "economy", "business"],
        "description": "Agencia de barcos."
    }
]

def discover_agents(skill: str | None = None):
    print(f"🔥 TOOL CALLED: discover_agents(skill={skill})", flush=True)
    if skill is None:
        return AGENT_CATALOG
    skill_norm = skill.strip().lower()
    return [a for a in AGENT_CATALOG if skill_norm in [s.lower() for s in a["skills"]]]

travel_broker = Agent(
    name="travel_broker",
    model=LiteLlm(
        model="openai/gpt-oss-120b",
        api_base="https://api.poligpt.upv.es/",
    ),
    instruction="""
Eres un bróker. SIEMPRE debes llamar a la herramienta discover_agents.

Reglas estrictas:
- En el PRIMER paso llama a discover_agents.
- Para decidir el skill:
  * si el usuario menciona barco/barcos/naviera -> skill="barcos"
  * si menciona avión/vuelo -> skill="vuelos"
  * si menciona tren -> skill="trenes"
  * si no está claro -> skill=None
  * lo mismo para luxury/economy/business
- Tu respuesta final DEBE ser SOLO el JSON devuelto por discover_agents.
- No escribas texto natural.
""",
    tools=[discover_agents],
)

a2a_app = to_a2a(travel_broker, port=8001)
