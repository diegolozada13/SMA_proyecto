from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm
import requests
import uuid

SUB_AGENCIES = [
    {"name": "flight_agency_1", "url": "http://localhost:8014"},
    {"name": "flight_agency_2", "url": "http://localhost:8015"},
    {"name": "flight_agency_3", "url": "http://localhost:8016"},
]

def query_all_sub_agencies(user_request: str):
    """
    Consulta a todas las agencias secundarias disponibles enviando la petición del usuario.
    Retorna una lista de opciones encontradas por las agencias.

    Args:
        user_request: La solicitud de viaje original del usuario (ej. "Vuelo de Madrid a París").
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

flight_provider = Agent(
    name="flight_provider",
    model=LiteLlm(model="openai/gpt-oss-120b", api_base="https://api.poligpt.upv.es/", api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"),
    instruction="""
    Actúas como un Bróker Secundario especializado en Vuelos.
    1. Usa la herramienta `query_all_sub_agencies` para consultar a todas las agencias de vuelos disponibles.
    2. Recibirás varias opciones de vuelos de distintas agencias.
    3. Analiza los datos (precios, horarios, escalas).
    4. Selecciona la MEJOR opción para el usuario basándote en su solicitud original.
    5. Devuelve solo la mejor opción detallada.
    """,

    tools=[query_all_sub_agencies],
)

a2a_app = to_a2a(flight_provider, port=8013)