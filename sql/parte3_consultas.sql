/*
Parte 3 - Consultas SQL
Banco de Dados I - ICP489

Banco esperado: MySQL
Observacao: este arquivo contem apenas consultas SELECT e nao altera dados
nem estrutura do banco.
*/

USE trabalho_final;

/*
Verificacao inicial da quantidade de registros em cada tabela.
A contagem de Participa deve ser observada com atencao, pois as consultas
1 e 2 dependem da relacao de autoria entre deputados e proposicoes.
*/
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

/*
Consulta 1 - Ranking de partidos por quantidade de proposicoes com autoria.
Objetivo: ranking/dashboard de partidos com maior participacao legislativa.
*/
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

-- Versao auxiliar para captura de tela.
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
    partido ASC
LIMIT 10;

/*
Consulta 2 - Deputados com maior numero de proposicoes assinadas.
Objetivo: ranking de parlamentares mais ativos na base carregada.
*/
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

-- Versao auxiliar para captura de tela.
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
    deputado ASC
LIMIT 10;

/*
Consulta 3 - Proposicoes com seus temas, mantendo proposicoes sem classificacao.
Objetivo: listagem geral de proposicoes com temas, sem excluir registros
incompletos. O LEFT JOIN preserva proposicoes que nao tenham registro
correspondente em Classificacao ou Tema.
*/
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

-- Versao auxiliar para captura de tela.
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
    pr.ID DESC
LIMIT 10;

/*
Consulta 4 - Ultima tramitacao conhecida de cada proposicao.
Objetivo: acompanhamento do status atual de cada proposicao. A subconsulta
correlacionada seleciona a maior sequencia de tramitacao para cada proposicao.
*/
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

-- Versao auxiliar para captura de tela.
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
    pr.ID DESC
LIMIT 10;

/*
Consulta 5 - Temas com quantidade de proposicoes acima da media.
Objetivo: destacar temas legislativos mais recorrentes. A subconsulta calcula
a media de proposicoes por tema e o HAVING compara cada tema com essa media.
*/
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

-- Versao auxiliar para captura de tela.
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
    tema ASC
LIMIT 10;

/*
Consulta 6 - Proposicoes com numero de tramitacoes acima da media.
Objetivo: identificar proposicoes com tramitacao mais intensa ou complexa.
A subconsulta calcula a media de tramitacoes por proposicao com tramitacao
registrada.
*/
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

-- Versao auxiliar para captura de tela.
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
    pr.numero DESC
LIMIT 10;
