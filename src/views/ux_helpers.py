from __future__ import annotations

import pandas as pd
import streamlit as st

from src.components.filters import contains_any_csv_value, split_values


def show_sql(query: str, caption: str = "Consulta SQL utilizada") -> None:
    with st.expander(caption):
        st.code(query.strip(), language="sql")


def filter_proposicoes(df: pd.DataFrame, key_prefix: str = "proposicoes") -> pd.DataFrame:
    st.markdown("### Filtros")
    col1, col2, col3 = st.columns(3)
    termo = col1.text_input(
        "Texto da ementa",
        placeholder="Ex.: educação, saúde, escala 6x1",
        key=f"{key_prefix}_termo",
    )
    anos = col2.multiselect(
        "Ano da proposição",
        sorted(df["ano"].dropna().unique(), reverse=True),
        key=f"{key_prefix}_anos",
    )
    tipos = col3.multiselect(
        "Tipo de proposição",
        sorted(df["Sigla_tipo"].dropna().unique()),
        key=f"{key_prefix}_tipos",
    )

    col4, col5, col6 = st.columns(3)
    temas = col4.multiselect("Tema tratado", split_values(df["temas"]), key=f"{key_prefix}_temas")
    partidos = col5.multiselect("Partido do autor", split_values(df["partidos"]), key=f"{key_prefix}_partidos")
    deputados = col6.multiselect("Deputado autor", split_values(df["autores"]), key=f"{key_prefix}_deputados")

    filtered = df.copy()
    if termo:
        termo_lower = termo.lower()
        filtered = filtered[
            filtered["ementa"].fillna("").str.lower().str.contains(termo_lower, regex=False)
            | filtered["proposicao"].fillna("").str.lower().str.contains(termo_lower, regex=False)
            | filtered["descricao_tipo"].fillna("").str.lower().str.contains(termo_lower, regex=False)
        ]
    if anos:
        filtered = filtered[filtered["ano"].isin(anos)]
    if tipos:
        filtered = filtered[filtered["Sigla_tipo"].isin(tipos)]
    if temas:
        filtered = filtered[filtered["temas"].apply(lambda value: contains_any_csv_value(value, temas))]
    if partidos:
        filtered = filtered[filtered["partidos"].apply(lambda value: contains_any_csv_value(value, partidos))]
    if deputados:
        filtered = filtered[filtered["autores"].apply(lambda value: contains_any_csv_value(value, deputados))]

    st.caption(f"{len(filtered)} proposição(ões) encontrada(s) no recorte atual.")
    return filtered.sort_values(["data_apresentacao", "proposicao_id"], ascending=[False, False])


def build_proposicao_options(df: pd.DataFrame) -> dict[int, str]:
    return {
        int(row.proposicao_id): f"{row.proposicao} · {str(row.ementa)[:110]}"
        for row in df.itertuples()
    }
