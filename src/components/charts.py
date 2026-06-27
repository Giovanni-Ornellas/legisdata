import pandas as pd
import plotly.express as px
import streamlit as st

from src.components.tables import DISPLAY_COLUMN_LABELS


SPECTRUM_COLORS = {
    "Não atribuído": "#B8B8B8",
    "Esquerda": "#C43C39",
    "Centro-Esquerda": "#E68A70",
    "Centro": "#8C7AA9",
    "Centro-Direita": "#5F8CCB",
    "Direita": "#2457A6",
    "Visão Independente": "#6D6D6D",
}


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str, top_n: int = 10, horizontal: bool = False) -> None:
    if df.empty or x not in df or y not in df:
        st.info("Não há dados suficientes para o gráfico.")
        return

    chart_df = df.head(top_n).copy()
    if horizontal:
        fig = px.bar(
            chart_df,
            x=y,
            y=x,
            orientation="h",
            title=title,
            text=y,
            labels=DISPLAY_COLUMN_LABELS,
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
    else:
        fig = px.bar(chart_df, x=x, y=y, title=title, text=y, labels=DISPLAY_COLUMN_LABELS)

    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
    st.plotly_chart(fig, width="stretch")


def plot_line_by_month(df: pd.DataFrame) -> None:
    if df.empty:
        return
    fig = px.line(
        df,
        x="mes_apresentacao",
        y="quantidade",
        markers=True,
        title="Proposições por mês",
        labels=DISPLAY_COLUMN_LABELS,
    )
    st.plotly_chart(fig, width="stretch")


def plot_theme_coverage(com_tema: int, sem_tema: int) -> None:
    tema_df = pd.DataFrame(
        {"classificacao": ["Com tema", "Sem tema"], "quantidade": [com_tema, sem_tema]}
    )
    fig = px.pie(
        tema_df,
        names="classificacao",
        values="quantidade",
        title="Cobertura de classificação temática",
        labels=DISPLAY_COLUMN_LABELS,
    )
    st.plotly_chart(fig, width="stretch")


def plot_spectrum_treemap(df: pd.DataFrame) -> None:
    fig = px.treemap(
        df,
        path=[px.Constant("Todos os espectros"), "espectro", "partido"],
        values="quantidade",
        color="espectro",
        color_discrete_map=SPECTRUM_COLORS,
        labels=DISPLAY_COLUMN_LABELS,
    )
    fig.update_traces(textinfo="label+value")
    st.plotly_chart(fig, width="stretch")


def plot_spectrum_bar(df: pd.DataFrame) -> None:
    grouped = df.groupby("espectro", as_index=False)["quantidade"].sum().sort_values("quantidade", ascending=False)
    fig = px.bar(
        grouped,
        x="espectro",
        y="quantidade",
        color="espectro",
        color_discrete_map=SPECTRUM_COLORS,
        text="quantidade",
        title="Proposições por espectro no recorte filtrado",
        labels=DISPLAY_COLUMN_LABELS,
    )
    st.plotly_chart(fig, width="stretch")
