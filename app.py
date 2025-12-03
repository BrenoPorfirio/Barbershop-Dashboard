import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="💈 Dashboard da Barbearia", layout="wide")
st.title("💈 Dashboard da Barbearia – Série Temporal e Finanças")

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
DAYS_FULL = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]

months = {
    "Janeiro": range(1, 5),
    "Fevereiro": range(5, 9),
    "Março": range(9, 14),
    "Abril": range(14, 18),
    "Maio": range(18, 23),
    "Junho": range(23, 27),
    "Julho": range(27, 31),
    "Agosto": range(31, 36),
    "Setembro": range(36, 40),
    "Outubro": range(40, 45),
    "Novembro": range(45, 49),
    "Dezembro": range(49, 53)
}

np.random.seed(42)

@st.cache_data
def load_data():
    df_2025 = pd.read_csv("data/table_2025.csv")
    df_2026 = pd.read_csv("data/table_2026.csv")
    return df_2025, df_2026

df2025, df2026 = load_data()

def clean_df(df):
    df_clean = df.copy()
    df_clean["day"] = df_clean["day"].map(dict(zip(DAYS, DAYS_FULL)))
    weeks_cols = [c for c in df_clean.columns if c.startswith("week") and int(c.replace("week","")) > 0]
    return df_clean, weeks_cols

clean2025, weeks2025 = clean_df(df2025)
clean2026, weeks2026 = clean_df(df2026)

def compute_statistics(df, weeks_cols, df_fin):
    max_single_value = df[weeks_cols].max().max()
    best_single_day = df.loc[df[weeks_cols].eq(max_single_value).any(axis=1), "day"].values[0]

    total_per_day = df[weeks_cols].sum(axis=1)
    best_total_day = df.loc[total_per_day.idxmax(), "day"]
    best_total_value = total_per_day.max()

    total_per_week = df[weeks_cols].sum()
    best_week = total_per_week.idxmax()
    best_week_value = total_per_week.max()

    best_profit_month = df_fin.loc[df_fin["Lucro"].idxmax(), "Mês"]
    best_profit_value = df_fin["Lucro"].max()

    highest_cost_month = df_fin.loc[df_fin["Custos"].idxmax(), "Mês"]
    highest_cost_value = df_fin["Custos"].max()

    best_week_translated = "Semana " + best_week.replace("week", "")

    return {
        "best_week": (best_week_translated, best_week_value),
        "best_single_day": (best_single_day, max_single_value),
        "best_total_day": (best_total_day, best_total_value),
        "best_profit": (best_profit_month, best_profit_value),
        "highest_cost": (highest_cost_month, highest_cost_value)
    }

def compute_financials(df, year):
    monthly_totals, costs, profits = {}, {}, {}
    monthly_noise_pct = np.random.uniform(0.05, 0.20, size=12) if year == 2026 else np.zeros(12)

    for idx, (month, week_range) in enumerate(months.items()):
        cols = [f"week{i}" for i in week_range if f"week{i}" in df.columns and i > 0]
        total_services = df[cols].sum().sum()
        monthly_totals[month] = total_services

        if year == 2025:
            if month in ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho"]:
                monthly_profit = total_services * (30 * 0.25)
            else:
                monthly_profit = total_services * 35
        else:
            monthly_profit = total_services * 35

        if year == 2025:
            if month in ["Janeiro","Fevereiro","Março","Abril","Maio","Junho"]:
                base_cost = 0
            elif month in ["Julho","Agosto","Setembro"]:
                base_cost = 400
            elif month == "Outubro":
                base_cost = 1000
            elif month == "Novembro":
                base_cost = 4400
            else:
                base_cost = 1000
        else:
            base_cost = 1000

        final_cost = round(base_cost * (1 + monthly_noise_pct[idx]), 2)
        costs[month] = final_cost
        profits[month] = round(monthly_profit, 2)

    return pd.DataFrame({
        "Mês": list(monthly_totals.keys()),
        "Atendimentos": list(monthly_totals.values()),
        "Custos": [costs[m] for m in monthly_totals.keys()],
        "Lucro": [profits[m] for m in monthly_totals.keys()]
    })

df_fin_2025 = compute_financials(clean2025, 2025)
df_fin_2026 = compute_financials(clean2026, 2026)

stats2025 = compute_statistics(clean2025, weeks2025, df_fin_2025)
stats2026 = compute_statistics(clean2026, weeks2026, df_fin_2026)

