# Banco de Dados I - Trabalho Final

Projeto final da disciplina Banco de Dados I - ICP489.

O objetivo do projeto é coletar, organizar e visualizar dados legislativos da Câmara dos Deputados em um banco relacional MySQL. A aplicação Web foi feita em Streamlit e é somente de leitura: ela consulta o banco, exibe tabelas, métricas e gráficos, mas não insere, altera nem exclui registros.

## Estrutura de pastas

```text
.
├── app.py
├── src/
│   ├── database.py
│   ├── queries.py
│   ├── services.py
│   ├── components/
│   └── views/
├── scripts/
├── sql/
├── relatorio/
├── docs/
├── tests/
└── .streamlit/
```

- `app.py`: inicialização da aplicação, cabeçalho, tratamento de conexão e navegação por abas.
- `src/database.py`: conexão com MySQL, suporte a Aiven/SSL e execução segura de consultas.
- `src/queries.py`: consultas SQL usadas pela aplicação.
- `src/services.py`: funções que carregam dados, aplicam cache e preparam `DataFrame`.
- `src/views/`: telas da aplicação, separadas por domínio.
- `src/components/`: filtros, gráficos, métricas, tabelas e exportação CSV.
- `src/content/`: glossário, explicações das consultas e textos didáticos.
- `scripts/`: scripts para popular e validar o banco.
- `sql/`: modelo físico e consultas da Parte 3.
- `docs/`: documentação técnica para manutenção em grupo.

Mais detalhes estão em [`docs/estrutura.md`](docs/estrutura.md).

## Banco de dados local

O projeto usa MySQL e o schema principal se chama `trabalho_final`.

### Subir MySQL com Docker

Opcionalmente, copie `.env.example` para `.env` e ajuste as credenciais.
Sem `.env`, o `docker-compose.yml` usa os valores padrão:

- banco: `trabalho_final`
- usuário: `bdi`
- senha: `bdi`
- senha do root: `root`
- porta: `3306`

```bash
docker compose up -d
```

Se a porta `3306` já estiver ocupada por outro MySQL local, use outra porta externa:

```bash
MYSQL_PORT=3307 docker compose up -d
```

Na primeira inicialização, o Docker executa automaticamente:

```text
sql/parte2_modelo_fisico.sql
```

Esse script cria as tabelas do modelo físico sem apagar dados existentes.

### Conectar no banco

```bash
docker compose exec mysql mysql -u bdi -pbdi trabalho_final
```

Ou pelo cliente MySQL local:

```bash
mysql -h 127.0.0.1 -P 3306 -u bdi -pbdi trabalho_final
```

Se o contêiner tiver sido iniciado com `MYSQL_PORT=3307`, use:

```bash
mysql -h 127.0.0.1 -P 3307 -u bdi -pbdi trabalho_final
```

### Criar o schema manualmente

Caso o MySQL já esteja instalado fora do Docker:

```bash
mysql -h 127.0.0.1 -P 3306 -u SEU_USUARIO -p < sql/parte2_modelo_fisico.sql
```

### Verificar tabelas e contagens

```bash
mysql -h 127.0.0.1 -P 3306 -u bdi -pbdi trabalho_final -e "SHOW TABLES;"
mysql -h 127.0.0.1 -P 3306 -u bdi -pbdi trabalho_final < sql/parte3_consultas.sql
```

Na configuração atual desta máquina, a porta `3306` estava ocupada e o contêiner foi iniciado na porta `3307`. Portanto, os comandos equivalentes são:

```bash
mysql -h 127.0.0.1 -P 3307 -u bdi -pbdi trabalho_final -e "SHOW TABLES;"
mysql -h 127.0.0.1 -P 3307 -u bdi -pbdi trabalho_final < sql/parte3_consultas.sql
```

Observação: antes de popular o banco, as consultas da Parte 3 podem retornar zero linhas. Em especial, `Participa` precisa conter dados reais de autoria para que os rankings por partido e deputado sejam úteis.

## Popular dados da API da Câmara

Crie um ambiente virtual, instale as dependências e copie as variáveis locais:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Na configuração local deste projeto, o MySQL está em `127.0.0.1:3307`, com usuário `bdi` e senha `bdi`. Para começar com uma carga menor, ajuste no `.env`:

```env
MAX_PROPOSICOES=50
ANO_PROPOSICOES=2025
```

Execute a população:

```bash
python scripts/popular_banco.py
```

O script carrega dados reais da API de Dados Abertos da Câmara e insere, quando houver dados disponíveis, as tabelas:

- `Partido`
- `Orgao`
- `Tema`
- `Proposicao`
- `Deputado`
- `Tramitacao`
- `Participa`
- `Classificacao`

O script usa `INSERT ... ON DUPLICATE KEY UPDATE`, então pode ser executado novamente sem duplicar registros.

## Validar dados carregados

Depois da população, execute:

```bash
python scripts/validar_banco.py
```

Esse script imprime `COUNT(*)` e `SELECT * LIMIT 10` para todas as tabelas. A tabela `Participa` deve ser conferida explicitamente, pois ela representa a autoria entre deputados e proposições e é essencial para as consultas da Parte 3.

Para validar as consultas SQL da Parte 3, execute:

```bash
python scripts/validar_consultas_parte3.py
```

