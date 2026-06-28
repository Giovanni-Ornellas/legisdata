# Guia das Funções da Aplicação

Este documento explica, em linguagem direta, o que cada parte da aplicação Streamlit faz e como ela pode ser apresentada para usuários, colegas e avaliadores.

## Objetivo da Aplicação

A aplicação permite visualizar dados legislativos da Câmara dos Deputados de forma mais amigável. Ela ajuda a responder perguntas como:

- Quantas proposições foram carregadas?
- Quais partidos aparecem com mais proposições?
- Quais deputados assinaram mais proposições?
- Quais temas são mais recorrentes?
- Qual é a última tramitação registrada de uma proposição?
- Por quais órgãos uma proposição passou?
- Existem proposições sem tema, sem autores ou sem tramitação?

A aplicação não interpreta juridicamente as proposições. Ela apenas organiza e apresenta os dados disponíveis no banco.

## Navegação

A navegação fica na barra lateral e é organizada por grupos:

- **Panorama**
- **Proposições**
- **Parlamentares e Partidos**
- **Tramitação e Órgãos**
- **Apoio**

Essa organização evita uma tela cheia de abas e facilita a apresentação.

## Filtros Laterais

Os filtros laterais permitem reduzir o conjunto de proposições exibido.

Filtros disponíveis:

- Texto da ementa ou palavra-chave.
- Ano da proposição.
- Tipo de proposição.
- Tema tratado.
- Partido do autor.
- Deputado autor.
- Situação.
- Período de apresentação.
- Somente proposições sem tema.
- Ordenação.

A barra lateral também mostra quantos registros restaram no recorte filtrado. Se uma palavra-chave existe, mas outros filtros removem os resultados, a aplicação mostra um aviso.

## Visão Geral

Mostra uma visão inicial do banco.

Principais elementos:

- Total de proposições.
- Total de deputados.
- Total de partidos.
- Total de temas.
- Total de tramitações.
- Total de autorias.
- Gráficos por tipo de proposição e situação.

Uso na apresentação:

> Esta tela demonstra que a aplicação está conectada ao banco e resume o volume geral dos dados carregados.

## Qualidade dos Dados

Mostra indicadores de cobertura da carga.

Indicadores:

- Total de proposições.
- Proposições sem tema.
- Proposições sem tramitação.
- Proposições sem autores identificados.
- Total de relações em `Participa`.
- Total de relações em `Classificacao`.
- Cobertura temática.
- Cobertura de autoria.
- Cobertura de tramitação.

Uso na apresentação:

> Esta página mostra uma análise crítica da base. Nem todos os dados da API vêm completos, então a aplicação evidencia lacunas em vez de escondê-las.

## Metodologia dos Dados

Explica a origem e o recorte da carga.

Conteúdos principais:

- Fonte: API de Dados Abertos da Câmara dos Deputados.
- Tabelas populadas.
- Recorte por ano.
- Limitações da carga.
- Campos nulos vindos da fonte.
- Autores ignorados quando não eram deputados.

Uso na apresentação:

> Esta página justifica o processo de coleta e mostra que o grupo reconhece as limitações dos dados.

## Entenda uma Proposição

Permite selecionar uma proposição e ver um resumo didático.

Mostra:

- Tipo.
- Número.
- Ano.
- Ementa.
- Autores.
- Partidos envolvidos.
- Temas.
- Situação mais recente.
- Dados principais.
- Linha do tempo de tramitações.
- Órgãos envolvidos.

A busca dessa página usa a base completa por padrão. Existe uma opção para aplicar os filtros laterais quando o usuário quiser restringir a seleção.

Uso na apresentação:

> Esta página transforma uma linha do banco em uma explicação compreensível para usuário leigo.

## Proposições e Temas

Lista proposições com seus temas associados.

Ponto técnico importante:

- Usa `LEFT JOIN` para manter proposições sem tema.
- Quando não há tema, aparece `Sem tema associado`.

Uso na apresentação:

> Esta tela mostra por que a junção externa é importante: ela evita que registros incompletos desapareçam da análise.

## Explorar

Mostra uma tabela geral de proposições filtradas.

Uso principal:

- Procurar proposições por palavra-chave.
- Combinar filtros por tema, partido, deputado, ano e situação.
- Exportar resultados em CSV.

Uso na apresentação:

> Esta tela funciona como uma busca geral sobre a base carregada.

## Ranking de Partidos

Mostra partidos ordenados pela quantidade de proposições associadas a seus deputados.

