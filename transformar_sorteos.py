import pandas as pd
import requests
import json
import os
import io
from datetime import datetime

# URLs de descarga de la Lotería Nacional
SORTEOS = {
    "melate": "https://www.loterianacional.gob.mx/Home/HistoricosCSV?ARHP=TQBlAGwAYQB0AGUALQBSAGUAdAByAG8A",
    "chispazo": "https://www.loterianacional.gob.mx/Home/HistoricosCSV?ARHP=QwBoAGkAcwBwAGEAegBvAA=="
}

def procesar():
    if not os.path.exists('data'):
        os.makedirs('data')

    # Simulamos ser un navegador para que no nos bloqueen
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for nombre, url in SORTEOS.items():
        try:
            print(f"Descargando {nombre}...")
            response = requests.get(url, headers=headers, timeout=30)
            
            # Verificamos si la descarga fue exitosa
            if response.status_code != 200:
                print(f"❌ Error de servidor: Código {response.status_code}")
                continue

            # Usamos io.StringIO para leer el contenido directamente de la memoria
            # y especificamos el separador por si acaso
            df = pd.read_csv(io.StringIO(response.text))

            # Limpieza de datos
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True).dt.strftime('%Y-%m-%d')
            df = df.sort_values(by='CONCURSO', ascending=False)

            filename = "data/resultados_melate.json" if nombre == "melate" else "data/resultados_chispazo.json"
            
            if nombre == "melate":
                columnas = ['CONCURSO', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'FECHA']
            else:
                columnas = ['CONCURSO', 'R1', 'R2', 'R3', 'R4', 'R5', 'FECHA']
            
            df = df[columnas]

            resultado = {
                "sorteo": nombre.upper(),
                "ultima_actualizacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "datos": df.to_dict(orient='records')
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)

            print(f"✅ {filename} actualizado exitosamente.")

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

if __name__ == "__main__":
    procesar()
