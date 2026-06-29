# Banco de Dados I - Trabalho Final

Projeto final da disciplina Banco de Dados I - ICP489.

A aplicação coleta, armazena e visualiza dados legislativos da Câmara dos Deputados em um banco relacional MySQL. A interface foi desenvolvida com Streamlit e é somente de leitura.

## Estrutura

```text
.
├── app.py
├── docker-compose.yml
├── requirements.txt
├── scripts/
├── sql/
├── src/
├── tests/
├── .env.example
└── .streamlit/secrets.toml.example
```

- `app.py`: ponto de entrada da aplicação Streamlit.
- `src/`: código da aplicação, consultas, conexão com banco, componentes e telas.
- `sql/`: modelo físico e consultas SQL.
- `scripts/`: carga, validação e sincronização de dados.
- `tests/`: testes do modelo relacional.
- `.env.example`: modelo de variáveis para execução local.
- `.streamlit/secrets.toml.example`: modelo de credenciais usado pelo Streamlit.

## Requisitos

- Python 3.10+
- Docker e Docker Compose
- MySQL client opcional, para inspeção manual do banco

## Configuração local

Crie o ambiente Python e instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copie os arquivos de exemplo:

```bash
cp .env.example .env
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Revise o `.env` antes de subir o banco. O `docker-compose.yml` exige as variáveis de conexão, incluindo:

```env
MYSQL_ROOT_PASSWORD=
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=trabalho_final
MYSQL_USER=
MYSQL_PASSWORD=
```

Use valores locais no `.env`. Não envie `.env`, `.streamlit/secrets.toml`, certificados ou chaves para o repositório.

## Banco de dados

Suba o MySQL:

```bash
docker compose up -d
```

Na primeira inicialização, o Docker executa:

```text
sql/parte2_modelo_fisico.sql
```

Para aplicar o modelo manualmente em outro MySQL:

```bash
mysql -h 127.0.0.1 -P 3306 -u SEU_USUARIO -p < sql/parte2_modelo_fisico.sql
```

Para verificar as tabelas:

```bash
mysql -h 127.0.0.1 -P 3306 -u SEU_USUARIO -p trabalho_final -e "SHOW TABLES;"
```

## Carga de dados

O script de carga consulta a API de Dados Abertos da Câmara e grava os dados no MySQL:

```bash
python scripts/popular_banco.py
```

Variáveis úteis no `.env`:

```env
ANO_PROPOSICOES=2025
MAX_PROPOSICOES=500
```

Para carregar mais de um ano:

```env
ANOS_PROPOSICOES=2025,2026
MAX_PROPOSICOES=250
```

O script evita duplicar registros usando as chaves do banco.

## Validação

Para conferir as tabelas carregadas:

```bash
python scripts/validar_banco.py
```

Para validar as consultas principais:

```bash
python scripts/validar_consultas_parte3.py
```

Para executar os testes:

```bash
pytest
```

## Aplicação

Com o banco em execução e o arquivo `.streamlit/secrets.toml` configurado, rode:

```bash
streamlit run app.py
```

Modelo mínimo de `.streamlit/secrets.toml`:

```toml
[mysql]
host = "127.0.0.1"
port = 3306
database = "trabalho_final"
user = "SEU_USUARIO"
password = "SUA_SENHA"
```

A aplicação apresenta consultas, métricas, tabelas e gráficos sobre proposições, deputados, partidos, temas, órgãos e tramitações.

## Aiven

Para usar MySQL no Aiven, preencha `.streamlit/secrets.toml` com os dados do serviço e configure SSL:

```toml
[mysql]
host = "SEU_HOST_AIVEN"
port = 18646
database = "defaultdb"
user = "avnadmin"
password = "SUA_SENHA_AIVEN"
ssl_mode = "REQUIRED"
ssl_ca = "certs/aiven-ca.pem"
ssl_verify_cert = true
ssl_verify_identity = false
```

O certificado CA deve ficar apenas localmente, por exemplo em `certs/aiven-ca.pem`.

Para sincronizar dados locais com o banco configurado no Streamlit:

```bash
python scripts/sincronizar_aiven.py
```
