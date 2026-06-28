import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.tables import show_dataframe
from src.queries import RANKING_DEPUTADOS_QUERY, RANKING_PARTIDOS_QUERY
from src.services import get_ranking_deputados, get_ranking_partidos
from src.views.ux_helpers import show_sql


def render_deputados_partidos_ux(config_items: tuple[tuple[str, str], ...]) -> None:
    st.header("Deputados e Partidos")
    st.write(
        "Esta página resume a participação legislativa por deputado e por partido, usando a relação "
        "de autoria registrada na tabela Participa."
    )

    deputados = get_ranking_deputados(config_items)
    partidos = get_ranking_partidos(config_items)

    st.markdown("### Filtros")
    col1, col2, col3 = st.columns(3)
    partidos_sel = col1.multiselect("Partido", sorted(deputados["partido"].dropna().unique()))
    ufs_sel = col2.multiselect("UF", sorted(deputados["sigla_uf"].dropna().unique()))
    top_n = col3.slider("Quantidade no ranking", 5, 50, 15, 5)

    filtered = deputados.copy()
    if partidos_sel:
        filtered = filtered[filtered["partido"].isin(partidos_sel)]
    if ufs_sel:
        filtered = filtered[filtered["sigla_uf"].isin(ufs_sel)]

    st.caption(f"{len(filtered)} deputado(s) no recorte atual.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Deputados mais ativos")
        plot_bar(
            filtered,
            "deputado",
            "quantidade_proposicoes_assinadas",
            "Deputados por proposições assinadas",
            top_n=top_n,
            horizontal=True,
        )
    with col_b:
        st.markdown("### Partidos com mais proposições")
        plot_bar(
            partidos,
            "partido",
            "quantidade_proposicoes",
            "Partidos por proposições com autoria",
            top_n=top_n,
        )

    st.markdown("### Tabela de deputados")
    show_dataframe(
        filtered[
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
        total_partidos = int(partidos["quantidade_proposicoes"].sum())
        lider = partidos.iloc[0]
        st.info(
            f"No recorte total, o partido com maior quantidade de proposições associadas é "
            f"**{lider['partido']}**, com **{int(lider['quantidade_proposicoes'])}** proposição(ões). "
            f"A soma das participações por partido no ranking é **{total_partidos}**."
        )

    show_sql(RANKING_DEPUTADOS_QUERY, "Ver consulta SQL do ranking de deputados")
    show_sql(RANKING_PARTIDOS_QUERY, "Ver consulta SQL do ranking de partidos")
