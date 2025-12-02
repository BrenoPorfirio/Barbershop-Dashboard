import pandas as pd
import numpy as np
import os

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
WEEKS = [f"week{i}" for i in range(1, 53)]

def generate_2025_from_csv(csv_path="data/table_2025.csv"):
    if not os.path.exists(csv_path):
        print(f"ERRO: Arquivo não encontrado em {csv_path}. Certifique-se de que table_2025.csv existe na pasta data/")
        raise FileNotFoundError(f"Arquivo base não encontrado: {csv_path}")

    df = pd.read_csv(csv_path)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    
    df[WEEKS] = df[WEEKS].replace('', 0).astype(float)
    
    if 'total' in df.columns:
        df.drop(columns=['total'], inplace=True)
        
    return df

def generate_2026_realistic_series(base_2025):
    
    data_rows = []
    
    for day in DAYS:
        series_2025 = base_2025.loc[base_2025.day == day, WEEKS].to_numpy().flatten().astype(float)
        forecast_2026 = series_2025.copy()
        
        for i in range(52):
            week_num = i + 1
            if 5 <= week_num <= 8 or 27 <= week_num <= 30 or 49 <= week_num <= 52:
                forecast_2026[i] *= 1.2
        
        noise = np.random.randint(-1, 2, size=52)
        
        final_forecast = np.clip(forecast_2026 + noise, 0, None).round().astype(int)
        
        row_data = {"day": day}
        
        for i, value in enumerate(final_forecast):
            row_data[WEEKS[i]] = value
            
        row_data["total"] = final_forecast.sum().astype(int)
        
        data_rows.append(row_data)

    df_2026 = pd.DataFrame(data_rows, columns=["day"] + WEEKS + ["total"])
    
    df_2026[WEEKS + ["total"]] = df_2026[WEEKS + ["total"]].astype(int)

    os.makedirs("data", exist_ok=True)
    df_2026.to_csv("data/table_2026.csv", index=False)

    return df_2026

if __name__ == "__main__":
    try:
        base_2025 = generate_2025_from_csv("data/table_2025.csv")
        
        df_2026 = generate_2026_realistic_series(base_2025)
        
        print("\nArquivo gerado com sucesso: data/table_2026.csv")
        print(df_2026)
        
    except FileNotFoundError as e:
        print(e)