Base lógica:

- `Partido`
- `Deputado`
- `Participa`
- `Proposicao`

Uso na apresentação:

> Esta tela usa múltiplos joins e agregação para mostrar participação legislativa por partido.

## Ranking de Deputados

Mostra deputados com maior número de proposições assinadas.

Informações exibidas:

- Deputado.
- UF.
- Partido.
- Quantidade de proposições assinadas.
- Quantidade como proponente.

Uso na apresentação:

> Esta tela usa a tabela `Participa`, que representa a relação de autoria entre deputados e proposições.

## Deputado Detalhado

Permite selecionar um deputado específico.

Mostra:

- Nome.
- Partido.
- UF.
- E-mail, quando disponível.
- Foto, quando disponível.
- Proposições assinadas.
- Temas mais frequentes nas proposições em que participou.

Uso na apresentação:

> Esta tela mostra uma visão individual de atuação parlamentar dentro da base.

## Espectro Político

Agrupa proposições de acordo com uma classificação simplificada de partidos.

Uso na apresentação:

> Esta tela é apenas uma visualização exploratória baseada nos partidos envolvidos. Ela não substitui análise política formal.

## Última Tramitação

Mostra a tramitação mais recente conhecida de cada proposição.

Ponto técnico importante:

- Usa subconsulta para obter a maior sequência de tramitação por proposição.
- Usa `LEFT JOIN` com `Orgao` para preservar tramitações mesmo se o órgão não estiver identificado.

Uso na apresentação:

> Esta tela mostra como acompanhar o estado mais recente de uma proposição dentro dos dados carregados.

## Tramitações Acima da Média

Lista proposições com quantidade de tramitações acima da média da base.

Ponto técnico importante:

- Usa agregação.
- Usa `GROUP BY`.
- Usa `HAVING`.
- Usa subconsulta para calcular a média.

Uso na apresentação:

> Esta tela ajuda a identificar proposições com maior movimentação no processo legislativo.

## Órgãos

Analisa a tabela `Orgao` junto com `Tramitacao`.

Mostra:

- Órgãos cadastrados.
- Tipos de órgão.
- Ranking por quantidade de tramitações.
- Proposições que passaram por um órgão selecionado.

Uso na apresentação:

> Esta tela aproveita melhor a dimensão institucional da tramitação legislativa.

## Temas Acima da Média

Mostra temas que aparecem em quantidade de proposições acima da média.

Ponto técnico importante:

- Usa `Tema`.
- Usa `Classificacao`.
- Usa agregação e subconsulta.

Uso na apresentação:

> Esta tela destaca os assuntos legislativos mais recorrentes na base.

## Glossário

Explica termos legislativos usados na aplicação.

Exemplos:

- Proposição.
- Projeto de Lei.
- Ementa.
- Autor.
- Partido.
- Tema.
- Órgão.
- Tramitação.
- Despacho.
- Comissão.
- Plenário.

Uso na apresentação:

> Esta tela reforça que a aplicação foi pensada também para usuários leigos.

## Exportação de Dados

Algumas tabelas possuem botão de download em CSV.

Uso:

- Permite salvar o recorte filtrado.
- Ajuda a gerar evidências para relatório.
- Facilita análise externa em planilhas.

## O Que a Aplicação Não Faz

A aplicação não faz:

- Cadastro de dados.
- Edição de registros.
- Exclusão de registros.
- Login de usuários.
- Análise jurídica automática.
- Previsão política.
- Consulta à API em tempo real durante o uso.

Todo conteúdo exibido vem do banco MySQL já populado.

## Roteiro Sugerido de Demonstração

1. Abrir a **Visão Geral** para mostrar os totais.
2. Abrir **Qualidade dos Dados** para mostrar cobertura e lacunas.
3. Usar **Entenda uma Proposição** para explicar um caso específico.
4. Mostrar **Ranking de Partidos** e **Ranking de Deputados**.
5. Mostrar **Proposições e Temas** destacando proposições sem tema.
6. Mostrar **Última Tramitação** e explicar a subconsulta.
7. Mostrar **Órgãos** para evidenciar o papel das tramitações.
8. Encerrar com o **Glossário** para reforçar o caráter didático.

## Mensagem Principal para a Apresentação

> A aplicação transforma um banco relacional com dados legislativos em uma ferramenta de consulta e visualização. Ela usa as consultas SQL da Parte 3, preserva o modelo físico da Parte 2 e apresenta os dados de forma acessível para usuários não técnicos.
