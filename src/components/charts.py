import pandas as pd
import plotly.express as px
import streamlit as st

from src.components.tables import DISPLAY_COLUMN_LABELS


SPECTRUM_COLORS = {
    "Não atribuído": "#A7ADB7",
    "Esquerda": "#B94A48",
    "Centro-Esquerda": "#D88B72",
    "Centro": "#8F7BAE",
    "Centro-Direita": "#6C92C7",
    "Direita": "#315F9E",
    "Visão Independente": "#747474",
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
    chart_df = df.copy()
    chart_df["texto"] = chart_df["partido"] + "<br>" + chart_df["quantidade"].astype(str)
    fig = px.treemap(
        chart_df,
        path=["espectro", "partido"],
        values="quantidade",
        color="espectro",
        color_discrete_map=SPECTRUM_COLORS,
        labels=DISPLAY_COLUMN_LABELS,
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value}",
        hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Espectro: %{parent}<extra></extra>",
        marker=dict(line=dict(color="rgba(255,255,255,0.45)", width=1)),
        tiling=dict(pad=3),
        textfont=dict(size=13),
    )
    fig.update_layout(
        height=430,
        margin=dict(l=0, r=0, t=12, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        uniformtext=dict(minsize=10, mode="hide"),
    )
    st.plotly_chart(fig, width="stretch")


def plot_spectrum_bar(df: pd.DataFrame) -> None:
    grouped = df.groupby("espectro", as_index=False)["quantidade"].sum().sort_values("quantidade", ascending=False)
    fig = px.bar(
        grouped,
        x="quantidade",
        y="espectro",
        orientation="h",
        color="espectro",
        color_discrete_map=SPECTRUM_COLORS,
        text="quantidade",
        title="Proposições por espectro no recorte filtrado",
        labels=DISPLAY_COLUMN_LABELS,
    )
    fig.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<extra></extra>",
        marker_line_width=0,
    )
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=35, t=50, b=10),
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")
