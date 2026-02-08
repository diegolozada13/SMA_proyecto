import uvicorn
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm


AGENT_CATALOG = [
    {
        "name": "",
        "agent_card": "http://localhost:8002/.well-known/agent-card.json",
        "skills": ["vuelos", "barcos", "trenes", "luxury", "economy", "business"],
        "description": "Agencia integral con conocimiento global de rutas marítimas y aéreas."
    }
]

def discover_agents(skill: str):
       return [
        agent for agent in AGENT_CATALOG
    ]

travel_broker_agent = Agent(
    name="travel_broker",
    model=LiteLlm(
        model="openai/gpt-oss-120b", 
        api_base="https://api.poligpt.upv.es/", 
        api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"
    ),
    instruction="""
    Eres un Bróker de servicios (Marketplace) bajo el protocolo A2A.
    Tu función es recibir peticiones de usuarios y usar la herramienta 'discover_agents' 
    para hablar con el agente para resolver la peticion.
    
    REGLAS ESTRICTAS:
    - DEBES usar la herramienta 'discover_agents' para obtener los datos del agente.
    - NO respondas en lenguaje natural.
    - Devuelve ÚNICAMENTE el JSON crudo que genera la herramienta.
    """,
    tools=[discover_agents],
)

a2a_app = to_a2a(travel_broker_agent, port=8001)
