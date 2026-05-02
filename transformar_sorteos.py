import pandas as pd
import json
import os

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
            print(f"⚠️ Saltando {nombre}: No se encontró {csv_path}")
            continue

        try:
            # Leer el CSV original
            df = pd.read_csv(csv_path, encoding='latin-1')
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Ordenar por concurso de mayor a menor
            df = df.sort_values(by='CONCURSO', ascending=False)

            json_final = []

            for _, row in df.iterrows():
                # Convertir fecha de DD/MM/YYYY a YYYY-MM-DD
                raw_date = str(row['FECHA'])
                date_obj = pd.to_datetime(raw_date, dayfirst=True)
                fecha_formateada = date_obj.strftime('%Y-%m-%d')
                
                if nombre == "melate":
                    # Estructura exacta Melate Retro
                    item = {
                        "idConcurso": int(row['CONCURSO']),
                        "fecha": fecha_formateada,
                        "numeros": [int(row['F1']), int(row['F2']), int(row['F3']), 
                                    int(row['F4']), int(row['F5']), int(row['F6'])],
                        "adicional": int(row['F7'])
                    }
                else:
                    # Estructura exacta Chispazo
                    item = {
                        "idConcurso": int(row['CONCURSO']),
                        "fecha": fecha_formateada,
                        "numeros": [int(row['R1']), int(row['R2']), int(row['R3']), 
                                    int(row['R4']), int(row['R5'])]
                    }
                json_final.append(item)

            # GUARDAR COMO LISTA PURA [ { ... }, { ... } ]
            filename = f"{OUTPUT_DIR}/resultados_{nombre}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                # Al pasar la lista directamente, el archivo empieza con [
                json.dump(json_final, f, ensure_ascii=False, indent=2)

            print(f"✅ Generado correctamente: {filename}")

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

if __name__ == "__main__":
    procesar()
