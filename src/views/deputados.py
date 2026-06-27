import streamlit as st

from src.components.charts import plot_bar
from src.components.tables import download_csv, show_dataframe
from src.services import get_ranking_deputados


def render_deputados(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Ranking de Deputados")
    df = get_ranking_deputados(config_items)
    plot_bar(df, "deputado", "quantidade_proposicoes_assinadas", "Top deputados por proposições", top_n=10)
    show_dataframe(df)
    download_csv(df, "ranking_deputados.csv")
