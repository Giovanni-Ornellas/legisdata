import pandas as pd
import streamlit as st


DISPLAY_COLUMN_LABELS = {
    "proposicao_id": "ID da proposição",
    "partido_id": "ID do partido",
    "deputado_id": "ID do deputado",
    "tema_cod": "Código do tema",
    "partido": "Partido",
    "nome_partido": "Nome do partido",
    "deputado": "Deputado",
    "sigla_uf": "UF",
    "Sigla_tipo": "Tipo",
    "numero": "Número",
    "ano": "Ano",
    "ementa": "Ementa",
    "tema": "Tema",
    "temas": "Temas",
    "autores": "Autores",
    "partidos": "Partidos",
    "proposicao": "Proposição",
    "descricao_tipo": "Tipo de proposição",
    "data_apresentacao": "Data de apresentação",
    "data_ultima_tramitacao": "Data da última tramitação",
    "descricao_situacao": "Situação",
    "descricao_tramitacao": "Tramitação",
    "despacho": "Despacho",
    "apreciacao": "Apreciação",
    "sigla_orgao": "Órgão",
    "nome_orgao": "Nome do órgão",
    "sequencia": "Sequência",
    "quantidade": "Quantidade",
    "quantidade_autores": "Quantidade de autores",
    "quantidade_deputados_autores": "Deputados autores",
    "quantidade_proposicoes": "Quantidade de proposições",
    "quantidade_proposicoes_assinadas": "Proposições assinadas",
    "quantidade_como_proponente": "Como proponente",
    "quantidade_tramitacoes": "Quantidade de tramitações",
    "link_camara": "Link da Câmara",
    "mes_apresentacao": "Mês de apresentação",
    "classificacao": "Classificação",
    "espectro": "Espectro",
    "termo": "Termo",
    "explicacao": "Explicação",
    "exemplo": "Exemplo",
}


def show_dataframe(
    df: pd.DataFrame,
    empty_message: str = "Nenhum registro encontrado.",
    link_columns: dict | None = None,
) -> None:
    if df.empty:
        st.info(empty_message)
        return

    display_df = df.rename(columns=DISPLAY_COLUMN_LABELS)
    display_link_columns = {}
    for key, value in (link_columns or {}).items():
        display_link_columns[DISPLAY_COLUMN_LABELS.get(key, key)] = value

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config=display_link_columns or None,
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
