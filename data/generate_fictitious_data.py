import pandas as pd
import numpy as np
import os
from statsmodels.tsa.arima.model import ARIMA

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
WEEKS = [f"week{i}" for i in range(1, 53)]

def generate_2025_from_csv(csv_path="data/table_2025.csv"):
    if not os.path.exists(csv_path):
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

        series_log = np.log1p(series_2025)

        try:
            model = ARIMA(series_log, order=(1,1,1))
            arima_fit = model.fit()
            forecast_log = arima_fit.forecast(len(series_2025))
        except:
            forecast_log = series_log.copy()

        forecast_2026 = np.expm1(forecast_log)

        noise = np.random.randint(-1, 2, size=len(series_2025))
        final_forecast = forecast_2026 + noise

        peak_weeks = {
            "Feb": range(4, 8),
            "Jul": range(26, 30),
            "Dec": range(48, 52)
        }

        for weeks in peak_weeks.values():
            final_forecast[weeks] = final_forecast[weeks] * np.random.uniform(1.1, 1.25, size=len(weeks))

        final_forecast = final_forecast.round().astype(int)

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
    base_2025 = generate_2025_from_csv("data/table_2025.csv")
    df_2026 = generate_2026_realistic_series(base_2025)
    print("\nArquivo gerado com sucesso: data/table_2026.csv")
    print(df_2026)
