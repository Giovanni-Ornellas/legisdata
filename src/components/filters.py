import pandas as pd
import streamlit as st


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


def render_filter_feedback(total_rows: int, filtered_rows: int, termo: str, term_matches: int) -> None:
    st.sidebar.caption(f"Registros no recorte: {filtered_rows} de {total_rows}")
    if termo and term_matches > 0 and filtered_rows == 0:
        st.sidebar.warning("A palavra-chave existe no banco, mas os outros filtros removeram os resultados.")


def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")
    st.sidebar.caption("Refine o recorte sem sair da página atual.")

    total_rows = len(df)
    term_matches = total_rows
    termo = st.sidebar.text_input(
        "Buscar assunto",
        placeholder="Ex.: saúde, educação, escala 6x1",
        help="Busca no texto da ementa e também em autores, partidos, temas e situação.",
    )
    anos = st.sidebar.multiselect("Ano", sorted(df["ano"].dropna().unique(), reverse=True), placeholder="Todos os anos")
    tipos = st.sidebar.multiselect("Tipo", sorted(df["Sigla_tipo"].dropna().unique()), placeholder="Todos os tipos")
    temas = st.sidebar.multiselect("Tema", split_values(df["temas"]), placeholder="Todos os temas")
    partidos = st.sidebar.multiselect("Partido", split_values(df["partidos"]), placeholder="Todos os partidos")
    deputados = st.sidebar.multiselect("Deputado", split_values(df["autores"]), placeholder="Todos os deputados")
    situacoes = st.sidebar.multiselect("Situação", sorted(df["descricao_situacao"].dropna().unique()), placeholder="Todas")

    min_date = df["data_apresentacao"].min()
    max_date = df["data_apresentacao"].max()
    if pd.notna(min_date) and pd.notna(max_date):
        periodo = st.sidebar.date_input(
            "Período de apresentação",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
    else:
        periodo = ()

    somente_sem_tema = st.sidebar.checkbox("Somente proposições sem tema")
    ordenacao = st.sidebar.radio(
        "Ordenar por",
        [
            "Data de apresentação mais recente",
            "Mais tramitações",
            "Mais autores",
            "Número da proposição",
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
        term_matches = int(mask.sum())
        filtered = filtered[mask]

    if anos:
        filtered = filtered[filtered["ano"].isin(anos)]
    if tipos:
        filtered = filtered[filtered["Sigla_tipo"].isin(tipos)]
    if temas:
        filtered = filtered[filtered["temas"].apply(lambda value: contains_any_csv_value(value, temas))]
    if partidos:
        filtered = filtered[filtered["partidos"].apply(lambda value: contains_any_csv_value(value, partidos))]
    if deputados:
        filtered = filtered[filtered["autores"].apply(lambda value: contains_any_csv_value(value, deputados))]
    if situacoes:
        filtered = filtered[filtered["descricao_situacao"].isin(situacoes)]
    if isinstance(periodo, tuple) and len(periodo) == 2:
        start, end = pd.to_datetime(periodo[0]), pd.to_datetime(periodo[1])
        filtered = filtered[
            (filtered["data_apresentacao"].isna())
            | ((filtered["data_apresentacao"] >= start) & (filtered["data_apresentacao"] <= end))
        ]
    if somente_sem_tema:
        filtered = filtered[filtered["temas"] == "Sem tema associado"]

    render_filter_feedback(total_rows, len(filtered), termo, term_matches)

    if ordenacao == "Mais tramitações":
        return filtered.sort_values(["quantidade_tramitacoes", "data_apresentacao"], ascending=[False, False])
    if ordenacao == "Mais autores":
        return filtered.sort_values(["quantidade_autores", "data_apresentacao"], ascending=[False, False])
    if ordenacao == "Número da proposição":
        return filtered.sort_values(["Sigla_tipo", "numero", "ano"], ascending=[True, True, False])
    return filtered.sort_values(["data_apresentacao", "proposicao_id"], ascending=[False, False])
