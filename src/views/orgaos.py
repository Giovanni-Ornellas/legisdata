import streamlit as st

from src.components.charts import plot_bar
from src.components.help_text import render_help_box
from src.components.tables import show_dataframe
from src.services import get_orgaos, get_proposicoes_por_orgao, get_ranking_orgaos


def render_orgaos(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Órgãos e Tramitações")
    render_help_box(
        "O que são órgãos?",
        "Órgãos são estruturas da Câmara relacionadas à tramitação, como comissões, Mesa Diretora e Plenário. Eles aparecem nos registros de movimentação das proposições.",
    )

    orgaos = get_orgaos(config_items)
    ranking = get_ranking_orgaos(config_items)

    col1, col2 = st.columns(2)
    col1.metric("Órgãos cadastrados", len(orgaos))
    col2.metric("Tipos de órgão", orgaos["tipo_orgao"].nunique() if not orgaos.empty else 0)

    st.markdown("### Tipos de órgão")
    tipos = orgaos["tipo_orgao"].fillna("Sem tipo informado").value_counts().reset_index()
    tipos.columns = ["tipo_orgao", "quantidade"]
    plot_bar(tipos, "tipo_orgao", "quantidade", "Quantidade de órgãos por tipo", top_n=12, horizontal=True)

    st.markdown("### Órgãos com mais tramitações")
    plot_bar(ranking, "sigla", "quantidade_tramitacoes", "Ranking de órgãos por tramitações", top_n=15)
    show_dataframe(ranking.head(30))

    st.markdown("### Proposições que passaram por um órgão")
    if orgaos.empty:
        st.info("Não há órgãos cadastrados.")
        return

    opcoes = {
        row.orgao_id: f"{row.sigla or 'Sem sigla'} - {row.nome}"
        for row in orgaos.itertuples()
    }
    orgao_id = st.selectbox("Selecione um órgão", options=list(opcoes.keys()), format_func=lambda value: opcoes[value])
    selecionado = orgaos[orgaos["orgao_id"] == orgao_id].iloc[0]
    st.caption(f"Tipo de órgão: {selecionado['tipo_orgao'] or 'Não informado'}")

    proposicoes = get_proposicoes_por_orgao(config_items, int(orgao_id))
    show_dataframe(proposicoes)
