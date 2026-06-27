import pandas as pd
import streamlit as st
from mysql.connector import Error as MySQLError

from src.database import connect_mysql, get_config_from_env, run_select_query


st.set_page_config(
    page_title="Analise Legislativa - Camara dos Deputados",
    layout="wide",
)


COUNT_QUERY = """
SELECT 'Proposicoes' AS metrica, COUNT(*) AS total FROM Proposicao
UNION ALL
SELECT 'Deputados' AS metrica, COUNT(*) AS total FROM Deputado
UNION ALL
SELECT 'Partidos' AS metrica, COUNT(*) AS total FROM Partido
UNION ALL
SELECT 'Temas' AS metrica, COUNT(*) AS total FROM Tema
UNION ALL
SELECT 'Tramitacoes' AS metrica, COUNT(*) AS total FROM Tramitacao
UNION ALL
SELECT 'Autorias' AS metrica, COUNT(*) AS total FROM Participa;
"""

RANKING_PARTIDOS_QUERY = """
SELECT
    pa.ID AS partido_id,
    pa.sigla AS partido,
    pa.nome AS nome_partido,
    COUNT(DISTINCT pr.ID) AS quantidade_proposicoes,
    COUNT(DISTINCT d.ID) AS quantidade_deputados_autores
FROM Partido pa
JOIN Deputado d
    ON d.fk_Partido_ID = pa.ID
JOIN Participa par
    ON par.fk_Deputado_ID = d.ID
JOIN Proposicao pr
    ON pr.ID = par.fk_Proposicao_ID
GROUP BY
    pa.ID,
    pa.sigla,
    pa.nome
ORDER BY
    quantidade_proposicoes DESC,
    partido ASC;
"""

RANKING_DEPUTADOS_QUERY = """
SELECT
    d.ID AS deputado_id,
    d.nome AS deputado,
    d.sigla_uf,
    pa.sigla AS partido,
    COUNT(DISTINCT pr.ID) AS quantidade_proposicoes_assinadas,
    SUM(CASE WHEN par.proponente = TRUE THEN 1 ELSE 0 END) AS quantidade_como_proponente
FROM Deputado d
JOIN Partido pa
    ON pa.ID = d.fk_Partido_ID
JOIN Participa par
    ON par.fk_Deputado_ID = d.ID
JOIN Proposicao pr
    ON pr.ID = par.fk_Proposicao_ID
GROUP BY
    d.ID,
    d.nome,
    d.sigla_uf,
    pa.sigla
ORDER BY
    quantidade_proposicoes_assinadas DESC,
    deputado ASC;
"""

PROPOSICOES_TEMAS_QUERY = """
SELECT
    pr.ID AS proposicao_id,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    COALESCE(GROUP_CONCAT(DISTINCT t.nome ORDER BY t.nome SEPARATOR ', '), 'Sem tema associado') AS temas
FROM Proposicao pr
LEFT JOIN Classificacao c
    ON c.fk_Proposicao_ID = pr.ID
LEFT JOIN Tema t
    ON t.Cod = c.fk_Tema_Cod
GROUP BY
    pr.ID,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa
ORDER BY
    pr.ano DESC,
    pr.numero DESC,
    pr.ID DESC;
"""

ULTIMA_TRAMITACAO_QUERY = """
SELECT
    pr.ID AS proposicao_id,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    tr.sequencia,
    tr.data_hora,
    tr.descricao_situacao,
    tr.descricao_tramitacao,
    o.sigla AS sigla_orgao,
    o.nome AS nome_orgao
FROM Proposicao pr
JOIN Tramitacao tr
    ON tr.fk_Proposicao_ID = pr.ID
    AND tr.sequencia = (
        SELECT MAX(tr2.sequencia)
        FROM Tramitacao tr2
        WHERE tr2.fk_Proposicao_ID = pr.ID
    )
LEFT JOIN Orgao o
    ON o.ID = tr.fk_Orgao_ID
ORDER BY
    tr.data_hora DESC,
    pr.ID DESC;
"""

