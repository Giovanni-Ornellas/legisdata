# Parte 4 — Aplicação Web

## Tecnologia utilizada

A aplicação Web foi implementada em Python utilizando o framework Streamlit. A escolha do Streamlit permite construir uma interface interativa de consulta e visualização de dados com baixo custo de configuração, mantendo integração direta com consultas SQL executadas no banco MySQL.

## Conexão com o banco de dados

A aplicação se conecta ao banco MySQL local `trabalho_final`, atualmente executado em `127.0.0.1:3307`. As credenciais não são fixadas no código-fonte: a aplicação lê os dados de conexão a partir de `.streamlit/secrets.toml` e, como alternativa, de variáveis de ambiente ou do arquivo `.env`.

A conexão é centralizada em `src/database.py`, que fornece funções reutilizáveis para abrir a conexão MySQL e executar consultas de leitura. A aplicação executa apenas comandos `SELECT`, sem operações de escrita no banco.

## Funcionalidades implementadas

A aplicação apresenta nove abas principais:

- Visão Geral: mostra métricas gerais do banco, como totais de proposições, deputados, partidos, temas, tramitações e relações de autoria.
- Ranking de Partidos: apresenta os partidos com maior quantidade de proposições associadas a seus deputados.
- Ranking de Deputados: apresenta os deputados com maior número de proposições assinadas.
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

A aplicação foi preparada para uma migração futura para Aiven sem alteração no código principal. Quando a migração for realizada, bastará alterar os dados de conexão em `.streamlit/secrets.toml`, substituindo host, porta, usuário, senha e banco pelos valores fornecidos pela instância Aiven. Nenhuma credencial real do Aiven foi adicionada ao projeto nesta etapa.
