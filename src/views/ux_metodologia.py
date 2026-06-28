import pandas as pd
import streamlit as st

from src.components.tables import show_dataframe
from src.services import get_qualidade_dados


def _percent(value: float) -> str:
    return f"{value:.1f}%"


def render_metodologia_ux(
    config_items: tuple[tuple[str, str], ...],
    base_df: pd.DataFrame,
) -> None:
    st.header("Metodologia dos Dados")
    st.write(
        "Esta página documenta a origem, o recorte e as limitações dos dados usados na aplicação."
    )

    st.markdown("### Fonte e modelagem")
    st.markdown(
        "- **Fonte:** API de Dados Abertos da Câmara dos Deputados.\n"
        "- **Banco:** MySQL relacional.\n"
        "- **Uso na aplicação:** somente leitura, sem alteração dos registros.\n"
        "- **Entidades principais:** Proposição, Deputado, Partido, Tema, Tramitação, Órgão, Participa e Classificação."
    )

    anos = sorted(int(ano) for ano in base_df["ano"].dropna().unique())
    periodo_inicio = base_df["data_apresentacao"].min()
    periodo_fim = base_df["data_apresentacao"].max()
    st.markdown("### Recorte carregado")
    st.markdown(
        f"- **Anos de proposição na base:** {', '.join(map(str, anos)) if anos else 'não informado'}.\n"
        f"- **Período de apresentação:** "
        f"{periodo_inicio.strftime('%d/%m/%Y') if pd.notna(periodo_inicio) else 'não informado'} "
        f"a {periodo_fim.strftime('%d/%m/%Y') if pd.notna(periodo_fim) else 'não informado'}.\n"
        "- **Observação:** o campo `ano` vem da proposição na API, enquanto `data_apresentacao` é uma data específica."
    )

    qualidade = get_qualidade_dados(config_items)
    if qualidade.empty:
        st.info("Não foi possível calcular os indicadores de qualidade.")
        return

    row = qualidade.iloc[0]
    st.markdown("### Indicadores de qualidade")
    col1, col2, col3 = st.columns(3)
    col1.metric("Cobertura temática", _percent(float(row["cobertura_tematica_percentual"])))
    col2.metric("Cobertura de autoria", _percent(float(row["cobertura_autoria_percentual"])))
    col3.metric("Cobertura de tramitação", _percent(float(row["cobertura_tramitacao_percentual"])))

    col4, col5, col6 = st.columns(3)
    col4.metric("Sem tema", int(row["proposicoes_sem_tema"]))
    col5.metric("Sem tramitação", int(row["proposicoes_sem_tramitacao"]))
    col6.metric("Sem autores identificados", int(row["proposicoes_sem_autores"]))

    st.markdown("### Tabelas populadas")
    tabelas = pd.DataFrame(
        [
            {"tabela": "Partido", "finalidade": "Identificar partidos políticos."},
            {"tabela": "Orgao", "finalidade": "Representar órgãos e comissões relacionados às tramitações."},
            {"tabela": "Tema", "finalidade": "Classificar assuntos legislativos."},
            {"tabela": "Proposicao", "finalidade": "Armazenar proposições legislativas."},
            {"tabela": "Deputado", "finalidade": "Armazenar parlamentares identificados na API."},
            {"tabela": "Tramitacao", "finalidade": "Registrar movimentações das proposições."},
            {"tabela": "Participa", "finalidade": "Relacionar deputados e proposições como autoria/participação."},
            {"tabela": "Classificacao", "finalidade": "Relacionar proposições e temas."},
        ]
    )
    show_dataframe(tabelas)

    st.markdown("### Limitações")
    st.markdown(
        "- Algumas proposições não possuem tema associado.\n"
        "- Algumas proposições podem não ter autores deputados identificados.\n"
        "- Campos nulos vêm da própria fonte ou do recorte de coleta.\n"
        "- A aplicação não consulta a API em tempo real; ela usa o banco já populado.\n"
        "- Os gráficos não representam interpretação jurídica ou política automática."
    )
