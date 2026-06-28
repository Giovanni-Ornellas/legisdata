# FAQ para Apresentação

Este documento reúne perguntas prováveis sobre o projeto e respostas curtas para apoiar o grupo durante a apresentação.

## 1. Qual é o objetivo principal do projeto?

O objetivo é coletar, organizar e visualizar dados legislativos da Câmara dos Deputados em um banco relacional MySQL, usando uma aplicação Web em Streamlit para consulta e análise dos dados.

## 2. Qual foi a fonte dos dados?

Os dados vieram da API de Dados Abertos da Câmara dos Deputados. A coleta foi feita por script Python e os dados foram armazenados em tabelas relacionais no MySQL.

## 3. O banco usado é relacional?

Sim. O projeto usa MySQL e o modelo possui entidades, chaves primárias, chaves estrangeiras e tabelas associativas, como `Participa` e `Classificacao`.

## 4. A aplicação altera dados no banco?

Não. A aplicação Streamlit é somente de leitura. Ela executa consultas `SELECT` e não faz `INSERT`, `UPDATE`, `DELETE` ou `DROP`.

## 5. Por que foi usado Streamlit?

Porque o Streamlit permite criar uma aplicação Web interativa em Python com baixo custo de implementação. Ele é adequado para dashboards, filtros, tabelas, métricas e gráficos, que são o foco do trabalho.

## 6. Por que foi usado MySQL?

Porque o trabalho exige banco relacional e o modelo físico foi criado em MySQL. Além disso, o MySQL é compatível com execução local via Docker e hospedagem em nuvem pelo Aiven.

## 7. Qual é o papel do Aiven no projeto?

O Aiven hospeda o banco MySQL na nuvem. Isso permite que a aplicação publicada no Streamlit Cloud acesse o banco sem depender da máquina local.

## 8. As credenciais do Aiven estão no GitHub?

Não. Credenciais reais ficam em arquivos locais ignorados pelo Git ou nos Secrets do Streamlit Cloud. O repositório contém apenas exemplos sem senha real.

## 9. Qual é a função da tabela `Participa`?

`Participa` representa a relação de autoria entre deputados e proposições. Ela liga `Deputado` a `Proposicao` e permite saber quais deputados participaram ou assinaram uma proposição.

## 10. Por que `Participa` é tão importante?

Porque várias análises dependem dela, especialmente ranking de partidos e ranking de deputados. Se essa tabela estivesse vazia, as consultas de autoria não teriam resultado útil.

## 11. Qual é a função da tabela `Classificacao`?

`Classificacao` representa a relação entre proposições e temas. Ela liga `Proposicao` a `Tema`, permitindo analisar os assuntos tratados nas proposições.

## 12. Por que algumas proposições aparecem sem tema?

Porque nem toda proposição possui classificação temática retornada pela fonte ou coletada no recorte usado. A aplicação mostra essa ausência em vez de esconder o registro.

## 13. Por que foi usado `LEFT JOIN` na consulta de proposições e temas?

Para preservar proposições sem tema associado. Com `INNER JOIN`, essas proposições desapareceriam da listagem, o que esconderia uma lacuna real dos dados.

## 14. Por que foi usado `LEFT JOIN` com `Orgao` na última tramitação?

Para manter a tramitação mesmo quando o órgão associado não estiver identificado. Assim, a aplicação não perde uma movimentação válida por ausência de dados do órgão.

## 15. O que é uma tramitação?

É um registro de movimentação da proposição no processo legislativo. Pode indicar apresentação, recebimento, despacho, publicação, arquivamento ou outro andamento.

## 16. Como a aplicação identifica a última tramitação?

Ela usa uma subconsulta correlacionada para selecionar a maior sequência de tramitação de cada proposição.

## 17. Por que usar subconsulta na consulta de última tramitação?

Porque é necessário comparar cada proposição com suas próprias tramitações e recuperar apenas o registro de maior sequência.

## 18. O que significa “temas acima da média”?

São temas que aparecem em uma quantidade de proposições superior à média de proposições por tema na base carregada.

## 19. O que significa “tramitações acima da média”?

