import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.controls import select_table_limit, select_top_n
from src.components.help_text import render_help_box, render_query_explanation
from src.components.tables import download_csv, show_dataframe
from src.content.explicacoes_consultas import EXPLICACOES_CONSULTAS
from src.services import get_ranking_partidos


def render_partidos(config_items: tuple[tuple[str, str], ...], filtered_df: pd.DataFrame) -> None:
    st.subheader("Ranking de Partidos")
    render_help_box(
        "O que são partidos nesta visualização?",
        "Partidos aparecem associados aos deputados autores ou assinantes das proposições carregadas no banco.",
    )
    render_query_explanation(EXPLICACOES_CONSULTAS["ranking_partidos"])
    df = get_ranking_partidos(config_items)
    top_n = select_top_n(default=10)
    table_limit = select_table_limit(default=30)
    plot_bar(df, "partido", "quantidade_proposicoes", "Top partidos por proposições", top_n=top_n)
    show_dataframe(df.head(table_limit))
    download_csv(df, "ranking_partidos.csv")

    st.markdown("#### Distribuição no recorte filtrado")
    rows = []
    for _, row in filtered_df.iterrows():
        for partido in str(row["partidos"]).split(","):
            partido = partido.strip()
            if partido and not partido.startswith("Sem "):
                rows.append(partido)

    if not rows:
        st.info("Não há partidos no recorte filtrado.")
        return

    local_df = (
        pd.Series(rows, name="partido")
        .value_counts()
        .reset_index(name="quantidade")
        .rename(columns={"index": "partido"})
    )
    plot_bar(local_df, "partido", "quantidade", "Partidos no recorte filtrado", top_n=top_n)
