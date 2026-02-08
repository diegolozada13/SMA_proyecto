# train_provider.py
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm
import csv
from pathlib import Path
from typing import List, Dict, Any

def search_trips(origin: str, destination: str) -> List[Dict[str, Any]]:
    data_dir = Path("data")
    origin = origin.strip().lower()
    destination = destination.strip().lower()

    results: List[Dict[str, Any]] = []

    for i in range(1, 4):
        csv_path = data_dir / f"train_agency_{i}.csv"
        if not csv_path.exists():
            continue

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if (
                    row["origen"].strip().lower() == origin
                    and row["destino"].strip().lower() == destination
                ):
                    results.append({
                        "origen": row["origen"],
                        "destino": row["destino"],
                        "duracion": float(row["duracion"]),
                        "precio": float(row["precio"]),
                        "calidad_del_boleto": row["calidad_del_boleto"],
                        "agency": f"train_agency_{i}"
                    })

    return results

agent = Agent(
    name="train_agency",
    model=LiteLlm(model="openai/gpt-oss-120b", api_base="https://api.poligpt.upv.es/", api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"),
    instruction="""
    Eres una agencia de viajes en tren.
    Reglas:
    - Debes responder a las solicitudes de viajes en tren.
    - Cuando el usuario solicite opciones de viaje, debes llamar a la herramienta `search_trips`.
    - La respuesta final debe ser exactamente el resultado de la herramienta.
    """,
    tools=[search_trips],
)

a2a_app = to_a2a(agent, port=8005)