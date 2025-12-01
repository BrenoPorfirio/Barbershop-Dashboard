import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="💈 Dashboard da Barbearia", layout="wide")
st.title("💈 Dashboard da Barbearia – Visão de Atendimentos e Finanças")

@st.cache_data
def load_data():
    df_2025 = pd.read_csv("data/table_2025.csv")
    df_2026 = pd.read_csv("data/table_2026.csv")
    return df_2025, df_2026

df2025, df2026 = load_data()

def clean_dataframe(df):
    df_clean = df[df["day"] != "total_week"].copy()
    weeks = df_clean.drop(columns=["day", "total_day"])
    return df_clean, weeks

DAYS_MAP = {
    "Mon": "Segunda-feira", "Tue": "Terça-feira", "Wed": "Quarta-feira",
    "Thu": "Quinta-feira", "Fri": "Sexta-feira", "Sat": "Sábado"
}

def translate_week(week_str):
    if "week" in week_str:
        return "Semana " + week_str.replace("week", "")
    return week_str

DAYS_FULL = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]

clean2025, weeks2025 = clean_dataframe(df2025)
clean2026, weeks2026 = clean_dataframe(df2026)

clean2025["day"] = clean2025["day"].map(DAYS_MAP)
clean2026["day"] = clean2026["day"].map(DAYS_MAP)

months = {
    "Janeiro": range(1, 5), "Fevereiro": range(5, 9), "Março": range(9, 13),
    "Abril": range(13, 17), "Maio": range(17, 21), "Junho": range(21, 25),
    "Julho": range(25, 29), "Agosto": range(29, 33), "Setembro": range(33, 37),
    "Outubro": range(37, 41), "Novembro": range(41, 45), "Dezembro": range(45, 53)
}

water_per_service = 10
energy_per_service = 0.5

def compute_financials(df, year):
    monthly_totals, costs, profits = {}, {}, {}

    for month, week_range in months.items():
        cols = [f"week{i}" for i in week_range if f"week{i}" in df.columns]
        total_services = df[cols].sum().sum()
        monthly_totals[month] = total_services

        base_cost = 0
        monthly_profit = 0

        if year == 2025:
            if month in ["Janeiro", "Fevereiro", "Março", "Abril", "Maio"]:
                monthly_profit = total_services * 30 * 0.25
            else:
                monthly_profit = total_services * 35
                base_cost = 1000

        elif year == 2026:
            monthly_profit = total_services * 35
            base_cost = 1000

        if (year == 2025 and month in ["Outubro", "Novembro", "Dezembro"]) or year == 2026:
            base_cost += total_services * water_per_service * 0.13
            base_cost += total_services * energy_per_service * 1.0

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

extra_costs_2025 = {"CADEIRA": {"month": "Novembro", "value": 3400}}
for item, info in extra_costs_2025.items():
    df_fin_2025.loc[df_fin_2025["Mês"] == info["month"], "Custos"] += info["value"]

def compute_statistics(df, df_fin):
    max_single_value = df.drop(columns=["day", "total_day"]).max().max()
    best_single_day = df.loc[df.drop(columns=["day", "total_day"]).eq(max_single_value).any(axis=1), "day"].values[0]

    total_per_day = df.drop(columns=["day", "total_day"]).sum(axis=1)
    best_total_day = df.loc[total_per_day.idxmax(), "day"]
    best_total_value = total_per_day.max()

    total_per_week = df.drop(columns=["day", "total_day"]).sum()
    best_week = total_per_week.idxmax()
    best_week_value = total_per_week.max()

    best_profit_month = df_fin.loc[df_fin["Lucro"].idxmax(), "Mês"]
    best_profit_value = df_fin["Lucro"].max()

    highest_cost_month = df_fin.loc[df_fin["Custos"].idxmax(), "Mês"]
    highest_cost_value = df_fin["Custos"].max()

    best_week_translated = translate_week(best_week)

    return {
        "best_week": (best_week_translated, best_week_value),
        "best_single_day": (best_single_day, max_single_value),
        "best_total_day": (best_total_day, best_total_value),
        "best_profit": (best_profit_month, best_profit_value),
        "highest_cost": (highest_cost_month, highest_cost_value)
    }

stats2025 = compute_statistics(clean2025, df_fin_2025)
stats2026 = compute_statistics(clean2026, df_fin_2026)

st.header("📊 Estatísticas Relevantes 2025 e Previsão 2026")
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

st.header("📌 Custos e Lucros Individuais por Ano")
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

st.header("📊 Comparativo de Atendimentos e Lucros 2025 vs Previsão 2026")
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

st.header("💰 Comparativo de Custos: 2025 vs Previsão 2026")
df_cost_compare = pd.DataFrame({
    "Mês": df_fin_2025["Mês"],
    "Custos 2025": df_fin_2025["Custos"],
    "Custos previstos 2026": df_fin_2026["Custos"]
})
fig_cost_compare = px.line(df_cost_compare, x="Mês", y=["Custos 2025", "Custos previstos 2026"],
                           markers=True, template="plotly_white")
st.plotly_chart(fig_cost_compare, use_container_width=True)

st.header("🔥 Mapa de Calor Semanal 2025")
fig_heat_2025 = px.imshow(clean2025.drop(columns=["day", "total_day"]).values,
                          x=[translate_week(col) for col in clean2025.drop(columns=["day", "total_day"]).columns],
                          y=DAYS_FULL,
                          color_continuous_scale="OrRd",
                          labels=dict(x="Semana", y="Dia"))
st.plotly_chart(fig_heat_2025, use_container_width=True)

st.header("🔥 Previsão de Mapa de Calor Semanal 2026")
fig_heat_2026 = px.imshow(clean2026.drop(columns=["day", "total_day"]).values,
                          x=[translate_week(col) for col in clean2026.drop(columns=["day", "total_day"]).columns],
                          y=DAYS_FULL,
                          color_continuous_scale="OrRd",
                          labels=dict(x="Semana", y="Dia"))
st.plotly_chart(fig_heat_2026, use_container_width=True)

# --- NOVO GRÁFICO: soma dos atendimentos por dia da semana ---
def sum_by_weekday(df):
    df_sums = df.drop(columns=["total_day"]).groupby("day").sum()
    df_sums["Total"] = df_sums.sum(axis=1)
    return df_sums["Total"].reindex(DAYS_FULL)

sums_2025 = sum_by_weekday(clean2025)
sums_2026 = sum_by_weekday(clean2026)

df_weekday_compare = pd.DataFrame({
    "Dia da Semana": DAYS_FULL,
    "Atendimentos 2025": sums_2025.values,
    "Atendimentos 2026": sums_2026.values
})

st.header("📊 Total de Atendimentos por Dia da Semana – 2025 vs Previsão 2026")
fig_weekday_compare = px.bar(
    df_weekday_compare,
    x="Dia da Semana",
    y=["Atendimentos 2025", "Atendimentos 2026"],
    barmode="group",
    title="Atendimentos por Dia da Semana",
    template="plotly_white"
)
st.plotly_chart(fig_weekday_compare, use_container_width=True)