st.header("📊 Métricas Relevantes 2025 e Previsão 2026")
def display_cards(stats, year):
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(f"📅 Semana mais atendida {year}", stats['best_week'][0], f"{stats['best_week'][1]} atendimentos")
    col2.metric(f"🗓️ Dia mais atendido individual {year}", stats['best_single_day'][0], f"{stats['best_single_day'][1]} atendimentos")
    col3.metric(f"🗓️ Dia da semana mais atendido total {year}", stats['best_total_day'][0], f"{stats['best_total_day'][1]} atendimentos")
    col4.metric(f"💰 Maior lucro {year}", stats['best_profit'][0], f"R$ {stats['best_profit'][1]:,.2f}")
    cost_value = stats['highest_cost'][1]
    col5.metric(f"💸 Maior custo {year}",
                value=f"R$ {cost_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                delta=f"-R$ {abs(cost_value):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                delta_color="normal")

display_cards(stats2025, 2025)
st.markdown("---")
display_cards(stats2026, "Previsão 2026")

st.header("📌 Custos e Lucros Mensais")
col1, col2 = st.columns(2)
col1.plotly_chart(px.bar(df_fin_2025, x="Mês", y="Custos", title="Custos 2025", template="plotly_white"), use_container_width=True)
col2.plotly_chart(px.bar(df_fin_2026, x="Mês", y="Custos", title="Custos previstos 2026", template="plotly_white"), use_container_width=True)
col3, col4 = st.columns(2)
col3.plotly_chart(px.bar(df_fin_2025, x="Mês", y="Lucro", title="Lucros 2025", template="plotly_white"), use_container_width=True)
col4.plotly_chart(px.bar(df_fin_2026, x="Mês", y="Lucro", title="Lucros previstos 2026", template="plotly_white"), use_container_width=True)

st.header("📊 Comparativo Mensal 2025 vs 2026")
df_comparison = pd.DataFrame({
    "Mês": df_fin_2025["Mês"],
    "Atendimentos 2025": df_fin_2025["Atendimentos"],
    "Atendimentos 2026": df_fin_2026["Atendimentos"],
    "Lucro 2025": df_fin_2025["Lucro"],
    "Lucro 2026": df_fin_2026["Lucro"]
})
st.plotly_chart(px.line(df_comparison, x="Mês", y=["Atendimentos 2025","Atendimentos 2026"], markers=True, title="Atendimentos Mensais 2025 vs 2026", template="plotly_white"), use_container_width=True)
st.plotly_chart(px.line(df_comparison, x="Mês", y=["Lucro 2025","Lucro 2026"], markers=True, title="Lucro Mensal 2025 vs 2026", template="plotly_white"), use_container_width=True)

st.header("🔥 Mapa de Calor Semanal 2025")
st.plotly_chart(px.imshow(clean2025[weeks2025].values, x=[f"Semana {i}" for i in range(1,len(weeks2025)+1)], y=DAYS_FULL, color_continuous_scale="OrRd", labels=dict(x="Semana", y="Dia")), use_container_width=True)
st.header("🔥 Mapa de Calor Semanal 2026")
st.plotly_chart(px.imshow(clean2026[weeks2026].values, x=[f"Semana {i}" for i in range(1,len(weeks2026)+1)], y=DAYS_FULL, color_continuous_scale="OrRd", labels=dict(x="Semana", y="Dia")), use_container_width=True)

x_weeks = [int(c.replace("week","")) for c in weeks2026]
y_days = {day: clean2026.loc[clean2026["day"]==day, weeks2026].values.flatten() for day in DAYS_FULL}

x_weeks_2025 = [int(c.replace("week","")) for c in weeks2025]
y_days_2025 = {day: clean2025.loc[clean2025["day"]==day, weeks2025].values.flatten() for day in DAYS_FULL}

st.header("📅 Evolução Semanal por Dia da Semana – 2025")
fig_weekly_2025 = go.Figure()
for day, y in y_days_2025.items():
    fig_weekly_2025.add_trace(go.Scatter(x=x_weeks_2025, y=y, mode="lines+markers", name=day))

st.plotly_chart(fig_weekly_2025, use_container_width=True)


st.header("📅 Evolução Semanal por Dia da Semana – 2026")
fig_weekly = go.Figure()
for day, y in y_days.items():
    fig_weekly.add_trace(go.Scatter(x=x_weeks, y=y, mode="lines+markers", name=day))
st.plotly_chart(fig_weekly, use_container_width=True)

weekly_2025 = clean2025[weeks2025].sum()
weekly_2026 = clean2026[weeks2026].sum()
fig_compare = go.Figure()
fig_compare.add_trace(go.Scatter(x=x_weeks, y=weekly_2025.cumsum(), mode="lines", name="2025 Acumulado"))
fig_compare.add_trace(go.Scatter(x=x_weeks, y=weekly_2026.cumsum(), mode="lines", name="2026 Acumulado"))