Esse script executa as seis consultas principais, informa se cada uma rodou com sucesso e mostra a quantidade de linhas retornadas. Ele executa apenas consultas `SELECT` ou `WITH`.

## Aplicação Streamlit

A Parte 4 do trabalho usa Streamlit para visualizar os dados carregados no MySQL. A aplicação é somente de leitura e reutiliza as consultas da Parte 3.

A interface foi pensada para usuários leigos. Além de tabelas e gráficos, ela inclui textos curtos explicando o que são proposições, autores, temas, tramitações, órgãos e situações registradas nos dados.

Instale as dependências e prepare o arquivo de credenciais local:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Com o MySQL local em execução na porta `3307`, rode:

```bash
streamlit run app.py
```

O arquivo `.streamlit/secrets.toml` deve seguir o modelo:

```toml
[mysql]
host = "127.0.0.1"
port = 3307
database = "trabalho_final"
user = "bdi"
password = "bdi"
```

As abas implementadas são:

- Visão Geral
- Qualidade dos Dados
- Metodologia dos Dados
- Entenda uma Proposição
- Ranking de Partidos
- Ranking de Deputados
- Deputado Detalhado
- Órgãos
- Proposições e Temas
- Última Tramitação
- Temas Acima da Média
- Tramitações Acima da Média
- Explorar
- Espectro Político
- Glossário

A aplicação também possui filtros globais na barra lateral para busca textual, tipo de proposição, partido, tema, situação, período de apresentação e proposições sem tema. A navegação é agrupada por assunto na barra lateral para evitar excesso de abas na tela. As tabelas principais permitem exportação em CSV, e os gráficos usam Plotly para facilitar a leitura dos rankings e distribuições.

As telas com rankings e tabelas maiores possuem controles de limite, como quantidade de linhas exibidas e tamanho do Top N. Isso mantém a interface leve mesmo quando o banco receber cargas maiores.

### Funcionalidades didáticas

- Página inicial com orientação sobre o objetivo da aplicação.
- Página de qualidade dos dados com cobertura temática, autoria e tramitação.
- Página de metodologia com fonte, recorte, tabelas e limitações da carga.
- Glossário legislativo com termos como proposição, ementa, tramitação, despacho, comissão e plenário.
- Página "Entenda uma Proposição", com resumo, autores, partidos, temas, situação e linha do tempo de tramitação.
- Páginas de órgãos e deputado detalhado para melhor aproveitamento das tabelas `Orgao`, `Tramitacao`, `Deputado` e `Participa`.
- Explicações curtas para as consultas principais da Parte 3.
- Cards explicativos nas páginas de proposições, temas, tramitações, partidos e deputados.

## Como contribuir sem quebrar a estrutura

- Nova consulta SQL da aplicação: adicionar em `src/queries.py`.
- Nova função de carregamento/preparação de dados: adicionar em `src/services.py`.
- Nova aba ou seção visual: criar arquivo em `src/views/` e registrar em `app.py`.
- Novo gráfico, filtro, métrica ou tabela reutilizável: adicionar em `src/components/`.
- Novo texto explicativo, glossário ou descrição de consulta: adicionar em `src/content/`.
- Scripts de carga ou validação: manter em `scripts/`.
- Não colocar credenciais reais no repositório.
- Não executar comandos de escrita no banco pela aplicação Streamlit.

## Migração para Aiven

A aplicação pode usar o MySQL local ou um MySQL hospedado no Aiven. Não há credenciais reais de Aiven no repositório.

Para apontar o Streamlit para o Aiven, copie o exemplo de secrets e preencha o arquivo local, que não deve ser commitado:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Modelo de configuração para Aiven:

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

Baixe o certificado CA no painel do Aiven e salve localmente em `certs/aiven-ca.pem`. Arquivos `.pem` e `.crt` dentro de `certs/` estão ignorados pelo Git.

No Streamlit Cloud, o arquivo local `.streamlit/secrets.toml` não é enviado para o servidor. Nesse caso, abra a aplicação no Streamlit Cloud, entre em `App settings > Secrets` e cole os dados no formato abaixo. Use `ssl_ca_content` para colar o conteúdo completo do certificado CA:

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
COLE_AQUI_O_CA_CERTIFICATE_DO_AIVEN
-----END CERTIFICATE-----
"""
ssl_verify_cert = true
ssl_verify_identity = false
```

Para levar os dados locais para o Aiven, primeiro exporte o banco local:

```bash
mysqldump --single-transaction --no-tablespaces \
  -h 127.0.0.1 -P 3307 -u bdi -p trabalho_final > dump_trabalho_final.sql
```

Depois importe no banco `defaultdb` do Aiven:

```bash
mysql --ssl-mode=REQUIRED \
  -h SEU_HOST_AIVEN -P 18646 -u avnadmin -p defaultdb < dump_trabalho_final.sql
```

Com o `.streamlit/secrets.toml` preenchido, execute:

```bash
streamlit run app.py
```

Os scripts `scripts/popular_banco.py` e `scripts/validar_banco.py` também aceitam as variáveis `MYSQL_SSL_MODE`, `MYSQL_SSL_CA`, `MYSQL_SSL_VERIFY_CERT` e `MYSQL_SSL_VERIFY_IDENTITY` no `.env`.
