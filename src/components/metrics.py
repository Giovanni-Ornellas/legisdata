import pandas as pd
import streamlit as st

from src.components.filters import split_values


def render_metric_row(df: pd.DataFrame) -> None:
    cols = st.columns(6)
    values = [
        ("Proposições", df["proposicao_id"].nunique()),
        ("Deputados autores", int(df["quantidade_autores"].sum())),
        ("Partidos", len(split_values(df["partidos"]))),
        ("Temas", len(split_values(df["temas"]))),
        ("Tramitações", int(df["quantidade_tramitacoes"].sum())),
        ("Sem tema", int((df["temas"] == "Sem tema associado").sum())),
    ]
    for col, (label, value) in zip(cols, values):
        col.metric(label, value)
