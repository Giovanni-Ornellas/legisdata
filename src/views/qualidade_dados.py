import pandas as pd
import streamlit as st

from src.components.help_text import render_help_box
from src.components.tables import show_dataframe
from src.services import get_qualidade_dados


def _metric_percent(value) -> str:
    if pd.isna(value):
        return "0,0%"
    return f"{float(value):.1f}%".replace(".", ",")


def render_qualidade_dados(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Qualidade dos Dados")
    render_help_box(
        "Por que olhar a qualidade dos dados?",
        "Estes indicadores mostram a cobertura do banco carregado. Eles ajudam a explicar lacunas naturais da fonte ou do processo de coleta, como proposições sem tema, sem tramitação ou sem autor identificado.",
    )

    df = get_qualidade_dados(config_items)
    if df.empty:
        st.info("Não foi possível calcular os indicadores de qualidade.")
        return

    row = df.iloc[0]
    cols = st.columns(3)
    cols[0].metric("Total de proposições", int(row["total_proposicoes"]))
    cols[1].metric("Relações em Participa", int(row["total_participa"]))
    cols[2].metric("Relações em Classificação", int(row["total_classificacao"]))

    cols = st.columns(3)
    cols[0].metric("Cobertura temática", _metric_percent(row["cobertura_tematica_percentual"]))
    cols[1].metric("Cobertura de autoria", _metric_percent(row["cobertura_autoria_percentual"]))
    cols[2].metric("Cobertura de tramitação", _metric_percent(row["cobertura_tramitacao_percentual"]))

    st.markdown("### Lacunas identificadas")
    lacunas = pd.DataFrame(
        [
            {
                "indicador": "Proposições sem tema",
                "total": int(row["proposicoes_sem_tema"]),
                "significado": "Registros sem classificação temática associada no banco.",
            },
            {
                "indicador": "Proposições sem tramitação",
                "total": int(row["proposicoes_sem_tramitacao"]),
                "significado": "Registros sem movimentações carregadas na tabela Tramitacao.",
            },
            {
                "indicador": "Proposições sem autores identificados",
                "total": int(row["proposicoes_sem_autores"]),
                "significado": "Registros sem deputados associados na tabela Participa.",
            },
        ]
    )
    show_dataframe(lacunas)

    with st.expander("Como interpretar estes indicadores?"):
        st.markdown(
            "- **Proposições sem tema** podem ocorrer quando a API não informa classificação temática ou quando ela não foi retornada na coleta.\n"
            "- **Proposições sem tramitação** indicam ausência de histórico de movimentação carregado para a proposição.\n"
            "- **Proposições sem autores identificados** indicam ausência de deputados associados no banco; autores que não eram deputados foram ignorados na carga.\n"
            "- As coberturas percentuais mostram a proporção de proposições com tema, autoria ou tramitação disponível."
        )
