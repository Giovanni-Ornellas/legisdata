import pandas as pd
import streamlit as st

from src.components.charts import plot_spectrum_bar, plot_spectrum_treemap


SPECTRUM_MAP = {
    "AGIR": "Centro-Direita",
    "AVANTE": "Centro",
    "CIDADANIA": "Centro-Esquerda",
    "MDB": "Centro",
    "NOVO": "Direita",
    "PCdoB": "Esquerda",
    "PDT": "Centro-Esquerda",
    "PL": "Direita",
    "PODE": "Visão Independente",
    "PP": "Centro-Direita",
    "PRD": "Centro-Direita",
    "PSB": "Centro-Esquerda",
    "PSD": "Centro",
    "PSDB": "Centro",
    "PSOL": "Esquerda",
    "PT": "Esquerda",
    "PV": "Centro-Esquerda",
    "REDE": "Esquerda",
    "REPUBLICANOS": "Direita",
    "SOLIDARIEDADE": "Centro",
    "UNIÃO": "Centro-Direita",
}


def render_espectro(filtered_df: pd.DataFrame) -> None:
    st.subheader("Distribuição por Espectro Político")
    rows = []
    for _, row in filtered_df.iterrows():
        for partido in str(row["partidos"]).split(","):
            partido = partido.strip()
            if partido and not partido.startswith("Sem "):
                rows.append(
                    {
                        "partido": partido,
                        "espectro": SPECTRUM_MAP.get(partido, "Não atribuído"),
                        "quantidade": 1,
                    }
                )

    if not rows:
        st.info("Não há partidos no recorte filtrado.")
        return

    df = pd.DataFrame(rows).groupby(["espectro", "partido"], as_index=False)["quantidade"].sum()
    tab_tree, tab_bar = st.tabs(["Mapa de árvore", "Barras"])
    with tab_tree:
        plot_spectrum_treemap(df)
    with tab_bar:
        plot_spectrum_bar(df)
