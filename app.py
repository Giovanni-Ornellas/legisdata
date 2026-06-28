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


def render_tabs(config_items: tuple[tuple[str, str], ...], base_df) -> None:
    if base_df.empty:
        render_empty_database_message()

    filtered_df = apply_sidebar_filters(base_df)
    tabs = st.tabs(
        [
            "Visão Geral",
            "Qualidade dos Dados",
            "Metodologia dos Dados",
            "Entenda uma Proposição",
            "Ranking de Partidos",
            "Ranking de Deputados",
            "Deputado Detalhado",
            "Órgãos",
            "Proposições e Temas",
            "Última Tramitação",
            "Temas Acima da Média",
            "Tramitações Acima da Média",
            "Explorar",
            "Espectro Político",
            "Glossário",
        ]
    )

    with tabs[0]:
        render_home(config_items, base_df, filtered_df)
    with tabs[1]:
        render_qualidade_dados(config_items)
    with tabs[2]:
        render_metodologia_dados(base_df)
    with tabs[3]:
        render_entenda_proposicao(config_items, filtered_df)
    with tabs[4]:
        render_partidos(config_items, filtered_df)
    with tabs[5]:
        render_deputados(config_items)
    with tabs[6]:
        render_deputado_detalhado(config_items)
    with tabs[7]:
        render_orgaos(config_items)
    with tabs[8]:
        render_proposicoes_temas(filtered_df)
    with tabs[9]:
        render_ultima_tramitacao(filtered_df)
    with tabs[10]:
        render_temas_acima_media(config_items, filtered_df)
    with tabs[11]:
        render_tramitacoes_acima_media(config_items)
    with tabs[12]:
        render_explorar(filtered_df)
    with tabs[13]:
        render_espectro(filtered_df)
    with tabs[14]:
        render_glossario()


def main() -> None:
    render_header()
    try:
        config_items, base_df = load_app_data()
    except MySQLError as exc:
        render_connection_error(exc)
    except Exception as exc:
        render_app_error(exc)

    render_tabs(config_items, base_df)


if __name__ == "__main__":
    main()
