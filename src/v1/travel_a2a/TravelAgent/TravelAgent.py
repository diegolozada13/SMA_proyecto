import uvicorn
import csv
import os
import glob
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "Data"))

def search_all_csvs(query: str):
    """
    Busca el término 'query' en TODOS los archivos CSV dentro de la carpeta Data.
    Devuelve una lista combinada de resultados.
    """
    print("HOLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print(DATA_DIR)
    if not os.path.exists(DATA_DIR):
        return f"Error: No se encuentra el directorio de datos en: {DATA_DIR}"

    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    
    if not csv_files:
        return "Aviso: La carpeta Data existe pero no contiene archivos .csv"

    all_results = []
    files_scanned = 0

    for file_path in csv_files:
        try:
            filename = os.path.basename(file_path)
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                files_scanned += 1
                for row in reader:
                    row_content = " ".join([str(v) for v in row.values()]).lower()
                    
                    if query.lower() in row_content:
                        row['origen_dato'] = filename
                        all_results.append(row)
                        
        except Exception as e:
            print(f"Error leyendo {filename}: {e}")
            continue

    if not all_results:
        return f"Búsqueda completada en {files_scanned} archivos. No se encontraron coincidencias para: {query}"
    
    return str(all_results)

travel_agent = Agent(
    name="TravelAgent",
    model=LiteLlm(
        model="openai/gpt-oss-120b", 
        api_base="https://api.poligpt.upv.es/", 
        api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"
    ),
    instruction="""
    Eres un agente de viajes operativo. Tu trabajo es consultar la base de datos de viajes.
    
    TU FLUJO DE TRABAJO:
    1. Recibes una intención de usuario (ej: "Quiero ir a Japón" o "Busco hotel barato").
    2. Identificas la palabra clave más relevante.
    3. USAS la herramienta `search_all_csvs` para consultar todas las bases de datos disponibles.
    4. Con los resultados (que incluirán el campo 'origen_dato'), compón una respuesta amable con las opciones de viaje disponibles.
    5. SOLO puedes usar las herramientas disponibles en "tools". Ninguna busqueda externa esta aprobada
    
    """,
    tools=[search_all_csvs],
)

a2a_app = to_a2a(travel_agent, port=8002)