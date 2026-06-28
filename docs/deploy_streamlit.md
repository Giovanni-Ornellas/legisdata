# Deploy no Streamlit Cloud

Este guia resume como publicar a aplicação no Streamlit Cloud usando o banco MySQL hospedado no Aiven.

## Configurar Secrets

No painel do Streamlit Cloud, abra:

```text
Manage app -> Settings -> Secrets
```

Cole os dados de conexão no formato:

```toml
[mysql]
host = "SEU_HOST_AIVEN"
port = 18646
database = "defaultdb"
user = "avnadmin"
password = "SUA_SENHA_AIVEN"
ssl_mode = "REQUIRED"
ssl_ca_content = """
-----BEGIN CERTIFICATE-----
COLE_AQUI_O_CONTEUDO_DO_CERTIFICADO_CA
-----END CERTIFICATE-----
"""
ssl_verify_cert = true
ssl_verify_identity = false
```

Não coloque esses dados em arquivos versionados.

## Reiniciar a aplicação

Após alterar os Secrets:

1. Clique em `Manage app`.
2. Use `Reboot app`.
3. Se necessário, use `Clear cache and reboot`.

## Erros comuns

- **Access denied for user**: usuário ou senha do Aiven estão incorretos.
- **Can't connect to MySQL server**: host, porta ou rede estão incorretos.
- **Invalid CA Certificate**: o certificado CA foi colado incompleto ou com formato inválido.
- **Unknown database**: o nome do banco informado não existe no serviço.
- **No module named ...**: alguma dependência está faltando em `requirements.txt`.

## Validação rápida

Depois do deploy, confirme se a aplicação abre e se as abas carregam métricas, tabelas e gráficos. A aplicação deve continuar somente leitura.
