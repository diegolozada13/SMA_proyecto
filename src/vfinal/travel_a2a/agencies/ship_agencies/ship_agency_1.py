# ship_provider.py
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm
import csv
from pathlib import Path
from typing import List, Dict, Any

def search_trips(origin: str, destination: str, date: str | None, quality: str | None) -> List[Dict[str, Any]]:
    """
    Busca viajes en barco desde un origen a un destino en una fecha y calidad determinadas.
    
    Args:
        origin: Origen del viaje.
        destination: Destino del viaje.
        date: Fecha del viaje.
        quality: Calidad del boleto.
    
    Calidad del boleto y fecha del viaje no son requeridos, en caso de no tener esta informacion buscar el viaje mas barato que cumpla con el origen y destino.
    Returns:
        Lista de viajes encontrados.
    """
    print(f"TOOL CALLED: search_trips(origin={origin}, destination={destination}, date={date}, quality={quality})", flush=True)
    data_dir = Path(__file__).resolve().parents[4] / "data"
    print(f"Searching trips from {origin} to {destination} in ship agencies... {data_dir}")
    origin = origin.strip().lower()
    destination = destination.strip().lower()
    date = date.strip().lower() if date else None
    quality = quality.strip().lower() if quality else None
    results: List[Dict[str, Any]] = []

    csv_path = data_dir / "ship_agency_1.csv"
    if not csv_path.exists():
        return results

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if (
                row["origen"].strip().lower() == origin
                and row["destino"].strip().lower() == destination
                and row["fecha"].strip().lower() == date if date else True
                and row["calidad_del_boleto"].strip().lower() == quality if quality else True
                ):
                    results.append({
                        "origen": row["origen"],
                        "destino": row["destino"],
                        "duracion": float(row["duracion"]),
                        "precio": float(row["precio"]),
                        "calidad_del_boleto": row["calidad_del_boleto"],
                        "agency": "ship_agency_1"
                    })        

    return results

agent = Agent(
    name="ship_agency",
    model=LiteLlm(model="openai/gpt-oss-120b", api_base="https://api.poligpt.upv.es/", api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"),
    instruction="""
    Eres una agencia de viajes en barcos.
    Reglas:
    - Debes responder a las solicitudes de viajes en barco.
    - Cuando el usuario solicite opciones de viaje, debes llamar a la herramienta `search_trips`.
    - Solo puedes llamar a la herramienta `search_trips`, no puedes hacer uso de otra cosa.
    - La respuesta final debe ser exactamente el resultado de la herramienta.
    """,
    tools=[search_trips],
)

a2a_app = to_a2a(agent, port=8024)