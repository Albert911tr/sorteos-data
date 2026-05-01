import pandas as pd
import requests
import json
import os
from datetime import datetime

# URLs de descarga de la Lotería Nacional
SORTEOS = {
    "melate": "https://www.loterianacional.gob.mx/Home/HistoricosCSV?ARHP=TQBlAGwAYQB0AGUALQBSAGUAdAByAG8A",
    "chispazo": "https://www.loterianacional.gob.mx/Home/HistoricosCSV?ARHP=QwBoAGkAcwBwAGEAegBvAA=="
}

def procesar():
    # Creamos la carpeta data si no existe
    if not os.path.exists('data'):
        os.makedirs('data')

    for nombre, url in SORTEOS.items():
        try:
            print(f"Descargando {nombre}...")
            response = requests.get(url, timeout=30)
            csv_path = f"{nombre}_temp.csv"
            with open(csv_path, 'wb') as f:
                f.write(response.content)

            df = pd.read_csv(csv_path)
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True).dt.strftime('%Y-%m-%d')
            df = df.sort_values(by='CONCURSO', ascending=False)

            # Nombres de archivo finales dentro de /data
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

            print(f"✅ {filename} actualizado en /data.")
            os.remove(csv_path)

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

if __name__ == "__main__":
    procesar()
