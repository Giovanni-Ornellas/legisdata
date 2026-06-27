# 3.4 Consultas

Esta seção apresenta as consultas SQL formuladas para a terceira parte do trabalho. As consultas foram elaboradas para o SGBD MySQL e têm como objetivo apoiar a futura aplicação Streamlit de análise e visualização de dados legislativos da Câmara dos Deputados. Todas as consultas utilizam apenas comandos de leitura.

Antes da execução das consultas, recomenda-se verificar a quantidade de registros em cada tabela do banco. A tabela `Participa` deve receber atenção especial, pois representa a relação de autoria entre deputados e proposições. Caso essa tabela esteja vazia, as Consultas 1 e 2 não retornarão resultados, pois dependem diretamente dos dados reais de autoria carregados no banco.

```sql
SELECT 'Partido' AS tabela, COUNT(*) AS quantidade FROM Partido
UNION ALL
SELECT 'Orgao' AS tabela, COUNT(*) AS quantidade FROM Orgao
UNION ALL
SELECT 'Tema' AS tabela, COUNT(*) AS quantidade FROM Tema
UNION ALL
SELECT 'Proposicao' AS tabela, COUNT(*) AS quantidade FROM Proposicao
UNION ALL
SELECT 'Deputado' AS tabela, COUNT(*) AS quantidade FROM Deputado
UNION ALL
SELECT 'Tramitacao' AS tabela, COUNT(*) AS quantidade FROM Tramitacao
UNION ALL
SELECT 'Participa' AS tabela, COUNT(*) AS quantidade FROM Participa
UNION ALL
SELECT 'Classificacao' AS tabela, COUNT(*) AS quantidade FROM Classificacao;
```

## Consulta 1 — Ranking de partidos por quantidade de proposições com autoria

### Objetivo

Retornar um ranking dos partidos políticos conforme a quantidade de proposições associadas a seus deputados por meio da tabela de autoria `Participa`. A consulta também informa quantos deputados distintos de cada partido aparecem como autores na base.

### Relevância para a aplicação Web

Essa consulta pode alimentar um painel estatístico ou dashboard de participação legislativa por partido, permitindo identificar quais legendas possuem maior volume de proposições com autoria registrada.

### SQL

```sql
SELECT
    pa.ID AS partido_id,
    pa.sigla AS partido,
    pa.nome AS nome_partido,
    COUNT(DISTINCT pr.ID) AS quantidade_proposicoes,
    COUNT(DISTINCT d.ID) AS quantidade_deputados_autores
FROM Partido pa
JOIN Deputado d
    ON d.fk_Partido_ID = pa.ID
JOIN Participa par
    ON par.fk_Deputado_ID = d.ID
JOIN Proposicao pr
    ON pr.ID = par.fk_Proposicao_ID
GROUP BY
    pa.ID,
    pa.sigla,
    pa.nome
ORDER BY
    quantidade_proposicoes DESC,
    partido ASC;
```

### Requisitos atendidos

- JOIN: sim
- Mais de um JOIN: sim
- Junção externa: não
- Agregação: sim
- GROUP BY: sim
- Subconsulta: não

### Resultado

Inserir a captura de tela da execução no MySQL. Caso a consulta retorne muitos registros, utilizar a versão auxiliar com `LIMIT 10` disponível em `sql/parte3_consultas.sql`.

## Consulta 2 — Deputados com maior número de proposições assinadas

### Objetivo

Listar os deputados com maior número de proposições assinadas, mostrando também a sigla da unidade federativa, o partido e a quantidade de participações em que o deputado aparece como proponente.

### Relevância para a aplicação Web

Essa consulta pode ser usada em uma página de ranking de parlamentares, permitindo destacar deputados com maior volume de atuação legislativa na base de dados carregada.

### SQL

```sql
SELECT
    d.ID AS deputado_id,
    d.nome AS deputado,
    d.sigla_uf,
    pa.sigla AS partido,
    COUNT(DISTINCT pr.ID) AS quantidade_proposicoes_assinadas,
    SUM(CASE WHEN par.proponente = TRUE THEN 1 ELSE 0 END) AS quantidade_como_proponente
FROM Deputado d
JOIN Partido pa
    ON pa.ID = d.fk_Partido_ID
JOIN Participa par
    ON par.fk_Deputado_ID = d.ID
JOIN Proposicao pr
    ON pr.ID = par.fk_Proposicao_ID
GROUP BY
    d.ID,
    d.nome,
    d.sigla_uf,
    pa.sigla
ORDER BY
    quantidade_proposicoes_assinadas DESC,
    deputado ASC;
```

### Requisitos atendidos

- JOIN: sim
- Mais de um JOIN: sim
- Junção externa: não
- Agregação: sim
- GROUP BY: sim
- Subconsulta: não

### Resultado

Inserir a captura de tela da execução no MySQL. Caso a tabela `Participa` esteja vazia, registrar no relatório que não há dados reais de autoria suficientes para gerar o ranking. Não devem ser criados dados artificiais apenas para essa consulta.

