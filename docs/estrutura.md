# Estrutura do Projeto

Este projeto foi organizado para separar interface, regras de consulta e acesso ao banco de dados. A aplicação continua sendo executada por `streamlit run app.py`.

## Pastas Principais

- `app.py`: ponto de entrada da aplicação Streamlit. Define o cabeçalho, carrega a configuração, aplica filtros globais e organiza as abas.
- `src/database.py`: conexão com MySQL, suporte a SSL/Aiven e execução segura de consultas somente leitura.
- `src/queries.py`: consultas SQL usadas pela aplicação.
- `src/services.py`: camada intermediária entre as views e as queries. Carrega dados, aplica cache e prepara DataFrames.
- `src/views/`: telas e seções da aplicação. Cada arquivo representa um domínio de visualização.
- `src/components/`: componentes reutilizáveis de interface, como filtros, gráficos, métricas, tabelas e exportação CSV.
- `sql/`: scripts SQL do modelo físico e das consultas da Parte 3.
- `scripts/`: scripts auxiliares para popular e validar o banco.
- `relatorio/`: textos do relatório acadêmico.
- `docs/`: documentação técnica curta para o grupo.

## Onde Adicionar uma Nova Consulta

Adicione a consulta SQL em `src/queries.py` com um nome claro, por exemplo:

```python
NOVA_CONSULTA_QUERY = """
SELECT ...
"""
```

Depois, crie uma função em `src/services.py` que execute essa consulta e retorne um `pandas.DataFrame`.

## Onde Adicionar uma Nova Página ou Aba

Crie um novo arquivo em `src/views/`, por exemplo:

```text
src/views/nova_pagina.py
```

Dentro dele, crie uma função `render_...()` responsável por exibir a interface. Depois importe essa função em `app.py` e adicione uma nova aba em `st.tabs`.

## Onde Adicionar um Novo Gráfico ou Componente

Componentes reutilizáveis devem ficar em `src/components/`.

- Gráficos: `src/components/charts.py`
- Filtros: `src/components/filters.py`
- Métricas: `src/components/metrics.py`
- Tabelas e downloads: `src/components/tables.py`

Se o código for usado por mais de uma tela, ele deve ficar em `components`. Se for específico de uma aba, pode ficar na própria view.

## Fluxo Recomendado

O fluxo de dados recomendado é:

```text
View -> Service -> Query -> Database
```

Exemplo:

1. A view chama uma função em `src/services.py`.
2. O service escolhe uma consulta de `src/queries.py`.
3. O service usa `src/database.py` para executar a consulta.
4. A view recebe um `DataFrame` pronto e renderiza tabelas, métricas ou gráficos.

## Regras de Manutenção

- Não coloque SQL diretamente nas views.
- Não coloque credenciais no código.
- Não faça `INSERT`, `UPDATE`, `DELETE` ou `DROP` pela aplicação Streamlit.
- Não altere o schema sem combinar com o grupo.
- Mantenha textos exibidos ao usuário em português formal e com acentuação.
