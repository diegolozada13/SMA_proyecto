import uvicorn
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm
from typing import List


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

def discover_agents(skill: str | List[str] | None = None):
    print(f"Discovering agents with skill: {skill}")
    return [
        agent for agent in AGENT_CATALOG if skill is None or skill in agent["skills"]
    ]

travel_broker = Agent(
    name="travel_broker",
    model=LiteLlm(
        model="openai/gpt-oss-120b", 
        api_base="https://api.poligpt.upv.es/", 
        api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"
    ),
    instruction="""
    Eres un Bróker de servicios bajo el protocolo A2A que recibe solicitudes de usuarios que quieren viajar.
    Tu función es recibir peticiones de usuarios y usar la herramienta 'discover_agents' 
    para hablar con el/los agentes para resolver la peticion. Por ejemplo, si el usuario pregunta por
    'Quiero viajar a las Maldivas en barco', deberías usar la herramienta 'discover_agents'
    con el skill 'barcos' para descubrir el agente 'ship_agency' y luego comunicarte con él para resolver
    la petición del usuario.
    
    REGLAS ESTRICTAS:
    - DEBES usar la herramienta 'discover_agents' para obtener los datos del agente.
    - NO respondas en lenguaje natural.
    - Devuelve ÚNICAMENTE el JSON crudo que genera la herramienta.
    """,
    tools=[discover_agents],
)

a2a_app = to_a2a(travel_broker, port=8001)

# if __name__ == "__main__":
#     uvicorn.run(a2a_app, host="localhost", port=8001)