São proposições que possuem mais registros de tramitação do que a média das proposições com tramitação carregada.

## 20. Ter muitas tramitações significa que uma proposição é mais importante?

Não necessariamente. Significa apenas que há mais movimentações registradas no banco. A aplicação não faz julgamento político ou jurídico.

## 21. A aplicação interpreta juridicamente as proposições?

Não. Ela apresenta os dados disponíveis no banco e textos explicativos curtos. Não gera conclusão jurídica, política ou preditiva.

## 22. Por que há uma página de qualidade dos dados?

Para mostrar a cobertura e as lacunas da carga. Isso torna a análise mais transparente, especialmente em relação a proposições sem tema, sem autores ou sem tramitação.

## 23. O que significa cobertura temática?

É a proporção de proposições que possuem pelo menos um tema associado na tabela `Classificacao`.

## 24. O que significa cobertura de autoria?

É a proporção de proposições que possuem pelo menos um deputado associado pela tabela `Participa`.

## 25. O que significa cobertura de tramitação?

É a proporção de proposições que possuem pelo menos um registro na tabela `Tramitacao`.

## 26. Por que nem todos os autores foram carregados?

Porque a coleta priorizou autores identificados como deputados. Autores que não eram deputados ou que não tinham identificador adequado foram ignorados para preservar a integridade das chaves estrangeiras.

## 27. O grupo inventou algum dado para preencher lacunas?

Não. Campos ausentes foram mantidos como nulos ou tratados na interface como “sem tema”, “sem partido” ou “sem deputado identificado”, conforme o caso.

## 28. Como o script evita duplicatas?

Os inserts usam `INSERT ... ON DUPLICATE KEY UPDATE`. Além disso, o script consulta IDs de proposições já existentes antes de fazer cargas incrementais.

## 29. Por que há dados de 2025 e 2026?

Porque a carga foi ampliada para cobrir proposições desses anos. O script permite carregar mais de um ano usando `ANOS_PROPOSICOES=2025,2026`.

## 30. Por que a data de apresentação pode não bater exatamente com o campo `ano`?

Porque o campo `ano` vem da própria proposição na API, enquanto `data_apresentacao` é uma data específica. Em alguns casos, uma proposição associada a um ano pode ter movimentações ou apresentação em período próximo ou posterior.

## 31. Onde estão as consultas oficiais da Parte 3?

No arquivo:

```text
sql/parte3_consultas.sql
```

E documentadas em:

```text
relatorio/parte3_consultas.md
```

## 32. A aplicação usa exatamente só as seis consultas da Parte 3?

Não. Ela usa as seis consultas principais e também consultas auxiliares para filtros, qualidade dos dados, órgãos, deputados e detalhamento de proposições.

## 33. Isso descaracteriza a Parte 3?

Não. As seis consultas da Parte 3 continuam preservadas. As consultas adicionais existem para melhorar a aplicação Web e explorar melhor as tabelas do banco.

## 34. Onde ficam as consultas usadas pela aplicação?

No arquivo:

```text
src/queries.py
```

Isso evita espalhar SQL pelas páginas da interface.

## 35. Por que separar `queries.py`, `services.py` e `views/`?

Para manter o projeto organizado. `queries.py` guarda SQL, `services.py` executa e prepara os dados, e `views/` mostra a interface ao usuário.

## 36. Qual é o fluxo de dados da aplicação?

O fluxo recomendado é:

```text
View -> Service -> Query -> Database
```

A tela chama um service, o service usa uma query, a query é executada no banco e o resultado volta como `DataFrame`.

## 37. Por que usar cache no Streamlit?

Para evitar reconectar e reexecutar consultas desnecessariamente a cada interação do usuário. Isso melhora desempenho e estabilidade.

## 38. O que acontece se uma consulta retorna vazia?

A aplicação mostra uma mensagem amigável, como “Nenhum resultado encontrado com os filtros atuais”. Isso evita erro visual e ajuda o usuário a ajustar filtros.

## 39. Por que a busca às vezes retorna zero resultados?

Porque os filtros são combinados. Uma palavra pode existir no banco, mas desaparecer quando combinada com partido, tema, situação ou período que não correspondem.

