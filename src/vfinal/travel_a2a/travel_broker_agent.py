import os
from typing import List
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm
import json


AGENT_CATALOG = [
    {
        "name": "train_provider",
        "agent_card": "http://localhost:8033/.well-known/agent-card.json",
        "skills": ["trenes", "luxury", "economy", "business"],
        "description": "Agencia de trenes."
    },
    {
        "name": "flight_provider",
        "agent_card": "http://localhost:8013/.well-known/agent-card.json",
        "skills": ["vuelos", "luxury", "economy", "business"],
        "description": "Agencia de vuelos."
    },
    {
        "name": "ship_provider",
        "agent_card": "http://localhost:8023/.well-known/agent-card.json",
        "skills": ["barcos", "luxury", "economy", "business", "otros"],
        "description": "Agencia de barcos."
    }
]

def discover_agents(skill: str | None = None):
    """
    Busca y recupera información de conexión de agentes especializados en el catálogo.
    
    Args:
        skill (str, optional): La especialidad a buscar. 
                               Valores aceptados: "vuelos", "trenes", "barcos".
                               Si es None, devuelve todos los agentes.
    
    Returns:
        str: Un JSON con la lista de agentes que coinciden con el criterio.
    """
    print(f"TOOL CALLED: discover_agents(skill={skill})", flush=True)
    res = AGENT_CATALOG
    if skill is None:
        print(f"RETURNING ALL AGENTS ({len(AGENT_CATALOG)})")
        return json.dumps(res)
    skill_norm = skill.strip().lower()
    res = [a for a in AGENT_CATALOG if skill_norm in [s.lower() for s in a["skills"]]]
    print(f"FOUND {len(res)} AGENTS for skill '{skill_norm}' and its {res[0]['name']}")
    return json.dumps(res)

travel_broker = Agent(
    name="travel_broker",
    model=LiteLlm(
        model="openai/gpt-oss-120b",
        api_base="https://api.poligpt.upv.es/",
        api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"
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
- No escribas texto natural.
- Ahora con el agente descubierto
""",
    tools=[discover_agents],
    sub_agents=[train_provider, flight_provider, ship_provider],
)

a2a_app = to_a2a(travel_broker, port=8001)
