# Guia do Projeto para o Grupo

Este documento resume a organização do projeto, as ferramentas utilizadas e os cuidados necessários para manutenção. A ideia é permitir que qualquer integrante do grupo consiga executar, entender e modificar o projeto sem quebrar a estrutura.

## Objetivo do Projeto

O projeto organiza dados legislativos da Câmara dos Deputados em um banco relacional MySQL e apresenta esses dados em uma aplicação Web feita com Streamlit.

A aplicação é somente de leitura. Ela consulta o banco e exibe métricas, tabelas, filtros e gráficos, mas não cria, altera ou apaga registros.

## Ferramentas Utilizadas

- **Python**: linguagem principal dos scripts e da aplicação.
- **Streamlit**: framework usado para criar a aplicação Web.
- **MySQL**: banco relacional usado no modelo físico.
- **Aiven**: serviço usado para hospedar o MySQL na nuvem.
- **Docker Compose**: usado para subir o MySQL local quando necessário.
- **Pandas**: usado para manipular os resultados das consultas como `DataFrame`.
- **Plotly**: usado para gráficos mais legíveis na aplicação.
- **mysql-connector-python**: biblioteca de conexão entre Python e MySQL.
- **API de Dados Abertos da Câmara**: fonte dos dados legislativos.

## Estrutura Principal

```text
.
├── app.py
├── src/
│   ├── database.py
│   ├── queries.py
│   ├── services.py
│   ├── components/
│   ├── content/
│   └── views/
├── scripts/
├── sql/
├── docs/
├── relatorio/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Função de Cada Parte

- `app.py`: inicia o Streamlit, carrega os dados principais, aplica filtros e organiza a navegação.
- `src/database.py`: concentra a conexão com MySQL local ou Aiven.
- `src/queries.py`: guarda as consultas SQL usadas pela aplicação.
- `src/services.py`: executa consultas, aplica cache e entrega dados prontos para as telas.
- `src/views/`: contém as páginas da aplicação.
- `src/components/`: contém filtros, tabelas, gráficos, métricas e componentes reutilizáveis.
- `src/content/`: guarda textos didáticos, glossário e explicações das consultas.
- `scripts/`: contém scripts de população, validação e sincronização com Aiven.
- `sql/`: contém o modelo físico e as consultas oficiais da Parte 3.
- `docs/`: documentação técnica e acadêmica de apoio.
- `relatorio/`: textos usados no relatório do trabalho.

## Fluxo de Dados da Aplicação

O fluxo recomendado é:

```text
View -> Service -> Query -> Database
```

Exemplo:

1. Uma tela em `src/views/` chama uma função de `src/services.py`.
2. O service escolhe uma consulta em `src/queries.py`.
3. A consulta é executada via `src/database.py`.
4. O resultado volta como `DataFrame` para a tela.

Esse padrão evita espalhar SQL pela interface e facilita manutenção.

## Banco de Dados

O modelo físico está em:

```text
sql/parte2_modelo_fisico.sql
```

As tabelas principais são:

- `Partido`
- `Orgao`
- `Tema`
- `Proposicao`
- `Deputado`
- `Tramitacao`
- `Participa`
- `Classificacao`

A tabela `Participa` representa a autoria entre deputados e proposições. Ela é essencial para rankings de partidos e deputados.

A tabela `Classificacao` representa a associação entre proposições e temas.

## Consultas da Parte 3

As consultas oficiais da Parte 3 estão em:

```text
sql/parte3_consultas.sql
relatorio/parte3_consultas.md
```

Elas incluem:

1. Ranking de partidos por proposições com autoria.
2. Deputados com mais proposições assinadas.
3. Proposições e temas, preservando proposições sem tema.
4. Última tramitação conhecida de cada proposição.
5. Temas com quantidade de proposições acima da média.
6. Proposições com tramitações acima da média.

## Scripts Importantes

Popular banco local:

```bash
python scripts/popular_banco.py
```

Validar tabelas e amostras:

```bash
python scripts/validar_banco.py
```

Validar consultas da Parte 3:

```bash
python scripts/validar_consultas_parte3.py
```

Sincronizar dados locais para Aiven:

```bash
python scripts/sincronizar_aiven.py
```

Executar aplicação:

```bash
streamlit run app.py
```

## Configuração de Credenciais

Credenciais reais não devem ser colocadas no GitHub.

Para execução local do Streamlit, use:

```text
.streamlit/secrets.toml
```

O exemplo público fica em:

```text
.streamlit/secrets.toml.example
```

Para scripts locais, pode ser usado:

```text
.env
```

O exemplo público fica em:

```text
.env.example
```

## Regras de Manutenção

- Não colocar senha real no código.
- Não alterar o schema sem combinar com o grupo.
- Não colocar SQL diretamente nas páginas de interface.
- Não fazer `INSERT`, `UPDATE`, `DELETE` ou `DROP` pela aplicação Streamlit.
- Consultas novas devem ir em `src/queries.py`.
- Funções de carregamento devem ir em `src/services.py`.
- Telas novas devem ir em `src/views/`.
- Componentes reutilizáveis devem ir em `src/components/`.
- Textos explicativos devem ir em `src/content/`.

## Como Adicionar uma Nova Página

1. Criar arquivo em `src/views/`, por exemplo:

```text
src/views/nova_pagina.py
```

2. Criar uma função `render_nova_pagina()`.
3. Importar a função em `app.py`.
4. Adicionar a página no grupo correto da navegação.

## Como Adicionar uma Nova Consulta

1. Criar a consulta em `src/queries.py`.
2. Criar função em `src/services.py` para executar a consulta.
3. Chamar a função na view correspondente.
4. Exibir o resultado com componentes de `src/components/`.

## Situação Atual dos Dados

Na carga atual, o banco contém dados de 2025 e 2026, com 1055 proposições carregadas. Os dados foram sincronizados para o Aiven e a aplicação Streamlit está usando essa conexão no deploy.

Contagens principais da carga atual:

```text
Partido        21
Orgao          1628
Tema           32
Proposicao     1055
Deputado       600
Tramitacao     5182
Participa      21153
Classificacao  965
```

## Cuidados Antes da Apresentação

- Confirmar se o Streamlit Cloud está conectado ao Aiven.
- Confirmar se as páginas abrem sem erro.
- Tirar prints das consultas da Parte 3.
- Tirar prints das telas principais da aplicação.
- Evitar mudar credenciais ou schema perto da entrega.
