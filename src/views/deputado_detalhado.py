import streamlit as st

from src.components.charts import plot_bar
from src.components.controls import select_table_limit, select_top_n
from src.components.help_text import render_help_box
from src.components.tables import show_dataframe
from src.services import get_deputados, get_proposicoes_deputado, get_temas_deputado


def render_deputado_detalhado(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Deputado Detalhado")
    render_help_box(
        "O que esta página mostra?",
        "Selecione um deputado para ver seus dados básicos, proposições assinadas no banco e temas mais frequentes nessas proposições.",
    )

    deputados = get_deputados(config_items)
    if deputados.empty:
        st.info("Não há deputados carregados no banco.")
        return

    busca = st.text_input("Buscar deputado por nome, partido ou UF")
    filtered = deputados.copy()
    if busca:
        termo = busca.lower()
        filtered = filtered[
            filtered["nome"].fillna("").str.lower().str.contains(termo, regex=False)
            | filtered["partido"].fillna("").str.lower().str.contains(termo, regex=False)
            | filtered["sigla_uf"].fillna("").str.lower().str.contains(termo, regex=False)
        ]

    if filtered.empty:
        st.info("Nenhum deputado encontrado com a busca atual.")
        return

    labels = {
        row.deputado_id: f"{row.nome} · {row.partido or 'Sem partido'}-{row.sigla_uf or 'UF não informada'}"
        for row in filtered.itertuples()
    }
    deputado_id = st.selectbox("Selecione um deputado", options=list(labels.keys()), format_func=lambda value: labels[value])
    deputado = deputados[deputados["deputado_id"] == deputado_id].iloc[0]

    col1, col2 = st.columns([1, 3])
    with col1:
        if deputado.get("url_foto"):
            st.image(deputado["url_foto"], caption=deputado["nome"])
    with col2:
        st.markdown(f"**Nome:** {deputado['nome']}")
        st.markdown(f"**Partido:** {deputado['partido'] or 'Não informado'}")
        st.markdown(f"**UF:** {deputado['sigla_uf'] or 'Não informada'}")
        st.markdown(f"**E-mail:** {deputado['email'] or 'Não informado'}")

    proposicoes = get_proposicoes_deputado(config_items, int(deputado_id))
    temas = get_temas_deputado(config_items, int(deputado_id))

    st.metric("Proposições assinadas no banco", len(proposicoes))
    top_n = select_top_n(default=10)
    table_limit = select_table_limit(default=50)
    plot_bar(temas, "tema", "quantidade_proposicoes", "Temas mais frequentes nas proposições do deputado", top_n=top_n, horizontal=True)

    st.markdown("### Proposições assinadas")
    show_dataframe(proposicoes.head(table_limit))