TEMAS_ACIMA_MEDIA_QUERY = """
SELECT
    t.Cod AS tema_cod,
    t.nome AS tema,
    COUNT(DISTINCT c.fk_Proposicao_ID) AS quantidade_proposicoes
FROM Tema t
JOIN Classificacao c
    ON c.fk_Tema_Cod = t.Cod
GROUP BY
    t.Cod,
    t.nome
HAVING COUNT(DISTINCT c.fk_Proposicao_ID) > (
    SELECT AVG(media_temas.quantidade_por_tema)
    FROM (
        SELECT
            t2.Cod,
            COUNT(DISTINCT c2.fk_Proposicao_ID) AS quantidade_por_tema
        FROM Tema t2
        LEFT JOIN Classificacao c2
            ON c2.fk_Tema_Cod = t2.Cod
        GROUP BY
            t2.Cod
    ) AS media_temas
)
ORDER BY
    quantidade_proposicoes DESC,
    tema ASC;
"""

TRAMITACOES_ACIMA_MEDIA_QUERY = """
SELECT
    pr.ID AS proposicao_id,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    COUNT(tr.sequencia) AS quantidade_tramitacoes
FROM Proposicao pr
JOIN Tramitacao tr
    ON tr.fk_Proposicao_ID = pr.ID
GROUP BY
    pr.ID,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa
HAVING COUNT(tr.sequencia) > (
    SELECT AVG(media_tramitacoes.quantidade_por_proposicao)
    FROM (
        SELECT
            tr2.fk_Proposicao_ID,
            COUNT(*) AS quantidade_por_proposicao
        FROM Tramitacao tr2
        GROUP BY
            tr2.fk_Proposicao_ID
    ) AS media_tramitacoes
)
ORDER BY
    quantidade_tramitacoes DESC,
    pr.ano DESC,
    pr.numero DESC;
"""


def get_mysql_config() -> dict:
    if "mysql" in st.secrets:
        return dict(st.secrets["mysql"])
    return get_config_from_env()


@st.cache_resource(show_spinner=False)
def get_connection(config_items: tuple[tuple[str, str], ...]):
    config = dict(config_items)
    return connect_mysql(config)


@st.cache_data(ttl=300, show_spinner=False)
def load_data(query: str, config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    connection = get_connection(config_items)
    return run_select_query(connection, query)


def config_to_cache_key(config: dict) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((key, str(value)) for key, value in config.items()))