## 40. Como a aplicação trata isso?

A barra lateral mostra quantos registros restam no recorte. Se a palavra-chave existe, mas outros filtros removem os resultados, a aplicação avisa.

## 41. Qual é a página mais importante para explicar uma proposição específica?

A página **Entenda uma Proposição**. Ela mostra tipo, número, ano, ementa, autores, partidos, temas, situação e linha do tempo de tramitações.

## 42. Para que serve o glossário?

Serve para explicar termos legislativos em linguagem simples, como proposição, ementa, tramitação, despacho, comissão e plenário.

## 43. Por que a aplicação tem uma página de metodologia?

Para explicar a origem dos dados, o recorte da carga, as tabelas populadas e as limitações encontradas.

## 44. Como o banco local foi populado?

Por meio do script:

```bash
python scripts/popular_banco.py
```

Ele consulta a API da Câmara e insere os dados nas tabelas do MySQL.

## 45. Como os dados foram levados para o Aiven?

Por meio do script:

```bash
python scripts/sincronizar_aiven.py
```

Ele copia dados do MySQL local para o MySQL do Aiven usando operação incremental.

## 46. Como validar se as tabelas estão populadas?

Com:

```bash
python scripts/validar_banco.py
```

O script mostra contagens e amostras de todas as tabelas.

## 47. Como validar se as consultas da Parte 3 funcionam?

Com:

```bash
python scripts/validar_consultas_parte3.py
```

Ele executa as seis consultas principais e informa se cada uma retornou com sucesso.

## 48. Quais foram as contagens finais principais?

Na carga atual:

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

## 49. O projeto poderia carregar mais dados?

Sim, mas isso deve ser feito de forma incremental e validada. A tabela `Participa` cresce bastante, então cargas maiores podem impactar tempo de coleta e desempenho.

## 50. Qual é uma limitação importante do projeto?

O projeto depende da qualidade e disponibilidade dos dados retornados pela API. Além disso, o recorte carregado não representa necessariamente todo o universo legislativo da Câmara.

## 51. Por que não usar uma API em tempo real na aplicação?

Porque o foco do trabalho é banco de dados relacional. A aplicação consulta o MySQL já populado, garantindo consistência e permitindo demonstrar modelagem, carga e consultas SQL.

## 52. Por que não foi feito CRUD?

Porque o escopo do trabalho é análise e visualização dos dados. Além disso, os dados vêm de fonte pública oficial e não devem ser editados pela aplicação.

## 53. O que aconteceria se a tabela `Participa` estivesse vazia?

Rankings por partido e deputado perderiam sentido, pois não haveria autoria associada às proposições.

## 54. O que aconteceria se a tabela `Classificacao` estivesse vazia?

Análises por tema ficariam vazias ou apareceriam como “sem tema associado”. A consulta com `LEFT JOIN` ainda mostraria as proposições.

## 55. Como demonstrar o uso de JOIN na apresentação?

Uma boa opção é mostrar o ranking de partidos, que une `Partido`, `Deputado`, `Participa` e `Proposicao`.

## 56. Como demonstrar o uso de `LEFT JOIN`?

Mostrar a tela **Proposições e Temas** ou a Consulta 3, explicando que proposições sem tema continuam aparecendo.

## 57. Como demonstrar o uso de subconsulta?

Mostrar a Consulta 4, que pega a maior sequência de tramitação, ou as consultas 5 e 6, que comparam valores com médias calculadas por subconsultas.

## 58. Como demonstrar agregação?

Mostrar rankings e contagens, como quantidade de proposições por partido, quantidade de proposições por tema ou quantidade de tramitações por proposição.

## 59. O que o grupo faria se tivesse mais tempo?

Poderia ampliar a carga de dados, melhorar filtros avançados, incluir mais recortes temporais e criar novas visualizações analíticas, mantendo a aplicação somente leitura.

## 60. Qual é a principal mensagem do projeto?

O projeto mostra como dados públicos legislativos podem ser coletados, modelados em um banco relacional, consultados com SQL e apresentados em uma aplicação Web didática e interativa.
