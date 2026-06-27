import pandas as pd
import streamlit as st

from src.components.help_text import render_help_box, render_query_explanation
from src.components.tables import download_csv, show_dataframe
from src.content.explicacoes_consultas import EXPLICACOES_CONSULTAS


PROPOSICOES_COLS = [
    "proposicao",
    "data_apresentacao",
    "descricao_tipo",
    "ementa",
    "temas",
    "autores",
    "partidos",
    "link_camara",
]

EXPLORAR_COLS = [
    "proposicao",
    "data_apresentacao",
    "descricao_tipo",
    "descricao_situacao",
    "quantidade_autores",
    "quantidade_tramitacoes",
    "temas",
    "autores",
    "partidos",
    "ementa",
    "link_camara",
]


def render_proposicoes_temas(filtered_df: pd.DataFrame) -> None:
    st.subheader("Proposições e Temas")
    render_help_box(
        "O que é uma proposição?",
        "Proposição é uma matéria legislativa apresentada à Câmara, como projeto de lei, indicação ou requerimento. "
        "Os temas ajudam a identificar o assunto tratado quando essa classificação está disponível.",
    )
    render_query_explanation(EXPLICACOES_CONSULTAS["proposicoes_temas"])
    sem_tema = int((filtered_df["temas"] == "Sem tema associado").sum())
    st.caption(f"{sem_tema} proposições no recorte aparecem sem tema associado e permanecem visíveis pelo LEFT JOIN.")
    show_dataframe(
        filtered_df[PROPOSICOES_COLS],
        link_columns={"link_camara": st.column_config.LinkColumn("Câmara")},
    )
    download_csv(filtered_df[PROPOSICOES_COLS], "proposicoes_temas.csv")


def render_explorar(filtered_df: pd.DataFrame) -> None:
    st.subheader("Explorar Proposições")
    render_help_box(
        "Como usar esta tabela?",
        "Use esta aba para procurar proposições por ementa, autor, partido, tema ou situação. "
        "A tabela mostra um resumo amplo dos campos mais importantes para análise.",
    )
    rows_per_page = st.slider("Quantidade de linhas na tabela", min_value=10, max_value=200, value=50, step=10)
    show_dataframe(
        filtered_df[EXPLORAR_COLS].head(rows_per_page),
        link_columns={"link_camara": st.column_config.LinkColumn("Câmara")},
    )
    download_csv(filtered_df[EXPLORAR_COLS], "proposicoes_filtradas.csv")
