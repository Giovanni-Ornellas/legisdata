import pandas as pd
import streamlit as st

from src.components.help_text import render_help_box
from src.components.tables import show_dataframe
from src.components.timeline import render_timeline
from src.services import get_tramitacoes_proposicao


RESUMO_COLS = [
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


def _format_date(value) -> str:
    if pd.isna(value):
        return "data não informada"
    return pd.to_datetime(value).strftime("%d/%m/%Y")


def _select_proposicao(filtered_df: pd.DataFrame) -> pd.Series | None:
    if filtered_df.empty:
        st.info("Nenhuma proposição encontrada com os filtros atuais.")
        return None

    options = filtered_df.sort_values(["data_apresentacao", "proposicao_id"], ascending=[False, False])
    labels = {
        row.proposicao_id: f"{row.proposicao} · {str(row.ementa)[:120]}"
        for row in options.itertuples()
    }
    selected_id = st.selectbox(
        "Escolha uma proposição para entender",
        options=list(labels.keys()),
        format_func=lambda value: labels[value],
    )
    return options[options["proposicao_id"] == selected_id].iloc[0]


def render_entenda_proposicao(
    config_items: tuple[tuple[str, str], ...],
    filtered_df: pd.DataFrame,
) -> None:
    st.subheader("Entenda uma Proposição")
    render_help_box(
        "O objetivo desta página",
        "Esta página resume uma proposição específica em linguagem simples, usando apenas os campos disponíveis no banco: ementa, autores, partidos, temas, situação, órgãos e tramitações.",
    )

    selected = _select_proposicao(filtered_df)
    if selected is None:
        return

    st.markdown("### Resumo")
    col1, col2, col3 = st.columns(3)
    col1.metric("Tipo", selected["Sigla_tipo"])
    col2.metric("Número", int(selected["numero"]) if pd.notna(selected["numero"]) else "Não informado")
    col3.metric("Ano", int(selected["ano"]) if pd.notna(selected["ano"]) else "Não informado")

    st.markdown(f"**Ementa:** {selected['ementa'] or 'Não informada'}")
    st.markdown(f"**Autores:** {selected['autores']}")
    st.markdown(f"**Partidos envolvidos:** {selected['partidos']}")
    st.markdown(f"**Temas:** {selected['temas']}")
    st.markdown(f"**Situação mais recente no banco:** {selected['descricao_situacao'] or 'Não informada'}")

    tema_principal = str(selected["temas"]).split(",")[0].strip()
    if tema_principal.startswith("Sem "):
        tema_principal = "tema não informado"
    st.info(
        f"Essa proposição trata de **{tema_principal}**. "
        f"Ela foi apresentada em **{_format_date(selected['data_apresentacao'])}** "
        f"e possui **{int(selected['quantidade_tramitacoes'])}** tramitação(ões) registrada(s) no banco."
    )

    st.markdown("### Dados principais")
    show_dataframe(
        pd.DataFrame([selected[RESUMO_COLS]]),
        link_columns={"link_camara": st.column_config.LinkColumn("Câmara")},
    )

    st.markdown("### Linha do tempo da tramitação")
    tramitacoes = get_tramitacoes_proposicao(config_items, int(selected["proposicao_id"]))
    render_timeline(tramitacoes)
