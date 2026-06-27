import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.tables import download_csv, show_dataframe
from src.services import get_temas_acima_media


def render_temas_acima_media(config_items: tuple[tuple[str, str], ...], filtered_df: pd.DataFrame) -> None:
    st.subheader("Temas Acima da Média")
    df = get_temas_acima_media(config_items)
    plot_bar(df, "tema", "quantidade_proposicoes", "Temas acima da média", top_n=10)
    show_dataframe(df)
    download_csv(df, "temas_acima_media.csv")

    st.markdown("#### Temas no recorte filtrado")
    tema_rows = []
    for value in filtered_df["temas"]:
        for tema in str(value).split(","):
            tema = tema.strip()
            if tema and not tema.startswith("Sem "):
                tema_rows.append(tema)

    if not tema_rows:
        st.info("Não há temas associados no recorte filtrado.")
        return

    local_df = (
        pd.Series(tema_rows, name="tema")
        .value_counts()
        .reset_index(name="quantidade")
        .rename(columns={"index": "tema"})
    )
    plot_bar(local_df, "tema", "quantidade", "Temas mais frequentes no recorte", top_n=12, horizontal=True)
