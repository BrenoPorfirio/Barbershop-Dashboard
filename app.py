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
WEEKS = [f"week{i}" for i in range(1, 53)]

months = {
    "Janeiro": range(1, 5), "Fevereiro": range(5, 9), "Março": range(9, 13),
    "Abril": range(13, 17), "Maio": range(17, 21), "Junho": range(21, 25),
    "Julho": range(25, 29), "Agosto": range(29, 33), "Setembro": range(33, 37),
    "Outubro": range(37, 41), "Novembro": range(41, 45), "Dezembro": range(45, 53)
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
    weeks_cols = df_clean.drop(columns=["day", "total"]).columns
    return df_clean, weeks_cols

clean2025, weeks2025 = clean_df(df2025)
clean2026, weeks2026 = clean_df(df2026)

def compute_statistics(df, df_fin):
    max_single_value = df[WEEKS].max().max()
    best_single_day = df.loc[df[WEEKS].eq(max_single_value).any(axis=1), "day"].values[0]

    total_per_day = df[WEEKS].sum(axis=1)
    best_total_day = df.loc[total_per_day.idxmax(), "day"]
    best_total_value = total_per_day.max()

    total_per_week = df[WEEKS].sum()
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
    water_per_service = 10
    energy_per_service = 0.5
    monthly_totals, costs, profits = {}, {}, {}

    for month, week_range in months.items():
        cols = [f"week{i}" for i in week_range if f"week{i}" in df.columns]
        total_services = df[cols].sum().sum()
        monthly_totals[month] = total_services

        base_cost = total_services * water_per_service * 0.13 + total_services * energy_per_service * 1.0
        monthly_profit = total_services * 35

        if year == 2025:
            if month in ["Janeiro", "Fevereiro", "Março", "Abril", "Maio"]:
                monthly_profit = total_services * 30 * 0.25
            else:
                monthly_profit = total_services * 35
                if month == "Novembro":
                    base_cost += 3400
        costs[month] = base_cost
        profits[month] = monthly_profit

    return pd.DataFrame({
        "Mês": list(monthly_totals.keys()),
        "Atendimentos": list(monthly_totals.values()),
        "Custos": [costs[m] for m in monthly_totals.keys()],
        "Lucro": [profits[m] for m in monthly_totals.keys()]
    })

df_fin_2025 = compute_financials(clean2025, 2025)
df_fin_2026 = compute_financials(clean2026, 2026)

stats2025 = compute_statistics(clean2025, df_fin_2025)
stats2026 = compute_statistics(clean2026, df_fin_2026)

st.header("📊 KPIs Relevantes 2025 e Previsão 2026")
def display_cards(stats, year):
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(f"📅 Semana mais atendida {year}", stats['best_week'][0], f"{stats['best_week'][1]} atendimentos")
    col2.metric(f"🗓️ Dia mais atendido individual {year}", stats['best_single_day'][0], f"{stats['best_single_day'][1]} atendimentos")
    col3.metric(f"🗓️ Dia da semana mais atendido total {year}", stats['best_total_day'][0], f"{stats['best_total_day'][1]} atendimentos")
    col4.metric(f"💰 Maior lucro {year}", stats['best_profit'][0], f"R$ {stats['best_profit'][1]:,.2f}")
    col5.metric(f"💸 Maior custo {year}", stats['highest_cost'][0], f"R$ {stats['highest_cost'][1]:,.2f}", delta_color="inverse")

display_cards(stats2025, 2025)
st.markdown("---")
display_cards(stats2026, "Previsão 2026")

st.header("📌 Custos e Lucros Mensais")
col1, col2 = st.columns(2)
fig_cost_2025 = px.bar(df_fin_2025, x="Mês", y="Custos", title="Custos 2025", template="plotly_white")
fig_cost_2026 = px.bar(df_fin_2026, x="Mês", y="Custos", title="Custos previstos 2026", template="plotly_white")
col1.plotly_chart(fig_cost_2025, use_container_width=True)
col2.plotly_chart(fig_cost_2026, use_container_width=True)

col3, col4 = st.columns(2)
fig_profit_2025 = px.bar(df_fin_2025, x="Mês", y="Lucro", title="Lucros 2025", template="plotly_white")
fig_profit_2026 = px.bar(df_fin_2026, x="Mês", y="Lucro", title="Lucros previstos 2026", template="plotly_white")
col3.plotly_chart(fig_profit_2025, use_container_width=True)
col4.plotly_chart(fig_profit_2026, use_container_width=True)

st.header("📊 Comparativo Mensal 2025 vs 2026")
df_comparison = pd.DataFrame({
    "Mês": df_fin_2025["Mês"],
    "Atendimentos 2025": df_fin_2025["Atendimentos"],
    "Atendimentos 2026": df_fin_2026["Atendimentos"],
    "Lucro 2025": df_fin_2025["Lucro"],
    "Lucro 2026": df_fin_2026["Lucro"]
})

fig_services = px.line(df_comparison, x="Mês", y=["Atendimentos 2025", "Atendimentos 2026"],
                       title="Atendimentos Mensais 2025 vs Previsão 2026", markers=True, template="plotly_white")
st.plotly_chart(fig_services, use_container_width=True)

fig_profit = px.line(df_comparison, x="Mês", y=["Lucro 2025", "Lucro 2026"],
                     title="Lucro Mensal 2025 vs Previsão 2026", markers=True, template="plotly_white")
st.plotly_chart(fig_profit, use_container_width=True)

st.header("🔥 Mapa de Calor Semanal 2025")
fig_heat_2025 = px.imshow(clean2025[WEEKS].values,
                          x=[f"Semana {i}" for i in range(1,53)],
                          y=DAYS_FULL,
                          color_continuous_scale="OrRd",
                          labels=dict(x="Semana", y="Dia"))
st.plotly_chart(fig_heat_2025, use_container_width=True)

st.header("🔥 Mapa de Calor Semanal 2026")
fig_heat_2026 = px.imshow(clean2026[WEEKS].values,
                          x=[f"Semana {i}" for i in range(1,53)],
                          y=DAYS_FULL,
                          color_continuous_scale="OrRd",
                          labels=dict(x="Semana", y="Dia"))
st.plotly_chart(fig_heat_2026, use_container_width=True)

st.header("📅 Evolução Semanal por Dia da Semana – 2026")
fig_weekly = go.Figure()
for i, day in enumerate(DAYS_FULL):
    fig_weekly.add_trace(go.Scatter(y=clean2026.loc[clean2026["day"]==day, WEEKS].values.flatten(),
                                    mode="lines+markers", name=day))
fig_weekly.update_layout(title="Atendimentos Semanais 2026 por Dia da Semana",
                         xaxis_title="Semana", yaxis_title="Atendimentos")
st.plotly_chart(fig_weekly, use_container_width=True)

st.header("📊 Variabilidade Semanal 2026")
weekly_values = clean2026[WEEKS].values.flatten()
fig_box = px.box(pd.DataFrame(clean2026[WEEKS].T), title="Distribuição de Atendimentos Semanais 2026", labels={"variable":"Semana","value":"Atendimentos"})
st.plotly_chart(fig_box, use_container_width=True)

fig_hist = px.histogram(weekly_values, nbins=20, title="Histograma de Atendimentos Semanais 2026", labels={"value":"Atendimentos"})
st.plotly_chart(fig_hist, use_container_width=True)

st.header("📈 Tendência Acumulada 2026")
cum_values = clean2026[WEEKS].cumsum(axis=1)
fig_cum = go.Figure()
for i, day in enumerate(DAYS_FULL):
    fig_cum.add_trace(go.Scatter(y=cum_values.iloc[i], mode="lines+markers", name=day))
fig_cum.update_layout(title="Atendimentos Acumulados 2026", xaxis_title="Semana", yaxis_title="Atendimentos acumulados")
st.plotly_chart(fig_cum, use_container_width=True)

st.header("📊 Comparativo Semanal 2025 vs 2026")
weekly_2025 = clean2025[WEEKS].sum()
weekly_2026 = clean2026[WEEKS].sum()
fig_compare = go.Figure()
fig_compare.add_trace(go.Scatter(y=weekly_2025.values, mode="lines+markers", name="2025"))
fig_compare.add_trace(go.Scatter(y=weekly_2026.values, mode="lines+markers", name="2026"))
fig_compare.update_layout(title="Atendimentos Semana a Semana: 2025 vs 2026", xaxis_title="Semana", yaxis_title="Atendimentos")
st.plotly_chart(fig_compare, use_container_width=True)
