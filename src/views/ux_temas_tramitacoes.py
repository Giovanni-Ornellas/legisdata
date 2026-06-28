import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.tables import show_dataframe
from src.services import get_ranking_orgaos, get_temas_acima_media, get_tramitacoes_acima_media


def _temas_frequentes(base_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for temas in base_df["temas"].dropna():
        for tema in str(temas).split(","):
            tema = tema.strip()
            if tema and not tema.startswith("Sem "):
                rows.append({"tema": tema})
    if not rows:
        return pd.DataFrame(columns=["tema", "quantidade"])
    return (
        pd.DataFrame(rows)
        .groupby("tema", as_index=False)
        .size()
        .rename(columns={"size": "quantidade"})
        .sort_values("quantidade", ascending=False)
    )


def render_temas_tramitacoes_ux(
    config_items: tuple[tuple[str, str], ...],
    filtered_df: pd.DataFrame,
) -> None:
    st.header("Temas e Tramitações")
    st.write(
        "Veja quais assuntos, órgãos e situações aparecem com mais força no recorte selecionado. "
        "Use os filtros laterais para acompanhar um tema, partido ou período específico."
    )

    top_n = st.slider("Quantidade exibida nos rankings", 5, 30, 10, 5)

    temas_freq = _temas_frequentes(filtered_df)
    orgaos = get_ranking_orgaos(config_items)
    temas_acima_media = get_temas_acima_media(config_items)
    tramitacoes_acima_media = get_tramitacoes_acima_media(config_items)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Temas mais frequentes")
        st.caption("Quantidade de ocorrências de cada tema nas proposições filtradas pela carga atual.")
        plot_bar(temas_freq, "tema", "quantidade", "Temas mais frequentes", top_n=top_n, horizontal=True)
    with col2:
        st.markdown("### Órgãos com mais tramitações")
        st.caption("Órgãos que aparecem com mais registros na tabela de tramitação.")
        plot_bar(orgaos, "sigla", "quantidade_tramitacoes", "Órgãos por tramitações", top_n=top_n)

    st.markdown("### Situações mais comuns")
    situacoes = (
        filtered_df.fillna({"descricao_situacao": "Sem situação"})
        .groupby("descricao_situacao", as_index=False)
        .agg(quantidade=("proposicao_id", "nunique"))
        .sort_values("quantidade", ascending=False)
    )
    plot_bar(situacoes, "descricao_situacao", "quantidade", "Situações registradas nas proposições", top_n=top_n, horizontal=True)

    tab1, tab2, tab3 = st.tabs(["Temas acima da média", "Tramitações acima da média", "Órgãos"])
    with tab1:
        st.write("Temas cuja quantidade de proposições é superior à média na base completa.")
        show_dataframe(temas_acima_media.head(50))
    with tab2:
        st.write("Proposições com número de tramitações superior à média na base completa.")
        show_dataframe(
            tramitacoes_acima_media[
                ["Sigla_tipo", "numero", "ano", "ementa", "quantidade_tramitacoes"]
            ].head(50)
        )
    with tab3:
        st.write("Ranking dos órgãos por quantidade de tramitações e proposições associadas.")
        show_dataframe(orgaos[["sigla", "nome", "tipo_orgao", "quantidade_tramitacoes", "quantidade_proposicoes"]].head(50))
