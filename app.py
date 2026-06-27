import pandas as pd
import plotly.express as px
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

BASE_PROPOSICOES_QUERY = """
SELECT
    pr.ID AS proposicao_id,
    CONCAT(pr.Sigla_tipo, ' ', pr.numero, '/', pr.ano) AS proposicao,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    pr.data_apresentacao,
    pr.descricao_tipo,
    COALESCE(temas.temas, 'Sem tema associado') AS temas,
    COALESCE(autores.autores, 'Sem deputado identificado') AS autores,
    COALESCE(autores.partidos, 'Sem partido identificado') AS partidos,
    COALESCE(autores.quantidade_autores, 0) AS quantidade_autores,
    COALESCE(tram.total_tramitacoes, 0) AS quantidade_tramitacoes,
    ult.data_hora AS data_ultima_tramitacao,
    ult.descricao_situacao,
    ult.descricao_tramitacao,
    o.sigla AS sigla_orgao,
    o.nome AS nome_orgao,
    CONCAT(
        'https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=',
        pr.ID
    ) AS link_camara
FROM Proposicao pr
LEFT JOIN (
    SELECT
        c.fk_Proposicao_ID,
        GROUP_CONCAT(DISTINCT t.nome ORDER BY t.nome SEPARATOR ', ') AS temas
    FROM Classificacao c
    JOIN Tema t
        ON t.Cod = c.fk_Tema_Cod
    GROUP BY
        c.fk_Proposicao_ID
) temas
    ON temas.fk_Proposicao_ID = pr.ID
LEFT JOIN (
    SELECT
        par.fk_Proposicao_ID,
        GROUP_CONCAT(DISTINCT d.nome ORDER BY par.ordem_assinatura SEPARATOR ', ') AS autores,
        GROUP_CONCAT(DISTINCT pa.sigla ORDER BY pa.sigla SEPARATOR ', ') AS partidos,
        COUNT(DISTINCT d.ID) AS quantidade_autores
    FROM Participa par
    JOIN Deputado d
        ON d.ID = par.fk_Deputado_ID
    LEFT JOIN Partido pa
        ON pa.ID = d.fk_Partido_ID
    GROUP BY
        par.fk_Proposicao_ID
) autores
    ON autores.fk_Proposicao_ID = pr.ID
LEFT JOIN (
    SELECT
        fk_Proposicao_ID,
        COUNT(*) AS total_tramitacoes
    FROM Tramitacao
    GROUP BY
        fk_Proposicao_ID
) tram
    ON tram.fk_Proposicao_ID = pr.ID
LEFT JOIN Tramitacao ult
    ON ult.fk_Proposicao_ID = pr.ID
    AND ult.sequencia = (
        SELECT MAX(t2.sequencia)
        FROM Tramitacao t2
        WHERE t2.fk_Proposicao_ID = pr.ID
    )
LEFT JOIN Orgao o
    ON o.ID = ult.fk_Orgao_ID
ORDER BY
    pr.data_apresentacao DESC,
    pr.ID DESC;
"""

SPECTRUM_MAP = {
    "AGIR": "Centro-Direita",
    "AVANTE": "Centro",
    "CIDADANIA": "Centro-Esquerda",
    "MDB": "Centro",
    "NOVO": "Direita",
    "PCdoB": "Esquerda",
    "PDT": "Centro-Esquerda",
    "PL": "Direita",
    "PODE": "Visao Independente",
    "PP": "Centro-Direita",
    "PRD": "Centro-Direita",
    "PSB": "Centro-Esquerda",
    "PSD": "Centro",
    "PSDB": "Centro",
    "PSOL": "Esquerda",
    "PT": "Esquerda",
    "PV": "Centro-Esquerda",
    "REDE": "Esquerda",
    "REPUBLICANOS": "Direita",
    "SOLIDARIEDADE": "Centro",
    "UNIÃO": "Centro-Direita",
}

