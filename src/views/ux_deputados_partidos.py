import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.filters import split_values
from src.components.tables import show_dataframe
from src.services import get_ranking_deputados, get_ranking_partidos


def _ranking_from_filtered(filtered_df: pd.DataFrame, column: str, output_name: str) -> pd.DataFrame:
    rows = []
    for value in filtered_df[column].dropna():
        for item in str(value).split(","):
            item = item.strip()
            if item and not item.startswith("Sem "):
                rows.append({output_name: item})
    if not rows:
        return pd.DataFrame(columns=[output_name, "quantidade"])
    return (
        pd.DataFrame(rows)
        .groupby(output_name, as_index=False)
        .size()
        .rename(columns={"size": "quantidade"})
        .sort_values("quantidade", ascending=False)
    )


def render_deputados_partidos_ux(
    config_items: tuple[tuple[str, str], ...],
    filtered_df: pd.DataFrame,
) -> None:
    st.header("Deputados e Partidos")
    st.write(
        "Acompanhe quais parlamentares e partidos aparecem mais no recorte selecionado. "
        "Os filtros laterais alteram os gráficos desta página."
    )

    deputados = get_ranking_deputados(config_items)
    partidos = get_ranking_partidos(config_items)
    top_n = st.slider("Quantidade exibida nos rankings", 5, 50, 15, 5)

    deputados_recorte = _ranking_from_filtered(filtered_df, "autores", "deputado")
    partidos_recorte = _ranking_from_filtered(filtered_df, "partidos", "partido")
    st.caption(
        f"{len(split_values(filtered_df['autores']))} deputado(s) e "
        f"{len(split_values(filtered_df['partidos']))} partido(s) aparecem no recorte atual."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Deputados mais presentes no recorte")
        plot_bar(
            deputados_recorte,
            "deputado",
            "quantidade",
            "Deputados por ocorrência nas proposições filtradas",
            top_n=top_n,
            horizontal=True,
        )
    with col_b:
        st.markdown("### Partidos mais presentes no recorte")
        plot_bar(
            partidos_recorte,
            "partido",
            "quantidade",
            "Partidos por ocorrência nas proposições filtradas",
            top_n=top_n,
        )

    st.markdown("### Ranking geral de deputados")
    st.caption("Tabela de apoio calculada sobre toda a base carregada.")
    show_dataframe(
        deputados[
            [
                "deputado",
                "sigla_uf",
                "partido",
                "quantidade_proposicoes_assinadas",
                "quantidade_como_proponente",
            ]
        ].head(100)
    )

    if not partidos.empty:
        lider = partidos.iloc[0]
        st.info(
            f"Na base completa, o partido com maior quantidade de proposições associadas é "
            f"**{lider['partido']}**, com **{int(lider['quantidade_proposicoes'])}** proposição(ões)."
        )
