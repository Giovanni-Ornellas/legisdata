import streamlit as st
from mysql.connector import Error as MySQLError

from src.components.errors import render_app_error, render_connection_error, render_empty_database_message
from src.components.filters import apply_sidebar_filters
from src.components.layout import apply_global_style
from src.services import config_to_cache_key, get_base_proposicoes, get_connection, get_mysql_config
from src.views.deputado_detalhado import render_deputado_detalhado
from src.views.ux_deputados_partidos import render_deputados_partidos_ux
from src.views.ux_explorar_proposicoes import render_explorar_proposicoes_ux
from src.views.ux_metodologia import render_metodologia_ux
from src.views.ux_temas_tramitacoes import render_temas_tramitacoes_ux
from src.views.ux_visao_geral import render_visao_geral_ux


PAGES = [
    "Visão Geral",
    "Explorar Proposições",
    "Deputados e Partidos",
    "Perfil do Deputado",
    "Temas e Tramitações",
    "Metodologia dos Dados",
]


st.set_page_config(
    page_title="Análise Legislativa - Câmara dos Deputados",
    layout="wide",
)
apply_global_style()


def render_header() -> None:
    st.markdown(
        """
        <div class="legis-hero">
            <div class="legis-eyebrow">Dados legislativos da Câmara dos Deputados</div>
            <h1>LegisData</h1>
            <p class="legis-subtitle">
                Acompanhe proposições, autores, partidos, temas e tramitações em uma interface
                de consulta pública construída sobre um banco relacional MySQL.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_app_data() -> tuple[tuple[tuple[str, str], ...], object]:
    config = get_mysql_config()
    config_items = config_to_cache_key(config)
    get_connection(config_items)
    base_df = get_base_proposicoes(config_items)
    return config_items, base_df


def select_page() -> str:
    st.sidebar.markdown('<div class="legis-sidebar-title">LegisData</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="legis-sidebar-caption">Use a navegação e os filtros para acompanhar o recorte legislativo.</div>',
        unsafe_allow_html=True,
    )
    return st.sidebar.radio("Página", PAGES)


def render_page(config_items: tuple[tuple[str, str], ...], base_df) -> None:
    if base_df.empty:
        render_empty_database_message()

    page = select_page()
    st.sidebar.divider()
    filtered_df = apply_sidebar_filters(base_df)

    if page == "Visão Geral":
        render_visao_geral_ux(config_items, base_df, filtered_df)
    elif page == "Explorar Proposições":
        render_explorar_proposicoes_ux(config_items, filtered_df)
    elif page == "Deputados e Partidos":
        render_deputados_partidos_ux(config_items, filtered_df)
    elif page == "Perfil do Deputado":
        render_deputado_detalhado(config_items)
    elif page == "Temas e Tramitações":
        render_temas_tramitacoes_ux(config_items, filtered_df)
    elif page == "Metodologia dos Dados":
        render_metodologia_ux(config_items, base_df)


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
