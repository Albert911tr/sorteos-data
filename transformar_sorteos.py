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

    # Simulamos un navegador real con cabeceras completas
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/csv,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://www.loterianacional.gob.mx/Home/Historicos',
        'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
    }

    for nombre, url in SORTEOS.items():
        try:
            print(f"--- Iniciando descarga de {nombre} ---")
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=45)
            
            if response.status_code != 200:
                print(f"❌ Error de servidor ({nombre}): Código {response.status_code}")
                continue

            content = response.text
            
            # Verificación: ¿Es HTML en lugar de CSV?
            if "<html" in content.lower() or "<!doctype" in content.lower():
                print(f"⚠️ El sitio de la Lotería bloqueó el Bot y envió una página HTML.")
                print("Primeros 150 caracteres recibidos:")
                print(content[:150])
                continue

            # Intentar leer el CSV (el sitio a veces usa latin-1)
            try:
                df = pd.read_csv(io.StringIO(content))
            except:
                df = pd.read_csv(io.StringIO(content), encoding='latin-1')

            # --- Procesamiento de datos ---
            # Si el CSV viene con una columna extra al final o nombres raros, los limpiamos
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Convertir fecha
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True).dt.strftime('%Y-%m-%d')
            df = df.sort_values(by='CONCURSO', ascending=False)

            filename = f"data/resultados_{nombre}.json"
            
            if nombre == "melate":
                # Nota: Melate Retro usa F1...F7. 
                # Si el CSV de la web tiene nombres diferentes, Pandas los filtrará aquí.
                cols = ['CONCURSO', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'FECHA']
            else:
                cols = ['CONCURSO', 'R1', 'R2', 'R3', 'R4', 'R5', 'FECHA']
            
            # Filtrar solo columnas existentes para evitar errores
            cols_existentes = [c for c in cols if c in df.columns]
            df = df[cols_existentes]

            resultado = {
                "sorteo": nombre.upper(),
                "ultima_actualizacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "datos": df.to_dict(orient='records')
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)

            print(f"✅ {filename} actualizado con {len(df)} registros.")

        except Exception as e:
            print(f"❌ Error crítico en {nombre}: {e}")

if __name__ == "__main__":
    procesar()
