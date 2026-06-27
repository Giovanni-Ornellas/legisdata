import pandas as pd
import streamlit as st

from src.components.tables import show_dataframe
from src.content.glossario import GLOSSARIO


def render_glossario() -> None:
    st.subheader("Glossário Legislativo")
    st.write(
        "Este glossário reúne termos que aparecem nos dados da Câmara. "
        "As explicações são curtas e servem apenas para apoiar a leitura da aplicação."
    )

    termo_busca = st.text_input("Buscar termo no glossário")
    df = pd.DataFrame(GLOSSARIO)
    if termo_busca:
        termo = termo_busca.lower()
        df = df[
            df["termo"].str.lower().str.contains(termo, regex=False)
            | df["explicacao"].str.lower().str.contains(termo, regex=False)
        ]

    for item in df.to_dict("records"):
        with st.expander(item["termo"]):
            st.markdown(item["explicacao"])
            st.caption(f"Exemplo: {item['exemplo']}")

    st.markdown("### Tabela resumida")
    show_dataframe(df)
