import pandas as pd
import numpy as np
import os

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
DAY_TOTALS = [302, 299, 312, 300, 361, 365]
WEEKS = [f"week{i}" for i in range(1, 53)]

PEAK_WEEKS = {
    "Feb": list(range(6, 10)),
    "Jul": list(range(27, 31)),
    "Dec": list(range(49, 53))
}


def linear_regression(series, variation=0.15):
    x = np.arange(1, len(series) + 1)
    m, b = np.polyfit(x, series, 1)
    pred = m * x + b
    noise = np.random.uniform(1 - variation, 1 + variation, len(pred))
    return np.maximum(0, np.round(pred * noise).astype(int))

def add_peak(values):
    for peak_weeks in PEAK_WEEKS.values():
        week = np.random.choice(peak_weeks)
        day_idx = np.random.randint(0, len(DAYS))
        values[day_idx][week - 1] = min(18, values[day_idx][week - 1] + np.random.randint(3, 6))
    return values


def generate_2025():
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame({"day": DAYS})
    base_values = []

    for day_idx, day in enumerate(DAYS):
        base = []
        total_day = DAY_TOTALS[day_idx]

        weights = np.random.rand(47)
        weights /= weights.sum()
        weeks_1_to_47 = np.round(weights * total_day).astype(int)
        base.extend(weeks_1_to_47)

        x = np.arange(1, len(base) + 1)
        m, b = np.polyfit(x, base, 1)
        for week in range(48, 53):
            value = int(np.round((m * week + b) * np.random.uniform(0.9, 1.1)))
            base.append(max(0, value))

        base_values.append(base)

    base_values = add_peak(base_values)

    for day_idx, day in enumerate(DAYS):
        for i, week_name in enumerate(WEEKS):
            df.loc[df["day"] == day, week_name] = base_values[day_idx][i]

    df[WEEKS] = df[WEEKS].astype(int)
    df["total_day"] = df[WEEKS].sum(axis=1).astype(int)

    total_week_values = df[WEEKS].sum().astype(int)
    total_week = total_week_values.to_dict()
    total_week["day"] = "total_week"
    total_week["total_day"] = sum(total_week_values)
    df = pd.concat([df, pd.DataFrame([total_week])], ignore_index=True)

    df.to_csv("data/table_2025.csv", index=False)
    print("Generated: data/table_2025.csv")
    return df


def add_peak_2026(values):
    for peak_list in PEAK_WEEKS.values():
        for w in peak_list:
            for day_idx in range(2, 6):
                values[day_idx][w - 1] = min(
                    18,
                    values[day_idx][w - 1] + np.random.randint(3, 7)
                )
    return values


def generate_2026(base_2025):
    df = pd.DataFrame({"day": DAYS})
    base_values = []

    day_multipliers = {
        0: 0.80,  
        1: 0.85,  
        2: 1.20,  
        3: 1.25,  
        4: 1.35,  
        5: 1.40   
    }

    for day_idx, day in enumerate(DAYS):
        base = base_2025.loc[base_2025["day"] == day, WEEKS].values.flatten()

        x = np.arange(1, 53)
        m, b = np.polyfit(x, base, 1)

        series_2026 = []
        for week in range(1, 53):
            value = m * week + b

            daily_factor = np.random.uniform(0.8, 1.25)

            value *= day_multipliers[day_idx]

            value = int(np.round(value * daily_factor))
            value = np.clip(value, 6, 18)

            series_2026.append(value)

        base_values.append(series_2026)

    base_values = add_peak_2026(base_values)

    for day_idx, day in enumerate(DAYS):
        for i, week_name in enumerate(WEEKS):
            df.loc[df["day"] == day, week_name] = base_values[day_idx][i]

    df[WEEKS] = df[WEEKS].astype(int)
    df["total_day"] = df[WEEKS].sum(axis=1).astype(int)

    total_week_values = df[WEEKS].sum().astype(int)
    total_week = total_week_values.to_dict()
    total_week["day"] = "total_week"
    total_week["total_day"] = sum(total_week_values)
    df = pd.concat([df, pd.DataFrame([total_week])], ignore_index=True)

    df.to_csv("data/table_2026.csv", index=False)
    print("Generated: data/table_2026.csv")
    return df

base_2025 = generate_2025()
generate_2026(base_2025)
