import pandas as pd
import json
import os
from datetime import datetime

def procesar():
    # Nueva ruta de salida para GitHub Pages
    INPUT_DIR = 'raw_csv'
    OUTPUT_DIR = 'docs'
    
    # Crea la carpeta docs si no existe
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    archivos = {
        "melate": "Melate-Retro.csv",
        "chispazo": "Chispazo.csv"
    }

    for nombre, archivo_csv in archivos.items():
        csv_path = os.path.join(INPUT_DIR, archivo_csv)
        
        if not os.path.exists(csv_path):
            print(f"⚠️ Saltando {nombre}: No se encontró el archivo en {csv_path}")
            continue

        try:
            print(f"Procesando {nombre} desde {csv_path}...")
            
            # Intentar leer con diferentes codificaciones
            try:
                df = pd.read_csv(csv_path, encoding='utf-8')
            except:
                df = pd.read_csv(csv_path, encoding='latin-1')

            # Limpiar nombres de columnas
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Formatear fecha para la App
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True).dt.strftime('%Y-%m-%d')
            df = df.sort_values(by='CONCURSO', ascending=False)

            filename = f"{OUTPUT_DIR}/resultados_{nombre}.json"
            
            if nombre == "melate":
                cols = ['CONCURSO', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'FECHA']
            else:
                cols = ['CONCURSO', 'R1', 'R2', 'R3', 'R4', 'R5', 'FECHA']
            
            cols_finales = [c for c in cols if c in df.columns]
            df = df[cols_finales]

            resultado = {
                "sorteo": nombre.upper(),
                "ultima_actualizacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "datos": df.to_dict(orient='records')
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)

            print(f"✅ Archivo generado en: {filename}")

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

if __name__ == "__main__":
    procesar()
