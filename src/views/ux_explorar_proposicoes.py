import pandas as pd
import streamlit as st

from src.components.tables import show_dataframe
from src.components.timeline import render_timeline
from src.services import get_tramitacoes_proposicao
from src.views.ux_helpers import build_proposicao_options


RESULT_COLS = [
    "proposicao",
    "data_apresentacao",
    "descricao_tipo",
    "ementa",
    "autores",
    "partidos",
    "temas",
    "descricao_situacao",
    "quantidade_tramitacoes",
    "link_camara",
]


def render_explorar_proposicoes_ux(
    config_items: tuple[tuple[str, str], ...],
    filtered_df: pd.DataFrame,
) -> None:
    st.header("Explorar Proposições")
    st.write(
        "Veja as proposições encontradas pelos filtros laterais e abra um registro para entender autores, "
        "temas, situação e histórico de tramitação."
    )

    st.markdown("### Resultados")
    if filtered_df.empty:
        st.info("Nenhum resultado encontrado. Remova algum filtro para ampliar a busca.")
        return

    table_limit = st.slider("Quantidade de linhas na tabela", 10, 100, 25, 5)
    show_dataframe(
        filtered_df[RESULT_COLS].head(table_limit),
        link_columns={"link_camara": st.column_config.LinkColumn("Câmara")},
    )

    st.markdown("### Detalhar uma proposição")
    options = build_proposicao_options(filtered_df.head(250))
    selected_id = st.selectbox(
        "Escolha uma proposição do recorte filtrado",
        options=list(options.keys()),
        format_func=lambda value: options[value],
    )
    selected = filtered_df[filtered_df["proposicao_id"] == selected_id].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tipo", selected["Sigla_tipo"])
    col2.metric("Número", int(selected["numero"]) if pd.notna(selected["numero"]) else "Não informado")
    col3.metric("Ano", int(selected["ano"]) if pd.notna(selected["ano"]) else "Não informado")
    col4.metric("Tramitações", int(selected["quantidade_tramitacoes"]))

    st.markdown(f"**Ementa:** {selected['ementa'] or 'Não informada'}")
    st.markdown(f"**Autores:** {selected['autores']}")
    st.markdown(f"**Partidos:** {selected['partidos']}")
    st.markdown(f"**Temas:** {selected['temas']}")
    st.markdown(f"**Situação mais recente:** {selected['descricao_situacao'] or 'Não informada'}")

    st.markdown("### Linha do tempo")
    tramitacoes = get_tramitacoes_proposicao(config_items, int(selected_id))
    render_timeline(tramitacoes.head(30))
