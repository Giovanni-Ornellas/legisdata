import pandas as pd
import streamlit as st

from src.database import connect_mysql, get_config_from_env, run_select_query
from src.queries import (
    BASE_PROPOSICOES_QUERY,
    COUNT_QUERY,
    RANKING_DEPUTADOS_QUERY,
    RANKING_PARTIDOS_QUERY,
    TEMAS_ACIMA_MEDIA_QUERY,
    TRAMITACOES_ACIMA_MEDIA_QUERY,
    TRAMITACOES_PROPOSICAO_QUERY,
)


def get_mysql_config() -> dict:
    if "mysql" in st.secrets:
        return dict(st.secrets["mysql"])
    return get_config_from_env()


def config_to_cache_key(config: dict) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((key, str(value)) for key, value in config.items()))


@st.cache_resource(show_spinner=False)
def get_connection(config_items: tuple[tuple[str, str], ...]):
    return connect_mysql(dict(config_items))


@st.cache_data(ttl=300, show_spinner=False)
def load_data(query: str, config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    connection = get_connection(config_items)
    return run_select_query(connection, query)


@st.cache_data(ttl=300, show_spinner=False)
def load_data_with_params(
    query: str,
    params: tuple,
    config_items: tuple[tuple[str, str], ...],
) -> pd.DataFrame:
    connection = get_connection(config_items)
    return run_select_query(connection, query, params)


def prepare_base(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["data_apresentacao", "data_ultima_tramitacao"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["mes_apresentacao"] = df["data_apresentacao"].dt.to_period("M").astype(str)
    return df


def get_counts(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return load_data(COUNT_QUERY, config_items)


def get_base_proposicoes(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return prepare_base(load_data(BASE_PROPOSICOES_QUERY, config_items))


def get_ranking_partidos(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return load_data(RANKING_PARTIDOS_QUERY, config_items)


def get_ranking_deputados(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return load_data(RANKING_DEPUTADOS_QUERY, config_items)


def get_temas_acima_media(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return load_data(TEMAS_ACIMA_MEDIA_QUERY, config_items)


def get_tramitacoes_acima_media(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return load_data(TRAMITACOES_ACIMA_MEDIA_QUERY, config_items)


def get_tramitacoes_proposicao(config_items: tuple[tuple[str, str], ...], proposicao_id: int) -> pd.DataFrame:
    return load_data_with_params(TRAMITACOES_PROPOSICAO_QUERY, (int(proposicao_id),), config_items)
