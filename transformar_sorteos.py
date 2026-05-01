import pandas as pd
import requests
import json
import os
import io
import time
from datetime import datetime

SORTEOS = {
    "melate": "https://www.loterianacional.gob.mx/Home/HistoricosCSV?ARHP=TQBlAGwAYQB0AGUALQBSAGUAdAByAG8A",
    "chispazo": "https://www.loterianacional.gob.mx/Home/HistoricosCSV?ARHP=QwBoAGkAcwBwAGEAegBvAA=="
}

def procesar():
    if not os.path.exists('data'):
        os.makedirs('data')

    # Configuración de cabeceras para parecer un humano real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-MX,es;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    }

    session = requests.Session()

    for nombre, url in SORTEOS.items():
        try:
            print(f"--- Intentando descargar {nombre} ---")
            
            # PASO 1: Visitar la página de inicio para obtener cookies de sesión
            print("Paso 1: Obteniendo cookies de sesión...")
            session.get("https://www.loterianacional.gob.mx/Home/Historicos", headers=headers, timeout=20)
            time.sleep(2) # Pausa para no parecer bot

            # PASO 2: Intentar la descarga con las cookies obtenidas
            print("Paso 2: Descargando archivo CSV...")
            # Actualizamos el referer dinámicamente
            headers['Referer'] = "https://www.loterianacional.gob.mx/Home/Historicos"
            response = session.get(url, headers=headers, timeout=30)
            
            content = response.text

            if "<html" in content.lower() or response.status_code != 200:
                print(f"❌ Seguimos bloqueados. El servidor respondió con HTML o error {response.status_code}")
                # Imprimimos un poco más para ver si hay algún mensaje de error útil
                continue

            # PASO 3: Procesamiento (si logramos pasar el muro)
            df = pd.read_csv(io.StringIO(content))
            df.columns = [c.strip().upper() for c in df.columns]
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True).dt.strftime('%Y-%m-%d')
            df = df.sort_values(by='CONCURSO', ascending=False)

            filename = f"data/resultados_{nombre}.json"
            cols = ['CONCURSO', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'FECHA'] if nombre == "melate" else ['CONCURSO', 'R1', 'R2', 'R3', 'R4', 'R5', 'FECHA']
            cols_existentes = [c for c in cols if c in df.columns]
            df = df[cols_existentes]

            resultado = {
                "sorteo": nombre.upper(),
                "ultima_actualizacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "datos": df.to_dict(orient='records')
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)

            print(f"✅ ÉXITO: {filename} generado.")

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

if __name__ == "__main__":
    procesar()
