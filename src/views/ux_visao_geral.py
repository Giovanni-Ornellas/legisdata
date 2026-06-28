import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.filters import split_values
from src.components.help_text import render_help_box
from src.components.tables import show_dataframe
from src.services import get_counts


def render_visao_geral_ux(
    config_items: tuple[tuple[str, str], ...],
    base_df: pd.DataFrame,
    filtered_df: pd.DataFrame,
) -> None:
    st.header("Visão Geral")
    st.write(
        "Um panorama rápido do que está acontecendo no recorte selecionado. Use os filtros laterais "
        "para acompanhar anos, temas, partidos ou palavras-chave específicas."
    )

    counts = get_counts(config_items)
    values = dict(zip(counts["metrica"], counts["total"])) if not counts.empty else {}
    cols = st.columns(5)
    cols[0].metric("Proposições no recorte", filtered_df["proposicao_id"].nunique())
    cols[1].metric("Total na base", int(values.get("Proposições", 0)))
    cols[2].metric("Temas no recorte", len(split_values(filtered_df["temas"])))
    cols[3].metric("Partidos no recorte", len(split_values(filtered_df["partidos"])))
    cols[4].metric("Tramitações no recorte", int(filtered_df["quantidade_tramitacoes"].sum()))

    render_help_box(
        "Leitura rápida",
        "Os cartões e gráficos abaixo mudam conforme os filtros laterais. Eles ajudam a perceber volume, temas e situações sem precisar olhar diretamente para as tabelas.",
    )

    if filtered_df.empty:
        st.info("Nenhuma proposição encontrada com os filtros atuais. Remova algum filtro para ampliar a busca.")
        return

    col1, col2 = st.columns(2)
    with col1:
        by_type = (
            filtered_df.groupby("Sigla_tipo", as_index=False)
            .agg(quantidade=("proposicao_id", "nunique"))
            .sort_values("quantidade", ascending=False)
        )
        plot_bar(by_type, "Sigla_tipo", "quantidade", "Tipos de proposição mais frequentes", top_n=10)

    with col2:
        by_status = (
            filtered_df.fillna({"descricao_situacao": "Sem situação"})
            .groupby("descricao_situacao", as_index=False)
            .agg(quantidade=("proposicao_id", "nunique"))
            .sort_values("quantidade", ascending=False)
        )
        plot_bar(by_status, "descricao_situacao", "quantidade", "Situações mais frequentes", top_n=10, horizontal=True)

    st.markdown("### Amostra da base")
    show_dataframe(
        filtered_df[
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
