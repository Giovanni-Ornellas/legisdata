import pandas as pd
import streamlit as st

from src.components.charts import plot_bar, plot_line_by_month, plot_theme_coverage
from src.components.help_text import render_help_box
from src.components.metrics import render_metric_row
from src.services import get_counts


def render_home(
    config_items: tuple[tuple[str, str], ...],
    base_df: pd.DataFrame,
    filtered_df: pd.DataFrame,
) -> None:
    st.subheader("Visão Geral")
    render_help_box(
        "Para que serve esta aplicação?",
        "Esta aplicação ajuda a visualizar dados de proposições legislativas da Câmara dos Deputados. "
        "Ela mostra quem propôs uma matéria, quais partidos aparecem, quais temas são tratados, "
        "por onde a proposição tramitou e qual situação aparece nos dados carregados.",
    )
    with st.expander("Como navegar pelos dados?"):
        st.markdown(
            "- Use os filtros laterais para escolher ano, tipo de proposição, tema, partido ou deputado.\n"
            "- A aba **Entenda uma Proposição** mostra um resumo didático de uma matéria específica.\n"
            "- A aba **Glossário** explica termos como ementa, tramitação, despacho e comissão.\n"
            "- Os rankings ajudam a responder quais partidos, deputados e temas aparecem com mais frequência."
        )

    counts = get_counts(config_items)
    if not counts.empty:
        values = dict(zip(counts["metrica"], counts["total"]))
        cols = st.columns(6)
        for col, key in zip(cols, ["Proposições", "Deputados", "Partidos", "Temas", "Tramitações", "Autorias"]):
            col.metric(key, int(values.get(key, 0)))

    st.markdown("#### Recorte filtrado")
    render_metric_row(filtered_df)

    if filtered_df.empty:
        st.info("Nenhum registro encontrado com os filtros atuais.")
        return

    col1, col2 = st.columns(2)
    with col1:
        by_month = (
            filtered_df.dropna(subset=["mes_apresentacao"])
            .groupby("mes_apresentacao", as_index=False)
            .size()
            .rename(columns={"size": "quantidade"})
        )
        plot_line_by_month(by_month)
    with col2:
        by_type = (
            filtered_df.groupby("Sigla_tipo", as_index=False)
            .size()
            .rename(columns={"size": "quantidade"})
            .sort_values("quantidade", ascending=False)
        )
        plot_bar(by_type, "Sigla_tipo", "quantidade", "Proposições por tipo", top_n=12)

    col3, col4 = st.columns(2)
    with col3:
        by_situation = (
            filtered_df.fillna({"descricao_situacao": "Sem situação"})
            .groupby("descricao_situacao", as_index=False)
            .size()
            .rename(columns={"size": "quantidade"})
            .sort_values("quantidade", ascending=False)
        )
        plot_bar(by_situation, "descricao_situacao", "quantidade", "Situação atual", top_n=10, horizontal=True)
    with col4:
        sem_tema = int((base_df["temas"] == "Sem tema associado").sum())
        com_tema = int(len(base_df) - sem_tema)
        plot_theme_coverage(com_tema, sem_tema)