SPECTRUM_COLORS = {
    "Nao atribuido": "#B8B8B8",
    "Esquerda": "#C43C39",
    "Centro-Esquerda": "#E68A70",
    "Centro": "#8C7AA9",
    "Centro-Direita": "#5F8CCB",
    "Direita": "#2457A6",
    "Visao Independente": "#6D6D6D",
}


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


def show_dataframe(
    df: pd.DataFrame,
    empty_message: str = "Nenhum registro encontrado.",
    link_columns: dict | None = None,
) -> None:
    if df.empty:
        st.info(empty_message)
        return
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config=link_columns,
    )


def download_csv(df: pd.DataFrame, filename: str) -> None:
    if df.empty:
        return
    st.download_button(
        "Baixar CSV",
        df.to_csv(index=False).encode("utf-8"),
        filename,
        "text/csv",
    )


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str, top_n: int = 10, horizontal: bool = False) -> None:
    if df.empty or x not in df or y not in df:
        st.info("Nao ha dados suficientes para o grafico.")
        return
    chart_df = df.head(top_n).copy()
    if horizontal:
        fig = px.bar(chart_df, x=y, y=x, orientation="h", title=title, text=y)
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
    else:
        fig = px.bar(chart_df, x=x, y=y, title=title, text=y)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
    st.plotly_chart(fig, width="stretch")


def split_values(series: pd.Series) -> list[str]:
    values: set[str] = set()
    for item in series.dropna():
        for part in str(item).split(","):
            part = part.strip()
            if part and not part.startswith("Sem "):
                values.add(part)
    return sorted(values)


def contains_any_csv_value(cell: str, selected: list[str]) -> bool:
    if not selected:
        return True
    values = {part.strip() for part in str(cell).split(",")}
    return bool(values.intersection(selected))


