from mysql.connector import Error as MySQLError
import streamlit as st


def _error_text(exc: Exception) -> str:
    return str(exc).lower()


def render_connection_error(exc: Exception) -> None:
    st.error("Não foi possível conectar ao MySQL configurado.")

    if isinstance(exc, MySQLError) and getattr(exc, "errno", None) == 1045:
        st.info(
            "O banco foi encontrado, mas o usuário ou a senha foram recusados. "
            "Verifique `user` e `password` nos Secrets do Streamlit ou no `.env` local."
        )
    elif isinstance(exc, MySQLError) and getattr(exc, "errno", None) == 1049:
        st.info(
            "A conexão foi aberta, mas o banco informado não existe. "
            "Verifique o campo `database` na configuração."
        )
    elif "invalid ca certificate" in _error_text(exc) or "pem" in _error_text(exc):
        st.info(
            "O certificado CA usado na conexão SSL parece inválido ou incompleto. "
            "No Streamlit Cloud, cole o conteúdo completo do certificado em `ssl_ca_content`."
        )
    elif "can't connect" in _error_text(exc) or "connection refused" in _error_text(exc):
        st.info(
            "O host ou a porta do MySQL não puderam ser acessados. "
            "Verifique `host`, `port` e se o serviço está disponível."
        )
    else:
        st.info(
            "Confira as credenciais e os parâmetros de conexão. "
            "Em deploy no Streamlit Cloud, os dados devem estar em `App settings > Secrets`."
        )

    st.caption(f"Detalhe técnico: {exc}")
    st.stop()


def render_app_error(exc: Exception) -> None:
    st.error("Falha ao carregar os dados da aplicação.")

    text = _error_text(exc)
    if "doesn't exist" in text or "unknown table" in text:
        st.info(
            "A conexão funcionou, mas alguma tabela esperada não foi encontrada. "
            "Verifique se o script do modelo físico foi executado no banco correto."
        )
    elif "executa apenas consultas select" in text:
        st.info("A aplicação bloqueou uma consulta que não era somente leitura.")
    else:
        st.info("Tente recarregar a página. Se persistir, valide o banco e as consultas pelo terminal.")

    st.caption(f"Detalhe técnico: {exc}")
    st.stop()


def render_empty_database_message() -> None:
    st.warning("Não há proposições carregadas no banco.")
    st.info(
        "O banco conectou corretamente, mas a tabela `Proposicao` não possui registros. "
        "Execute a carga de dados ou verifique se a aplicação aponta para o banco correto."
    )
    st.stop()
