import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.controls import select_table_limit, select_top_n
from src.components.help_text import render_help_box, render_query_explanation
from src.components.tables import download_csv, show_dataframe
from src.content.explicacoes_consultas import EXPLICACOES_CONSULTAS
from src.services import get_tramitacoes_acima_media


ULTIMA_TRAMITACAO_COLS = [
    "proposicao",
    "data_ultima_tramitacao",
    "descricao_situacao",
    "descricao_tramitacao",
    "sigla_orgao",
    "nome_orgao",
    "ementa",
    "link_camara",
]


def render_ultima_tramitacao(filtered_df: pd.DataFrame) -> None:
    st.subheader("Última Tramitação")
    render_help_box(
        "O que é tramitação?",
        "Tramitação é o histórico de movimentações de uma proposição. Cada registro pode indicar uma apresentação, recebimento, despacho, arquivamento ou outro andamento.",
    )
    render_query_explanation(EXPLICACOES_CONSULTAS["ultima_tramitacao"])
    table_limit = select_table_limit(default=50)
    show_dataframe(
        filtered_df[ULTIMA_TRAMITACAO_COLS].head(table_limit),
        link_columns={"link_camara": st.column_config.LinkColumn("Câmara")},
    )
    download_csv(filtered_df[ULTIMA_TRAMITACAO_COLS], "ultima_tramitacao.csv")


def render_tramitacoes_acima_media(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Proposições com Tramitação Acima da Média")
    render_help_box(
        "Como interpretar muitas tramitações?",
        "Uma quantidade maior de tramitações indica mais registros de movimentação no banco. Isso não significa, por si só, aprovação, rejeição ou importância política.",
    )
    render_query_explanation(EXPLICACOES_CONSULTAS["tramitacoes_acima_media"])
    df = get_tramitacoes_acima_media(config_items)
    top_n = select_top_n(default=10)
    table_limit = select_table_limit(default=50)
    if not df.empty:
        chart_df = df.copy()
        chart_df["proposicao"] = (
            chart_df["Sigla_tipo"].fillna("")
            + " "
            + chart_df["numero"].astype(str)
            + "/"
            + chart_df["ano"].astype(str)
        )
        plot_bar(chart_df, "proposicao", "quantidade_tramitacoes", "Proposições mais movimentadas", top_n=top_n)
    show_dataframe(df.head(table_limit))
    download_csv(df, "tramitacoes_acima_media.csv")