def prepare_base(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["data_apresentacao", "data_ultima_tramitacao"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["mes_apresentacao"] = df["data_apresentacao"].dt.to_period("M").astype(str)
    return df


def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")

    termo = st.sidebar.text_input("Busca textual", help="Filtra por proposicao, ementa, autor, partido, tema ou situacao.")
    tipos = st.sidebar.multiselect("Tipo de proposicao", sorted(df["Sigla_tipo"].dropna().unique()))
    partidos = st.sidebar.multiselect("Partido", split_values(df["partidos"]))
    temas = st.sidebar.multiselect("Tema", split_values(df["temas"]))
    situacoes = st.sidebar.multiselect("Situacao", sorted(df["descricao_situacao"].dropna().unique()))

    min_date = df["data_apresentacao"].min()
    max_date = df["data_apresentacao"].max()
    if pd.notna(min_date) and pd.notna(max_date):
        periodo = st.sidebar.date_input(
            "Periodo de apresentacao",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
    else:
        periodo = ()

    somente_sem_tema = st.sidebar.checkbox("Somente proposicoes sem tema")
    ordenacao = st.sidebar.radio(
        "Ordenar por",
        [
            "Data de apresentacao mais recente",
            "Mais tramitacoes",
            "Mais autores",
            "Numero da proposicao",
        ],
    )

    filtered = df.copy()

    if termo:
        termo_lower = termo.lower()
        searchable_cols = [
            "proposicao",
            "ementa",
            "autores",
            "partidos",
            "temas",
            "descricao_situacao",
            "descricao_tipo",
        ]
        mask = pd.Series(False, index=filtered.index)
        for col in searchable_cols:
            mask = mask | filtered[col].fillna("").str.lower().str.contains(termo_lower, regex=False)
        filtered = filtered[mask]

    if tipos:
        filtered = filtered[filtered["Sigla_tipo"].isin(tipos)]
    if partidos:
        filtered = filtered[filtered["partidos"].apply(lambda value: contains_any_csv_value(value, partidos))]
    if temas:
        filtered = filtered[filtered["temas"].apply(lambda value: contains_any_csv_value(value, temas))]
    if situacoes:
        filtered = filtered[filtered["descricao_situacao"].isin(situacoes)]
    if len(periodo) == 2:
        start, end = pd.to_datetime(periodo[0]), pd.to_datetime(periodo[1])
        filtered = filtered[
            (filtered["data_apresentacao"].isna())
            | ((filtered["data_apresentacao"] >= start) & (filtered["data_apresentacao"] <= end))
        ]
    if somente_sem_tema:
        filtered = filtered[filtered["temas"] == "Sem tema associado"]

    if ordenacao == "Mais tramitacoes":
        filtered = filtered.sort_values(["quantidade_tramitacoes", "data_apresentacao"], ascending=[False, False])
    elif ordenacao == "Mais autores":
        filtered = filtered.sort_values(["quantidade_autores", "data_apresentacao"], ascending=[False, False])
    elif ordenacao == "Numero da proposicao":
        filtered = filtered.sort_values(["Sigla_tipo", "numero", "ano"], ascending=[True, True, False])
    else:
        filtered = filtered.sort_values(["data_apresentacao", "proposicao_id"], ascending=[False, False])

    return filtered


def render_metric_row(df: pd.DataFrame) -> None:
    cols = st.columns(6)
    values = [
        ("Proposicoes", df["proposicao_id"].nunique()),
        ("Deputados autores", int(df["quantidade_autores"].sum())),
        ("Partidos", len(split_values(df["partidos"]))),
        ("Temas", len(split_values(df["temas"]))),
        ("Tramitacoes", int(df["quantidade_tramitacoes"].sum())),
        ("Sem tema", int((df["temas"] == "Sem tema associado").sum())),
    ]
    for col, (label, value) in zip(cols, values):
        col.metric(label, value)


def render_visao_geral(
    config_items: tuple[tuple[str, str], ...],
    base_df: pd.DataFrame,
    filtered_df: pd.DataFrame,
) -> None:
    st.subheader("Visao Geral")
    counts = query_df(COUNT_QUERY, config_items)
    if not counts.empty:
        values = dict(zip(counts["metrica"], counts["total"]))
        cols = st.columns(6)
        for col, key in zip(cols, ["Proposicoes", "Deputados", "Partidos", "Temas", "Tramitacoes", "Autorias"]):
            col.metric(key, int(values.get(key, 0)))

    st.markdown("#### Recorte filtrado")
    render_metric_row(filtered_df)

    if filtered_df.empty:
        st.info("Nenhum registro encontrado com os filtros atuais.")
        return

    col1, col2 = st.columns(2)
    with col1:
        by_month = (
            filtered_df.dropna(subset=["mes_apresentacao"])
            .groupby("mes_apresentacao", as_index=False)
            .size()
            .rename(columns={"size": "quantidade"})
        )
        if not by_month.empty:
            fig = px.line(by_month, x="mes_apresentacao", y="quantidade", markers=True, title="Proposicoes por mes")
            st.plotly_chart(fig, width="stretch")
    with col2:
        by_type = (
            filtered_df.groupby("Sigla_tipo", as_index=False)
            .size()
            .rename(columns={"size": "quantidade"})
            .sort_values("quantidade", ascending=False)
        )
        plot_bar(by_type, "Sigla_tipo", "quantidade", "Proposicoes por tipo", top_n=12)

    col3, col4 = st.columns(2)
    with col3:
        by_situation = (
            filtered_df.fillna({"descricao_situacao": "Sem situacao"})
            .groupby("descricao_situacao", as_index=False)
            .size()
            .rename(columns={"size": "quantidade"})
            .sort_values("quantidade", ascending=False)
        )
        plot_bar(by_situation, "descricao_situacao", "quantidade", "Situacao atual", top_n=10, horizontal=True)
    with col4:
        sem_tema = int((base_df["temas"] == "Sem tema associado").sum())
        com_tema = int(len(base_df) - sem_tema)
        tema_df = pd.DataFrame(
            {"classificacao": ["Com tema", "Sem tema"], "quantidade": [com_tema, sem_tema]}
        )
        fig = px.pie(tema_df, names="classificacao", values="quantidade", title="Cobertura de classificacao tematica")
        st.plotly_chart(fig, width="stretch")


def render_ranking_partidos(
    config_items: tuple[tuple[str, str], ...],
    filtered_df: pd.DataFrame,
) -> None:
    st.subheader("Ranking de Partidos")
    df = query_df(RANKING_PARTIDOS_QUERY, config_items)
    plot_bar(df, "partido", "quantidade_proposicoes", "Top partidos por proposicoes", top_n=10)
    show_dataframe(df)
    download_csv(df, "ranking_partidos.csv")

    st.markdown("#### Distribuicao no recorte filtrado")
    rows = []
    for _, row in filtered_df.iterrows():
        for partido in str(row["partidos"]).split(","):
            partido = partido.strip()
            if partido and not partido.startswith("Sem "):
                rows.append(partido)
    if rows:
        local_df = (
            pd.Series(rows, name="partido")
            .value_counts()
            .reset_index(name="quantidade")
            .rename(columns={"index": "partido"})
        )
        plot_bar(local_df, "partido", "quantidade", "Partidos no recorte filtrado", top_n=10)
    else:
        st.info("Nao ha partidos no recorte filtrado.")


def render_ranking_deputados(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Ranking de Deputados")
    df = query_df(RANKING_DEPUTADOS_QUERY, config_items)
    plot_bar(df, "deputado", "quantidade_proposicoes_assinadas", "Top deputados por proposicoes", top_n=10)
    show_dataframe(df)
    download_csv(df, "ranking_deputados.csv")


def render_proposicoes_temas(filtered_df: pd.DataFrame) -> None:
    st.subheader("Proposicoes e Temas")
    cols = [
        "proposicao",
        "data_apresentacao",
        "descricao_tipo",
        "ementa",
        "temas",
        "autores",
        "partidos",
        "link_camara",
    ]
    sem_tema = int((filtered_df["temas"] == "Sem tema associado").sum())
    st.caption(f"{sem_tema} proposicoes no recorte aparecem sem tema associado e permanecem visiveis pelo LEFT JOIN.")
    show_dataframe(
        filtered_df[cols],
        link_columns={"link_camara": st.column_config.LinkColumn("Camara")},
    )
    download_csv(filtered_df[cols], "proposicoes_temas.csv")


def render_ultima_tramitacao(filtered_df: pd.DataFrame) -> None:
    st.subheader("Ultima Tramitacao")
    cols = [
        "proposicao",
        "data_ultima_tramitacao",
        "descricao_situacao",
        "descricao_tramitacao",
        "sigla_orgao",
        "nome_orgao",
        "ementa",
        "link_camara",
    ]
    show_dataframe(
        filtered_df[cols],
        link_columns={"link_camara": st.column_config.LinkColumn("Camara")},
    )
    download_csv(filtered_df[cols], "ultima_tramitacao.csv")


def render_temas_acima_media(config_items: tuple[tuple[str, str], ...], filtered_df: pd.DataFrame) -> None:
    st.subheader("Temas Acima da Media")
    df = query_df(TEMAS_ACIMA_MEDIA_QUERY, config_items)
    plot_bar(df, "tema", "quantidade_proposicoes", "Temas acima da media", top_n=10)
    show_dataframe(df)
    download_csv(df, "temas_acima_media.csv")

    st.markdown("#### Temas no recorte filtrado")
    tema_rows = []
    for value in filtered_df["temas"]:
        for tema in str(value).split(","):
            tema = tema.strip()
            if tema and not tema.startswith("Sem "):
                tema_rows.append(tema)
    if tema_rows:
        local_df = (
            pd.Series(tema_rows, name="tema")
            .value_counts()
            .reset_index(name="quantidade")
            .rename(columns={"index": "tema"})
        )
        plot_bar(local_df, "tema", "quantidade", "Temas mais frequentes no recorte", top_n=12, horizontal=True)
    else:
        st.info("Nao ha temas associados no recorte filtrado.")


def render_tramitacoes_acima_media(config_items: tuple[tuple[str, str], ...]) -> None:
    st.subheader("Proposicoes com Tramitacao Acima da Media")
    df = query_df(TRAMITACOES_ACIMA_MEDIA_QUERY, config_items)
    if not df.empty:
        chart_df = df.copy()
        chart_df["proposicao"] = (
            chart_df["Sigla_tipo"].fillna("")
            + " "
            + chart_df["numero"].astype(str)
            + "/"
            + chart_df["ano"].astype(str)
        )
        plot_bar(chart_df, "proposicao", "quantidade_tramitacoes", "Proposicoes mais movimentadas", top_n=10)
    show_dataframe(df)
    download_csv(df, "tramitacoes_acima_media.csv")


def render_explorar(filtered_df: pd.DataFrame) -> None:
    st.subheader("Explorar Proposicoes")
    rows_per_page = st.slider("Quantidade de linhas na tabela", min_value=10, max_value=200, value=50, step=10)
    cols = [
        "proposicao",
        "data_apresentacao",
        "descricao_tipo",
        "descricao_situacao",
        "quantidade_autores",
        "quantidade_tramitacoes",
        "temas",
        "autores",
        "partidos",
        "ementa",
        "link_camara",
    ]
    show_dataframe(
        filtered_df[cols].head(rows_per_page),
        link_columns={"link_camara": st.column_config.LinkColumn("Camara")},
    )
    download_csv(filtered_df[cols], "proposicoes_filtradas.csv")


def render_espectro(filtered_df: pd.DataFrame) -> None:
    st.subheader("Distribuicao por Espectro Politico")
    rows = []
    for _, row in filtered_df.iterrows():
        for partido in str(row["partidos"]).split(","):
            partido = partido.strip()
            if partido and not partido.startswith("Sem "):
                rows.append(
                    {
                        "partido": partido,
                        "espectro": SPECTRUM_MAP.get(partido, "Nao atribuido"),
                        "quantidade": 1,
                    }
                )
    if not rows:
        st.info("Nao ha partidos no recorte filtrado.")
        return

    df = pd.DataFrame(rows).groupby(["espectro", "partido"], as_index=False)["quantidade"].sum()
    tab_tree, tab_bar = st.tabs(["Mapa de arvore", "Barras"])
    with tab_tree:
        fig = px.treemap(
            df,
            path=[px.Constant("Todos os espectros"), "espectro", "partido"],
            values="quantidade",
            color="espectro",
            color_discrete_map=SPECTRUM_COLORS,
        )
        fig.update_traces(textinfo="label+value")
        st.plotly_chart(fig, width="stretch")
    with tab_bar:
        grouped = df.groupby("espectro", as_index=False)["quantidade"].sum().sort_values("quantidade", ascending=False)
        fig = px.bar(
            grouped,
            x="espectro",
            y="quantidade",
            color="espectro",
            color_discrete_map=SPECTRUM_COLORS,
            text="quantidade",
            title="Proposicoes por espectro no recorte filtrado",
        )
        st.plotly_chart(fig, width="stretch")


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

    base_df = prepare_base(query_df(BASE_PROPOSICOES_QUERY, config_items))
    if base_df.empty:
        st.warning("Nao ha proposicoes carregadas no banco.")
        st.stop()

    filtered_df = apply_sidebar_filters(base_df)

    tabs = st.tabs(
        [
            "Visao Geral",
            "Ranking de Partidos",
            "Ranking de Deputados",
            "Proposicoes e Temas",
            "Ultima Tramitacao",
            "Temas Acima da Media",
            "Tramitacoes Acima da Media",
            "Explorar",
            "Espectro Politico",
        ]
    )

    with tabs[0]:
        render_visao_geral(config_items, base_df, filtered_df)
    with tabs[1]:
        render_ranking_partidos(config_items, filtered_df)
    with tabs[2]:
        render_ranking_deputados(config_items)
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


if __name__ == "__main__":
    main()