def query_df(query: str, config_items: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    return load_data(query, config_items)


def show_dataframe(df: pd.DataFrame, empty_message: str = "Nenhum registro encontrado.") -> None:
    if df.empty:
        st.info(empty_message)
        return
    st.dataframe(df, width="stretch", hide_index=True)


def show_bar_chart(df: pd.DataFrame, label_col: str, value_col: str, top_n: int = 10) -> None:
    if df.empty or label_col not in df or value_col not in df:
        st.info("Nao ha dados suficientes para o grafico.")
        return

    chart_df = df[[label_col, value_col]].head(top_n).copy()
    chart_df[value_col] = pd.to_numeric(chart_df[value_col], errors="coerce").fillna(0)
    chart_df = chart_df.set_index(label_col)
    st.bar_chart(chart_df, width="stretch")


def proposta_label(df: pd.DataFrame) -> pd.Series:
    return (
        df["Sigla_tipo"].fillna("")
        + " "
        + df["numero"].astype(str)
        + "/"
        + df["ano"].astype(str)
    )


def render_visao_geral(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Visao Geral")
    counts = query_df(COUNT_QUERY, config_items)
    if counts.empty:
        st.info("Nao foi possivel carregar as metricas do banco.")
        return

    values = dict(zip(counts["metrica"], counts["total"]))
    cols = st.columns(6)
    metrics = [
        ("Proposicoes", "Proposicoes"),
        ("Deputados", "Deputados"),
        ("Partidos", "Partidos"),
        ("Temas", "Temas"),
        ("Tramitacoes", "Tramitacoes"),
        ("Autorias", "Autorias"),
    ]
    for col, (label, key) in zip(cols, metrics):
        col.metric(label, int(values.get(key, 0)))

    st.caption("Contagens calculadas diretamente das tabelas do banco MySQL local.")


def render_ranking_partidos(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Ranking de Partidos")
    df = query_df(RANKING_PARTIDOS_QUERY, config_items)
    show_bar_chart(df, "partido", "quantidade_proposicoes", top_n=10)
    show_dataframe(df)


def render_ranking_deputados(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Ranking de Deputados")
    df = query_df(RANKING_DEPUTADOS_QUERY, config_items)
    show_bar_chart(df, "deputado", "quantidade_proposicoes_assinadas", top_n=10)
    show_dataframe(df)


def render_proposicoes_temas(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Proposicoes e Temas")
    df = query_df(PROPOSICOES_TEMAS_QUERY, config_items)
    if df.empty:
        show_dataframe(df)
        return

    tipos = sorted(df["Sigla_tipo"].dropna().unique().tolist())
    tipo = st.selectbox("Filtrar por tipo", ["Todos"] + tipos)
    filtered = df if tipo == "Todos" else df[df["Sigla_tipo"] == tipo]

    sem_tema = int((filtered["temas"] == "Sem tema associado").sum())
    st.caption(
        f"{sem_tema} proposicoes no filtro atual aparecem sem tema associado, preservadas pelo LEFT JOIN."
    )
    show_dataframe(filtered)


def render_ultima_tramitacao(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Ultima Tramitacao")
    df = query_df(ULTIMA_TRAMITACAO_QUERY, config_items)
    if df.empty:
        show_dataframe(df)
        return

    termo = st.text_input("Filtrar por ementa ou situacao", "")
    filtered = df
    if termo:
        termo_lower = termo.lower()
        filtered = df[
            df["ementa"].fillna("").str.lower().str.contains(termo_lower)
            | df["descricao_situacao"].fillna("").str.lower().str.contains(termo_lower)
        ]
    show_dataframe(filtered)


def render_temas_acima_media(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Temas Acima da Media")
    df = query_df(TEMAS_ACIMA_MEDIA_QUERY, config_items)
    show_bar_chart(df, "tema", "quantidade_proposicoes", top_n=10)
    show_dataframe(df)


def render_tramitacoes_acima_media(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Proposicoes com Tramitacao Acima da Media")
    df = query_df(TRAMITACOES_ACIMA_MEDIA_QUERY, config_items)
    if not df.empty:
        chart_df = df.copy()
        chart_df["proposicao"] = proposta_label(chart_df)
        show_bar_chart(chart_df, "proposicao", "quantidade_tramitacoes", top_n=10)
    show_dataframe(df)


def main() -> None:
    st.title("Analise Legislativa - Camara dos Deputados")
    st.write(
        "Dados coletados da API de Dados Abertos da Camara dos Deputados e organizados "
        "em um banco relacional MySQL para consulta e visualizacao."
    )

    try:
        config = get_mysql_config()
        config_items = config_to_cache_key(config)
        get_connection(config_items)
    except MySQLError as exc:
        st.error("Nao foi possivel conectar ao MySQL local.")
        st.caption(f"Detalhe tecnico: {exc}")
        st.stop()
    except Exception as exc:
        st.error("Falha ao carregar a configuracao de conexao.")
        st.caption(f"Detalhe tecnico: {exc}")
        st.stop()

    tabs = st.tabs(
        [
            "Visao Geral",
            "Ranking de Partidos",
            "Ranking de Deputados",
            "Proposicoes e Temas",
            "Ultima Tramitacao",
            "Temas Acima da Media",
            "Tramitacoes Acima da Media",
        ]
    )

    with tabs[0]:
        render_visao_geral(config_items)
    with tabs[1]:
        render_ranking_partidos(config_items)
    with tabs[2]:
        render_ranking_deputados(config_items)
    with tabs[3]:
        render_proposicoes_temas(config_items)
    with tabs[4]:
        render_ultima_tramitacao(config_items)
    with tabs[5]:
        render_temas_acima_media(config_items)
    with tabs[6]:
        render_tramitacoes_acima_media(config_items)


if __name__ == "__main__":
    main()
