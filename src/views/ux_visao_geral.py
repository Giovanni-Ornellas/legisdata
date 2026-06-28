import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.help_text import render_help_box
from src.components.tables import show_dataframe
from src.queries import BASE_PROPOSICOES_QUERY, COUNT_QUERY
from src.services import get_counts
from src.views.ux_helpers import show_sql


def render_visao_geral_ux(config_items: tuple[tuple[str, str], ...], base_df: pd.DataFrame) -> None:
    st.header("Visão Geral")
    st.write(
        "Comece por aqui para entender o tamanho da base, os tipos de proposição carregados "
        "e a distribuição inicial dos dados legislativos."
    )

    counts = get_counts(config_items)
    values = dict(zip(counts["metrica"], counts["total"])) if not counts.empty else {}
    cols = st.columns(6)
    for col, label in zip(cols, ["Proposições", "Deputados", "Partidos", "Temas", "Tramitações", "Autorias"]):
        col.metric(label, int(values.get(label, 0)))

    render_help_box(
        "O que esta página responde?",
        "Ela mostra o volume geral do banco e ajuda a identificar quais tipos e situações aparecem com mais frequência.",
    )

    if base_df.empty:
        st.info("O banco conectou, mas não há proposições carregadas.")
        return

    col1, col2 = st.columns(2)
    with col1:
        by_type = (
            base_df.groupby("Sigla_tipo", as_index=False)
            .agg(quantidade=("proposicao_id", "nunique"))
            .sort_values("quantidade", ascending=False)
        )
        plot_bar(by_type, "Sigla_tipo", "quantidade", "Tipos de proposição mais frequentes", top_n=10)

    with col2:
        by_status = (
            base_df.fillna({"descricao_situacao": "Sem situação"})
            .groupby("descricao_situacao", as_index=False)
            .agg(quantidade=("proposicao_id", "nunique"))
            .sort_values("quantidade", ascending=False)
        )
        plot_bar(by_status, "descricao_situacao", "quantidade", "Situações mais frequentes", top_n=10, horizontal=True)

    st.markdown("### Amostra da base")
    show_dataframe(
        base_df[
            [
                "proposicao",
                "data_apresentacao",
                "descricao_tipo",
                "ementa",
                "autores",
                "partidos",
                "temas",
                "descricao_situacao",
            ]
        ].head(12)
    )

    show_sql(COUNT_QUERY, "Ver consulta SQL das métricas")
    show_sql(BASE_PROPOSICOES_QUERY, "Ver consulta SQL da base de proposições")
