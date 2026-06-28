import pandas as pd
import streamlit as st

from src.database import connect_mysql, get_config_from_env, run_select_query
from src.queries import (
    BASE_PROPOSICOES_QUERY,
    COUNT_QUERY,
    DEPUTADOS_QUERY,
    DEPUTADO_PROPOSICOES_QUERY,
    DEPUTADO_TEMAS_QUERY,
    ORGAOS_QUERY,
    ORGAOS_RANKING_QUERY,
    ORGAO_PROPOSICOES_QUERY,
    QUALIDADE_DADOS_QUERY,
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


def get_qualidade_dados(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    df = load_data(QUALIDADE_DADOS_QUERY, config_items)
    if df.empty:
        return df

    df = df.copy()
    total = int(df.loc[0, "total_proposicoes"] or 0)
    if total == 0:
        df["cobertura_tematica_percentual"] = 0.0
        df["cobertura_autoria_percentual"] = 0.0
        df["cobertura_tramitacao_percentual"] = 0.0
        return df

    df["cobertura_tematica_percentual"] = 100 * (total - df["proposicoes_sem_tema"]) / total
    df["cobertura_autoria_percentual"] = 100 * (total - df["proposicoes_sem_autores"]) / total
    df["cobertura_tramitacao_percentual"] = 100 * (total - df["proposicoes_sem_tramitacao"]) / total
    return df


def get_orgaos(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return load_data(ORGAOS_QUERY, config_items)


def get_ranking_orgaos(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return load_data(ORGAOS_RANKING_QUERY, config_items)


def get_proposicoes_por_orgao(config_items: tuple[tuple[str, str], ...], orgao_id: int) -> pd.DataFrame:
    return load_data_with_params(ORGAO_PROPOSICOES_QUERY, (int(orgao_id),), config_items)


def get_deputados(config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return load_data(DEPUTADOS_QUERY, config_items)


def get_proposicoes_deputado(config_items: tuple[tuple[str, str], ...], deputado_id: int) -> pd.DataFrame:
    return load_data_with_params(DEPUTADO_PROPOSICOES_QUERY, (int(deputado_id),), config_items)


def get_temas_deputado(config_items: tuple[tuple[str, str], ...], deputado_id: int) -> pd.DataFrame:
    return load_data_with_params(DEPUTADO_TEMAS_QUERY, (int(deputado_id),), config_items)
