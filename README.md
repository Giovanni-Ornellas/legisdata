# Banco de Dados I - Trabalho Final

Projeto final da disciplina Banco de Dados I - ICP489.

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

## Aplicacao Streamlit

A Parte 4 do trabalho usa Streamlit para visualizar os dados carregados no MySQL local. A aplicacao e somente de leitura e reutiliza as consultas da Parte 3.

Instale as dependencias e prepare o arquivo de credenciais local:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Com o MySQL local em execucao na porta `3307`, rode:

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

As abas implementadas sao:

- Visao Geral
- Ranking de Partidos
- Ranking de Deputados
- Proposicoes e Temas
- Ultima Tramitacao
- Temas Acima da Media
- Tramitacoes Acima da Media

## Migracao futura para Aiven

A aplicacao ainda usa o MySQL local. Em uma etapa futura, a migracao para Aiven podera ser feita trocando apenas os dados de conexao em `.streamlit/secrets.toml`. Nao ha credenciais reais de Aiven no repositorio.
