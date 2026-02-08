from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm

# ÚNICO agente disponible: agencia JS A2A
AGENT_CATALOG = [
    {
        "name": "boat_agency_js",
        "agent_card": "http://localhost:8011/.well-known/agent-card.json",
        "type": "travel_agency",
        "mode": "boat",
        "language": "javascript"
    }
]

def discover_agents():
    """
    Broker tool.
    Returns the list of available remote agents (A2A).
    In this version, there is only one JS-based agency.
    """
    return AGENT_CATALOG


broker_agent = Agent(
    name="broker_agent",
    model=LiteLlm(
        model="openai/gpt-oss-120b",
        api_base="https://api.poligpt.upv.es/",
        api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"
    ),
    instruction="""
You are a broker agent in a multi-agent system.

Your role is to act as a mediator between a client and remote service agents.
You do NOT provide travel offers yourself.
You do NOT invoke other agents directly.

Your task is to expose the list of available remote agents that can handle
travel-related requests.

Rules:
- You MUST call the provided tool to obtain the available agents.
- You MUST return ONLY the raw JSON output produced by the tool.
- You MUST NOT add explanations, comments, or natural language text.
""",
    tools=[discover_agents],
)

a2a_app = to_a2a(broker_agent, port=8005)