## Consulta 3 — Proposições com seus temas, mantendo proposições sem classificação temática

### Objetivo

Retornar uma listagem de proposições acompanhadas de seus temas associados. Quando uma proposição não possuir classificação temática, ela continua aparecendo no resultado com a indicação de ausência de tema.

### Relevância para a aplicação Web

Essa consulta é adequada para uma página geral de listagem ou busca de proposições, pois evita que proposições incompletas sejam removidas da visualização apenas por não possuírem registro correspondente em `Classificacao` ou `Tema`.

### SQL

```sql
SELECT
    pr.ID AS proposicao_id,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    COALESCE(GROUP_CONCAT(DISTINCT t.nome ORDER BY t.nome SEPARATOR ', '), 'Sem tema associado') AS temas
FROM Proposicao pr
LEFT JOIN Classificacao c
    ON c.fk_Proposicao_ID = pr.ID
LEFT JOIN Tema t
    ON t.Cod = c.fk_Tema_Cod
GROUP BY
    pr.ID,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa
ORDER BY
    pr.ano DESC,
    pr.numero DESC,
    pr.ID DESC;
```

**Justificativa da junção externa:**
Foi utilizado `LEFT JOIN` porque a consulta deve preservar todas as proposições, inclusive aquelas que não tenham classificação temática cadastrada. Com `INNER JOIN`, proposições sem correspondência em `Classificacao` ou `Tema` seriam removidas do resultado, o que prejudicaria uma listagem geral da aplicação. Na carga local utilizada para teste, foram identificadas 36 proposições sem tema associado, confirmando que a junção externa faz diferença real no resultado.

### Requisitos atendidos

- JOIN: sim
- Mais de um JOIN: sim
- Junção externa: sim
- Agregação: sim
- GROUP BY: sim
- Subconsulta: não

### Resultado

Inserir a captura de tela da execução no MySQL. Caso a consulta retorne muitos registros, utilizar a versão auxiliar com `LIMIT 10` disponível em `sql/parte3_consultas.sql`.

## Consulta 4 — Última tramitação conhecida de cada proposição

### Objetivo

Retornar, para cada proposição com tramitação registrada, a última tramitação conhecida, considerando a maior sequência de tramitação associada à proposição. A consulta também apresenta informações do órgão responsável, quando disponível.

### Relevância para a aplicação Web

Essa consulta é útil para uma página de acompanhamento da situação atual de cada proposição, pois permite exibir o estado mais recente do processo legislativo sem listar todo o histórico de tramitações.

### SQL

```sql
SELECT
    pr.ID AS proposicao_id,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    tr.sequencia,
    tr.data_hora,
    tr.descricao_situacao,
    tr.descricao_tramitacao,
    o.sigla AS sigla_orgao,
    o.nome AS nome_orgao
FROM Proposicao pr
JOIN Tramitacao tr
    ON tr.fk_Proposicao_ID = pr.ID
    AND tr.sequencia = (
        SELECT MAX(tr2.sequencia)
        FROM Tramitacao tr2
        WHERE tr2.fk_Proposicao_ID = pr.ID
    )
LEFT JOIN Orgao o
    ON o.ID = tr.fk_Orgao_ID
ORDER BY
    tr.data_hora DESC,
    pr.ID DESC;
```

**Justificativa da subconsulta:**
A subconsulta correlacionada calcula a maior sequência de tramitação para a proposição analisada na linha externa. Dessa forma, a consulta recupera de modo consistente apenas o último registro de tramitação de cada proposição.

**Justificativa da junção externa:**
Foi utilizado `LEFT JOIN` com `Orgao` para preservar a tramitação mais recente mesmo quando o órgão associado não estiver identificado na base. Com `INNER JOIN`, uma tramitação válida poderia ser omitida do acompanhamento da proposição por ausência de correspondência na tabela `Orgao`.

### Requisitos atendidos

- JOIN: sim
- Mais de um JOIN: sim
- Junção externa: sim
- Agregação: sim
- GROUP BY: não
- Subconsulta: sim

### Resultado

Inserir a captura de tela da execução no MySQL. Caso a consulta retorne muitos registros, utilizar a versão auxiliar com `LIMIT 10` disponível em `sql/parte3_consultas.sql`.

## Consulta 5 — Temas com quantidade de proposições acima da média

### Objetivo

Identificar os temas legislativos cuja quantidade de proposições classificadas é superior à média de proposições por tema.

### Relevância para a aplicação Web

Essa consulta pode ser utilizada em dashboards e páginas de análise temática para destacar assuntos mais recorrentes na base de proposições legislativas.

### SQL

