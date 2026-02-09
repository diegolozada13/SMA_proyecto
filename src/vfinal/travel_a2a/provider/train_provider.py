from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm
import requests
import uuid

SUB_AGENCIES = [
    {"name": "train_agency_1", "url": "http://localhost:8034"},
    {"name": "train_agency_2", "url": "http://localhost:8035"},
    {"name": "train_agency_3", "url": "http://localhost:8036"},
]

def query_all_sub_agencies(user_request: str):
    """
    Consulta a todas las agencias secundarias disponibles enviando la petición del usuario.
    Retorna una lista de opciones encontradas por las agencias.

    Args:
        user_request: La solicitud de viaje original del usuario (ej. "Tren de Madrid a París").
    """
    results = []
    for agency in SUB_AGENCIES:
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "message/send",
                "params": {
                    "conversationId": str(uuid.uuid4()),
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": user_request}]
                    }
                }
            }
            resp = requests.post(f"{agency['url']}/api/v1/message", json=payload, timeout=10).json()
            content = resp.get("result", {}).get("artifacts", [{}])[0].get("parts", [{}])[0].get("text", "")
            results.append(f"Agencia {agency['name']}: {content}")
        except Exception as e:
            results.append(f"Error en {agency['name']}: {str(e)}")
    return results

train_provider = Agent(
    name="train_provider",
    model=LiteLlm(model="openai/gpt-oss-120b", api_base="https://api.poligpt.upv.es/", api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"),
    instruction="""
    Eres un orquestador de agencias de trenes. TU ÚNICO PROPÓSITO es consultar a las agencias externas.
    
    REGLAS OBLIGATORIAS:
    1. NO inventes información ni precios.
    2. DEBES llamar SIEMPRE a la herramienta `query_all_sub_agencies` con la solicitud del usuario.
    3. Si la herramienta devuelve una lista vacía o error, dilo explícitamente.
    4. Tu respuesta final debe basarse EXCLUSIVAMENTE en el retorno de la herramienta.
    5. Si el mensaje con la informacion del usuario no tiene fecha ni calidad del viaje entendemos que da igual ambos datos busca para todas las calidades y todas las fechas en el año actual.
    """,

    tools=[query_all_sub_agencies],
)

a2a_app = to_a2a(train_provider, port=8033)