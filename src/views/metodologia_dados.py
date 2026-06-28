import pandas as pd
import streamlit as st

from src.components.help_text import render_help_box


def _date_range_text(df: pd.DataFrame) -> str:
    if df.empty or df["data_apresentacao"].dropna().empty:
        return "período não identificado"
    start = df["data_apresentacao"].min().strftime("%d/%m/%Y")
    end = df["data_apresentacao"].max().strftime("%d/%m/%Y")
    return f"{start} a {end}"


def render_metodologia_dados(base_df: pd.DataFrame) -> None:
    st.subheader("Metodologia dos Dados")
    render_help_box(
        "Objetivo da metodologia",
        "Esta seção resume a origem, o recorte e as limitações dos dados usados na aplicação, para apoiar a apresentação acadêmica do trabalho.",
    )

    anos = sorted(base_df["ano"].dropna().astype(int).unique().tolist()) if not base_df.empty else []
    st.markdown("### Fonte e recorte")
    st.markdown(
        "- **Fonte:** API de Dados Abertos da Câmara dos Deputados.\n"
        "- **Banco:** MySQL, com dados organizados em tabelas relacionais.\n"
        f"- **Ano(s) carregado(s):** {', '.join(map(str, anos)) if anos else 'não identificado'}.\n"
        f"- **Período de apresentação no banco:** {_date_range_text(base_df)}.\n"
        f"- **Quantidade de proposições no recorte atual:** {base_df['proposicao_id'].nunique() if not base_df.empty else 0}."
    )

    st.markdown("### Tabelas utilizadas")
    st.markdown(
        "`Partido`, `Orgao`, `Tema`, `Proposicao`, `Deputado`, `Tramitacao`, `Participa` e `Classificacao`."
    )

    st.markdown("### Possíveis lacunas")
    st.markdown(
        "- Algumas proposições podem aparecer sem tema associado.\n"
        "- Algumas proposições podem não ter tramitações carregadas.\n"
        "- Autores que não eram deputados foram ignorados no processo de carga para preservar a relação com a tabela `Deputado`.\n"
        "- Campos nulos ou ausentes podem vir da própria fonte de dados.\n"
        "- O banco representa o recorte coletado pelo grupo, não todo o universo legislativo da Câmara."
    )

    st.warning(
        "A aplicação apresenta os registros disponíveis no banco e não interpreta consequências jurídicas, políticas ou regimentais."
    )
