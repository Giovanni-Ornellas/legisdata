import pandas as pd
import streamlit as st


def _format_date(value) -> str:
    if pd.isna(value):
        return "Data não informada"
    return pd.to_datetime(value).strftime("%d/%m/%Y %H:%M")


def render_timeline(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Não há tramitações registradas para esta proposição.")
        return

    timeline_df = df.copy()
    timeline_df["data_hora"] = pd.to_datetime(timeline_df["data_hora"], errors="coerce")
    timeline_df = timeline_df.sort_values(["data_hora", "sequencia"], ascending=[False, False])

    for _, row in timeline_df.iterrows():
        title = f"{_format_date(row['data_hora'])} · {row.get('sigla_orgao') or 'Órgão não informado'}"
        with st.expander(title):
            st.markdown(f"**Tramitação:** {row.get('descricao_tramitacao') or 'Não informada'}")
            st.markdown(f"**Situação:** {row.get('descricao_situacao') or 'Não informada'}")
            if row.get("nome_orgao"):
                st.markdown(f"**Órgão:** {row['nome_orgao']}")
            if row.get("despacho"):
                st.markdown(f"**Despacho:** {row['despacho']}")
            if row.get("apreciacao"):
                st.markdown(f"**Apreciação:** {row['apreciacao']}")
            st.caption(
                "Este item representa uma movimentação registrada no histórico da proposição. "
                "A aplicação exibe o texto disponível no banco, sem interpretar efeitos jurídicos."
            )
