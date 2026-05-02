import pandas as pd
import json
import os
from datetime import datetime

def procesar():
    INPUT_DIR = 'raw_csv'
    OUTPUT_DIR = 'docs'
    
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
            print(f"Procesando {nombre} con nueva estructura...")
            
            try:
                df = pd.read_csv(csv_path, encoding='utf-8')
            except:
                df = pd.read_csv(csv_path, encoding='latin-1')

            # Limpiar nombres de columnas
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Formatear fecha
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True).dt.strftime('%Y-%m-%d')
            df = df.sort_values(by='CONCURSO', ascending=False)

            json_final = []

            for _, row in df.iterrows():
                if nombre == "melate":
                    # Estructura Melate Retro: 6 números + 1 adicional
                    item = {
                        "idConcurso": int(row['CONCURSO']),
                        "fecha": row['FECHA'],
                        "numeros": [int(row['F1']), int(row['F2']), int(row['F3']), 
                                    int(row['F4']), int(row['F5']), int(row['F6'])],
                        "adicional": int(row['F7'])
                    }
                else:
                    # Estructura Chispazo: 5 números
                    item = {
                        "idConcurso": int(row['CONCURSO']),
                        "fecha": row['FECHA'],
                        "numeros": [int(row['R1']), int(row['R2']), int(row['R3']), 
                                    int(row['R4']), int(row['R5'])]
                    }
                json_final.append(item)

            # Guardar el archivo directamente como una lista [ {...}, {...} ]
            filename = f"{OUTPUT_DIR}/resultados_{nombre}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_final, f, ensure_ascii=False, indent=2)

            print(f"✅ Generado: {filename} con {len(json_final)} registros.")

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

if __name__ == "__main__":
    procesar()
