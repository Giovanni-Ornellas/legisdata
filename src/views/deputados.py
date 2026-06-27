import streamlit as st

from src.components.charts import plot_bar
from src.components.help_text import render_help_box, render_query_explanation
from src.components.tables import download_csv, show_dataframe
from src.content.explicacoes_consultas import EXPLICACOES_CONSULTAS
from src.services import get_ranking_deputados


def render_deputados(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Ranking de Deputados")
    render_help_box(
        "Quem são os autores?",
        "Autores e assinantes são deputados vinculados a uma proposição nos dados da Câmara. "
        "A aplicação mostra essas relações sem avaliar posição política ou mérito da matéria.",
    )
    render_query_explanation(EXPLICACOES_CONSULTAS["ranking_deputados"])
    df = get_ranking_deputados(config_items)
    plot_bar(df, "deputado", "quantidade_proposicoes_assinadas", "Top deputados por proposições", top_n=10)
    show_dataframe(df)
    download_csv(df, "ranking_deputados.csv")
