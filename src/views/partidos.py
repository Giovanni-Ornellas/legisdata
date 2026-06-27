import pandas as pd
import streamlit as st

from src.components.charts import plot_bar
from src.components.tables import download_csv, show_dataframe
from src.services import get_ranking_partidos


def render_partidos(config_items: tuple[tuple[str, str], ...], filtered_df: pd.DataFrame) -> None:
    st.subheader("Ranking de Partidos")
    df = get_ranking_partidos(config_items)
    plot_bar(df, "partido", "quantidade_proposicoes", "Top partidos por proposições", top_n=10)
    show_dataframe(df)
    download_csv(df, "ranking_partidos.csv")

    st.markdown("#### Distribuição no recorte filtrado")
    rows = []
    for _, row in filtered_df.iterrows():
        for partido in str(row["partidos"]).split(","):
            partido = partido.strip()
            if partido and not partido.startswith("Sem "):
                rows.append(partido)

    if not rows:
        st.info("Não há partidos no recorte filtrado.")
        return

    local_df = (
        pd.Series(rows, name="partido")
        .value_counts()
        .reset_index(name="quantidade")
        .rename(columns={"index": "partido"})
    )
    plot_bar(local_df, "partido", "quantidade", "Partidos no recorte filtrado", top_n=10)
