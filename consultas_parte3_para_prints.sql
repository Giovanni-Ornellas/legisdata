/*
Consultas para prints da Parte 3
Banco de Dados I - ICP489

Uso local:
mysql -h 127.0.0.1 -P 3307 -u bdi -p trabalho_final < consultas_parte3_para_prints.sql
*/

USE trabalho_final;

-- Contagens das tabelas
SELECT 'Partido' AS tabela, COUNT(*) AS quantidade FROM Partido
UNION ALL
SELECT 'Orgao', COUNT(*) FROM Orgao
UNION ALL
SELECT 'Tema', COUNT(*) FROM Tema
UNION ALL
SELECT 'Proposicao', COUNT(*) FROM Proposicao
UNION ALL
SELECT 'Deputado', COUNT(*) FROM Deputado
UNION ALL
SELECT 'Tramitacao', COUNT(*) FROM Tramitacao
UNION ALL
SELECT 'Participa', COUNT(*) FROM Participa
UNION ALL
SELECT 'Classificacao', COUNT(*) FROM Classificacao;

-- Consulta 1 - Ranking de partidos por quantidade de proposicoes com autoria
SELECT
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

-- Consulta 2 - Deputados com maior numero de proposicoes assinadas
SELECT
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

-- Consulta 3 - Proposicoes e seus temas, mantendo proposicoes sem tema
SELECT
    pr.ID AS proposicao_id,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    LEFT(pr.ementa, 120) AS ementa,
    COALESCE(
        GROUP_CONCAT(DISTINCT t.nome ORDER BY t.nome SEPARATOR ', '),
        'Sem tema associado'
    ) AS temas
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

-- Consulta 4 - Ultima tramitacao conhecida de cada proposicao
SELECT
    pr.ID AS proposicao_id,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    tr.sequencia,
    tr.data_hora,
    tr.descricao_situacao,
    tr.descricao_tramitacao,
    o.sigla AS sigla_orgao
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

-- Consulta 5 - Temas com quantidade de proposicoes acima da media
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

-- Consulta 6 - Proposicoes com numero de tramitacoes acima da media
SELECT
    pr.ID AS proposicao_id,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    LEFT(pr.ementa, 120) AS ementa,
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