```sql
SELECT
    t.Cod AS tema_cod,
    t.nome AS tema,
    COUNT(DISTINCT c.fk_Proposicao_ID) AS quantidade_proposicoes
FROM Tema t
JOIN Classificacao c
    ON c.fk_Tema_Cod = t.Cod
GROUP BY
    t.Cod,
    t.nome
HAVING COUNT(DISTINCT c.fk_Proposicao_ID) > (
    SELECT AVG(media_temas.quantidade_por_tema)
    FROM (
        SELECT
            t2.Cod,
            COUNT(DISTINCT c2.fk_Proposicao_ID) AS quantidade_por_tema
        FROM Tema t2
        LEFT JOIN Classificacao c2
            ON c2.fk_Tema_Cod = t2.Cod
        GROUP BY
            t2.Cod
    ) AS media_temas
)
ORDER BY
    quantidade_proposicoes DESC,
    tema ASC;
```

**Justificativa da subconsulta:**
A subconsulta interna calcula a quantidade de proposições por tema, incluindo temas sem proposições por meio de `LEFT JOIN`. A subconsulta externa calcula a média dessas quantidades. O `HAVING` compara cada tema com essa média derivada, selecionando apenas os temas acima do comportamento médio da base.

### Requisitos atendidos

- JOIN: sim
- Mais de um JOIN: não
- Junção externa: sim
- Agregação: sim
- GROUP BY: sim
- Subconsulta: sim

### Resultado

Inserir a captura de tela da execução no MySQL. Caso a consulta retorne muitos registros, utilizar a versão auxiliar com `LIMIT 10` disponível em `sql/parte3_consultas.sql`.

## Consulta 6 — Proposições com número de tramitações acima da média

### Objetivo

Listar proposições cujo número de tramitações registradas é superior à média de tramitações por proposição.

### Relevância para a aplicação Web

Essa consulta permite identificar proposições com tramitação mais intensa ou complexa, o que pode ser explorado em telas de monitoramento legislativo, filtros de prioridade ou painéis analíticos.

### SQL

```sql
SELECT
    pr.ID AS proposicao_id,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    COUNT(tr.sequencia) AS quantidade_tramitacoes
FROM Proposicao pr
JOIN Tramitacao tr
    ON tr.fk_Proposicao_ID = pr.ID
GROUP BY
    pr.ID,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa
HAVING COUNT(tr.sequencia) > (
    SELECT AVG(media_tramitacoes.quantidade_por_proposicao)
    FROM (
        SELECT
            tr2.fk_Proposicao_ID,
            COUNT(*) AS quantidade_por_proposicao
        FROM Tramitacao tr2
        GROUP BY
            tr2.fk_Proposicao_ID
    ) AS media_tramitacoes
)
ORDER BY
    quantidade_tramitacoes DESC,
    pr.ano DESC,
    pr.numero DESC;
```

**Justificativa da subconsulta:**
A subconsulta gera uma tabela derivada com a quantidade de tramitações por proposição. Em seguida, calcula-se a média dessas quantidades, permitindo que a consulta principal retorne apenas proposições com movimentação acima da média.

### Requisitos atendidos

- JOIN: sim
- Mais de um JOIN: não
- Junção externa: não
- Agregação: sim
- GROUP BY: sim
- Subconsulta: sim

### Resultado

Inserir a captura de tela da execução no MySQL. Caso a consulta retorne muitos registros, utilizar a versão auxiliar com `LIMIT 10` disponível em `sql/parte3_consultas.sql`.

## Validação dos requisitos da Parte 3

| Consulta | JOIN | Mais de um JOIN | Junção externa | Agregação | GROUP BY | Subconsulta |
|---|---|---|---|---|---|---|
| Consulta 1 | Sim | Sim | Não | Sim | Sim | Não |
| Consulta 2 | Sim | Sim | Não | Sim | Sim | Não |
| Consulta 3 | Sim | Sim | Sim | Sim | Sim | Não |
| Consulta 4 | Sim | Sim | Sim | Sim | Não | Sim |
| Consulta 5 | Sim | Não | Sim | Sim | Sim | Sim |
| Consulta 6 | Sim | Não | Não | Sim | Sim | Sim |

Com esse conjunto, os requisitos mínimos são atendidos: ao menos três consultas utilizam `JOIN`; há uso de junção externa em consultas nas quais ela preserva registros relevantes; mais de uma consulta utiliza múltiplas junções; há uso recorrente de funções de agregação; há agrupamento com `GROUP BY`; e há subconsultas aninhadas aplicadas de forma lógica para seleção de últimos registros e comparação com médias derivadas.

## Comandos para geração de evidências

Para gerar as evidências da carga e das consultas no MySQL local, podem ser utilizados os comandos abaixo:

```bash
python scripts/validar_banco.py
mysql -h 127.0.0.1 -P 3307 -u bdi -p trabalho_final < sql/parte3_consultas.sql
```

Para capturas mais legíveis, recomenda-se executar as versões auxiliares com `LIMIT 10` presentes em `sql/parte3_consultas.sql`, consulta por consulta, no cliente MySQL.
