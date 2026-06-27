import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.tables import download_csv, show_dataframe
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
    show_dataframe(
        filtered_df[ULTIMA_TRAMITACAO_COLS],
        link_columns={"link_camara": st.column_config.LinkColumn("Câmara")},
    )
    download_csv(filtered_df[ULTIMA_TRAMITACAO_COLS], "ultima_tramitacao.csv")


def render_tramitacoes_acima_media(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Proposições com Tramitação Acima da Média")
    df = get_tramitacoes_acima_media(config_items)
    if not df.empty:
        chart_df = df.copy()
        chart_df["proposicao"] = (
            chart_df["Sigla_tipo"].fillna("")
            + " "
            + chart_df["numero"].astype(str)
            + "/"
            + chart_df["ano"].astype(str)
        )
        plot_bar(chart_df, "proposicao", "quantidade_tramitacoes", "Proposições mais movimentadas", top_n=10)
    show_dataframe(df)
    download_csv(df, "tramitacoes_acima_media.csv")
