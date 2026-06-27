import streamlit as st
from mysql.connector import Error as MySQLError

from src.components.filters import apply_sidebar_filters
from src.services import config_to_cache_key, get_base_proposicoes, get_connection, get_mysql_config
from src.views.deputados import render_deputados
from src.views.espectro import render_espectro
from src.views.home import render_home
from src.views.partidos import render_partidos
from src.views.proposicoes import render_explorar, render_proposicoes_temas
from src.views.temas import render_temas_acima_media
from src.views.tramitacoes import render_tramitacoes_acima_media, render_ultima_tramitacao


st.set_page_config(
    page_title="Análise Legislativa - Câmara dos Deputados",
    layout="wide",
)


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


def render_connection_error(exc: Exception) -> None:
    st.error("Não foi possível conectar ao MySQL configurado.")
    st.info(
        "Se a aplicação estiver no Streamlit Cloud, configure os dados do Aiven "
        "em App settings > Secrets. Sem esses secrets, o app tenta usar o MySQL local."
    )
    st.caption(f"Detalhe técnico: {exc}")
    st.stop()


def render_tabs(config_items: tuple[tuple[str, str], ...], base_df) -> None:
    if base_df.empty:
        st.warning("Não há proposições carregadas no banco.")
        st.stop()

    filtered_df = apply_sidebar_filters(base_df)
    tabs = st.tabs(
        [
            "Visão Geral",
            "Ranking de Partidos",
            "Ranking de Deputados",
            "Proposições e Temas",
            "Última Tramitação",
            "Temas Acima da Média",
            "Tramitações Acima da Média",
            "Explorar",
            "Espectro Político",
        ]
    )

    with tabs[0]:
        render_home(config_items, base_df, filtered_df)
    with tabs[1]:
        render_partidos(config_items, filtered_df)
    with tabs[2]:
        render_deputados(config_items)
    with tabs[3]:
        render_proposicoes_temas(filtered_df)
    with tabs[4]:
        render_ultima_tramitacao(filtered_df)
    with tabs[5]:
        render_temas_acima_media(config_items, filtered_df)
    with tabs[6]:
        render_tramitacoes_acima_media(config_items)
    with tabs[7]:
        render_explorar(filtered_df)
    with tabs[8]:
        render_espectro(filtered_df)


def main() -> None:
    render_header()
    try:
        config_items, base_df = load_app_data()
    except MySQLError as exc:
        render_connection_error(exc)
    except Exception as exc:
        st.error("Falha ao carregar a configuração de conexão.")
        st.caption(f"Detalhe técnico: {exc}")
        st.stop()

    render_tabs(config_items, base_df)


if __name__ == "__main__":
    main()
