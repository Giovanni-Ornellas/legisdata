# Parte 4 — Aplicação Web

## Tecnologia utilizada

A aplicação Web foi implementada em Python utilizando o framework Streamlit. A escolha do Streamlit permite construir uma interface interativa de consulta e visualização de dados com baixo custo de configuração, mantendo integração direta com consultas SQL executadas no banco MySQL.

## Conexão com o banco de dados

A aplicação se conecta ao banco MySQL local `trabalho_final`, atualmente executado em `127.0.0.1:3307`. As credenciais não são fixadas no código-fonte: a aplicação lê os dados de conexão a partir de `.streamlit/secrets.toml` e, como alternativa, de variáveis de ambiente ou do arquivo `.env`.

A conexão é centralizada em `src/database.py`, que fornece funções reutilizáveis para abrir a conexão MySQL e executar consultas de leitura. A aplicação executa apenas comandos `SELECT`, sem operações de escrita no banco.

## Organização do código

A aplicação foi refatorada para evitar concentração de responsabilidades em um único arquivo. O arquivo `app.py` atua como ponto de entrada, responsável pela configuração geral, tratamento de conexão, filtros globais e navegação entre abas.

As consultas SQL usadas pela aplicação foram centralizadas em `src/queries.py`. A camada `src/services.py` executa essas consultas, aplica cache do Streamlit e prepara os dados em `DataFrame`. As telas ficam em `src/views/`, separadas por tema, como proposições, deputados, partidos, temas e tramitações. Componentes reutilizáveis de interface, como gráficos, filtros, métricas, tabelas e exportação CSV, ficam em `src/components/`.

Essa organização segue o fluxo `View -> Service -> Query -> Database`, facilitando manutenção por diferentes integrantes do grupo.

## Funcionalidades implementadas

A aplicação apresenta abas de exploração, validação e apoio didático:

- Visão Geral: mostra métricas gerais do banco, como totais de proposições, deputados, partidos, temas, tramitações e relações de autoria.
- Qualidade dos Dados: mostra cobertura temática, autoria, tramitação e lacunas da carga.
- Metodologia dos Dados: explica fonte, recorte, tabelas populadas e limitações dos dados.
- Entenda uma Proposição: apresenta resumo didático e linha do tempo de uma proposição selecionada.
- Ranking de Partidos: apresenta os partidos com maior quantidade de proposições associadas a seus deputados.
- Ranking de Deputados: apresenta os deputados com maior número de proposições assinadas.
- Deputado Detalhado: permite selecionar um deputado e visualizar dados básicos, proposições e temas frequentes.
- Órgãos: lista órgãos cadastrados, tipos de órgão e tramitações associadas.
- Proposições e Temas: lista proposições e seus temas, preservando proposições sem classificação temática.
- Última Tramitação: mostra a última tramitação conhecida de cada proposição.
- Temas Acima da Média: destaca temas com quantidade de proposições acima da média.
- Tramitações Acima da Média: lista proposições com número de tramitações acima da média.
- Explorar: disponibiliza uma tabela geral de proposições filtradas, com autores, partidos, temas, situação, tramitações e link para a página da Câmara.
- Espectro Político: agrupa os partidos por uma classificação de espectro político para apoiar análises exploratórias da composição partidária das proposições.

Além das abas, a aplicação possui uma barra lateral com filtros globais por texto, tipo de proposição, partido, tema, situação, período de apresentação e proposições sem tema. Esses filtros são aplicados às abas exploratórias e permitem simular recortes que seriam úteis em uma aplicação pública de consulta legislativa.

## Consultas utilizadas

A aplicação utiliza as seis consultas formuladas na Parte 3:

1. Ranking de partidos por quantidade de proposições com autoria.
2. Deputados com maior número de proposições assinadas.
3. Proposições com seus temas, mantendo proposições sem tema por meio de `LEFT JOIN`.
4. Última tramitação conhecida de cada proposição.
5. Temas com quantidade de proposições acima da média.
6. Proposições com número de tramitações acima da média.

Além dessas consultas, a aba de visão geral executa consultas de contagem (`COUNT(*)`) sobre as principais tabelas do banco.

## Visualizações

As visualizações incluem tabelas interativas com `st.dataframe`, métricas com `st.metric`, gráficos de barras, gráfico de linha temporal, gráfico de pizza e mapa de árvore. A biblioteca Plotly é usada para melhorar a leitura dos rankings, distribuições por tipo, situação, tema, partido e espectro político.

As principais tabelas também possuem botão de exportação em CSV, o que permite reaproveitar os resultados filtrados em planilhas ou anexos de análise.

A interface usa um padrão visual único para métricas, tabelas, caixas de ajuda e mensagens de retorno. Também há tratamento específico para erros comuns de conexão, como senha incorreta, banco inexistente, host inacessível e certificado CA inválido.

A navegação foi organizada em grupos na barra lateral, reduzindo a quantidade de abas simultâneas e carregando apenas a página selecionada. Telas com rankings ou tabelas extensas possuem controles de limite, como Top N e quantidade de linhas exibidas, para manter a aplicação legível com bases maiores.

## Funcionalidades didáticas

A aplicação também foi ampliada para facilitar o uso por pessoas sem familiaridade prévia com o processo legislativo. A página inicial apresenta o objetivo do sistema e orienta a navegação. A aba "Entenda uma Proposição" resume uma proposição específica, mostrando tipo, número, ano, ementa, autores, partidos, temas, situação, órgãos envolvidos e linha do tempo das tramitações registradas.

A aba "Glossário" reúne explicações curtas para termos recorrentes nos dados, como proposição, projeto de lei, ementa, autor, órgão, tramitação, despacho, situação, plenário e comissão. As páginas principais também possuem cards explicativos e descrições das consultas da Parte 3, indicando o que cada visualização mostra, por que ela é útil e como interpretar os resultados.

Todas as explicações são estáticas e baseadas nos campos disponíveis no banco. A aplicação não consulta APIs externas em tempo de execução e não produz conclusões jurídicas ou políticas.

## Validação das consultas

O projeto inclui o script `scripts/validar_consultas_parte3.py`, que executa as seis consultas principais da Parte 3, informa se cada consulta foi executada com sucesso e mostra a quantidade de linhas retornadas. O script valida que as consultas são apenas `SELECT` ou `WITH`, sem modificar o banco.

```bash
python scripts/validar_consultas_parte3.py
```

## Como executar

Com o MySQL local em execução e populado, a aplicação pode ser executada com os comandos:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
streamlit run app.py
```

O arquivo `.streamlit/secrets.toml` deve conter os dados de conexão local com o banco MySQL.

## Preparação para Aiven

A aplicação foi preparada para utilizar o MySQL local ou uma instância MySQL hospedada no Aiven sem alteração no código principal. Para isso, a camada de conexão aceita parâmetros de SSL, como `ssl_mode`, `ssl_ca`, `ssl_verify_cert` e `ssl_verify_identity`.

Na migração para Aiven, basta alterar os dados de conexão em `.streamlit/secrets.toml`, substituindo host, porta, usuário, senha e banco pelos valores fornecidos pela instância Aiven. Como o serviço Aiven exige conexão criptografada, o modo SSL deve ser configurado como `REQUIRED`, com possibilidade de informar o certificado CA baixado no painel do serviço.

Nenhuma credencial real do Aiven foi adicionada ao projeto. O arquivo real `.streamlit/secrets.toml` permanece local e não é versionado.
