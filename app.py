import streamlit as st
from mysql.connector import Error as MySQLError

from src.components.errors import render_app_error, render_connection_error, render_empty_database_message
from src.components.filters import apply_sidebar_filters
from src.components.layout import apply_global_style
from src.services import config_to_cache_key, get_base_proposicoes, get_connection, get_mysql_config
from src.views.deputado_detalhado import render_deputado_detalhado
from src.views.deputados import render_deputados
from src.views.entenda_proposicao import render_entenda_proposicao
from src.views.espectro import render_espectro
from src.views.glossario import render_glossario
from src.views.home import render_home
from src.views.metodologia_dados import render_metodologia_dados
from src.views.orgaos import render_orgaos
from src.views.partidos import render_partidos
from src.views.proposicoes import render_explorar, render_proposicoes_temas
from src.views.qualidade_dados import render_qualidade_dados
from src.views.temas import render_temas_acima_media
from src.views.tramitacoes import render_tramitacoes_acima_media, render_ultima_tramitacao


PAGE_GROUPS = {
    "Panorama": [
        "Visão Geral",
        "Qualidade dos Dados",
        "Metodologia dos Dados",
    ],
    "Proposições": [
        "Entenda uma Proposição",
        "Proposições e Temas",
        "Temas Acima da Média",
        "Explorar",
    ],
    "Parlamentares e Partidos": [
        "Ranking de Partidos",
        "Ranking de Deputados",
        "Deputado Detalhado",
        "Espectro Político",
    ],
    "Tramitação e Órgãos": [
        "Última Tramitação",
        "Tramitações Acima da Média",
        "Órgãos",
    ],
    "Apoio": [
        "Glossário",
    ],
}


st.set_page_config(
    page_title="Análise Legislativa - Câmara dos Deputados",
    layout="wide",
)
apply_global_style()


def render_header() -> None:
    st.title("Análise Legislativa - Câmara dos Deputados")
    st.write(
        "Dados coletados da API de Dados Abertos da Câmara dos Deputados e organizados "
        "em um banco relacional MySQL para consulta e visualização."
    )


def load_app_data() -> tuple[tuple[tuple[str, str], ...], object]:
    config = get_mysql_config()
    config_items = config_to_cache_key(config)
    get_connection(config_items)
    base_df = get_base_proposicoes(config_items)
    return config_items, base_df


def select_page() -> str:
    st.sidebar.header("Navegação")
    group = st.sidebar.radio("Grupo de páginas", list(PAGE_GROUPS.keys()))
    return st.sidebar.radio("Página", PAGE_GROUPS[group])


def render_page(config_items: tuple[tuple[str, str], ...], base_df) -> None:
    if base_df.empty:
        render_empty_database_message()

    page = select_page()
    filtered_df = apply_sidebar_filters(base_df)

    if page == "Visão Geral":
        render_home(config_items, base_df, filtered_df)
    elif page == "Qualidade dos Dados":
        render_qualidade_dados(config_items)
    elif page == "Metodologia dos Dados":
        render_metodologia_dados(base_df)
    elif page == "Entenda uma Proposição":
        render_entenda_proposicao(config_items, base_df, filtered_df)
    elif page == "Ranking de Partidos":
        render_partidos(config_items, filtered_df)
    elif page == "Ranking de Deputados":
        render_deputados(config_items)
    elif page == "Deputado Detalhado":
        render_deputado_detalhado(config_items)
    elif page == "Órgãos":
        render_orgaos(config_items)
    elif page == "Proposições e Temas":
        render_proposicoes_temas(filtered_df)
    elif page == "Última Tramitação":
        render_ultima_tramitacao(filtered_df)
    elif page == "Temas Acima da Média":
        render_temas_acima_media(config_items, filtered_df)
    elif page == "Tramitações Acima da Média":
        render_tramitacoes_acima_media(config_items)
    elif page == "Explorar":
        render_explorar(filtered_df)
    elif page == "Espectro Político":
        render_espectro(filtered_df)
    elif page == "Glossário":
        render_glossario()


def main() -> None:
    render_header()
    try:
        config_items, base_df = load_app_data()
    except MySQLError as exc:
        render_connection_error(exc)
        return
    except Exception as exc:
        render_app_error(exc)
        return

    render_page(config_items, base_df)


if __name__ == "__main__":
    main()
