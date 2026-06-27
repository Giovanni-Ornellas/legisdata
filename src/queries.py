COUNT_QUERY = """
SELECT 'Proposições' AS metrica, COUNT(*) AS total FROM Proposicao
UNION ALL
SELECT 'Deputados' AS metrica, COUNT(*) AS total FROM Deputado
UNION ALL
SELECT 'Partidos' AS metrica, COUNT(*) AS total FROM Partido
UNION ALL
SELECT 'Temas' AS metrica, COUNT(*) AS total FROM Tema
UNION ALL
SELECT 'Tramitações' AS metrica, COUNT(*) AS total FROM Tramitacao
UNION ALL
SELECT 'Autorias' AS metrica, COUNT(*) AS total FROM Participa;
"""

RANKING_PARTIDOS_QUERY = """
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
"""

RANKING_DEPUTADOS_QUERY = """
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
"""

TEMAS_ACIMA_MEDIA_QUERY = """
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
"""

TRAMITACOES_ACIMA_MEDIA_QUERY = """
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
"""

BASE_PROPOSICOES_QUERY = """
SELECT
    pr.ID AS proposicao_id,
    CONCAT(pr.Sigla_tipo, ' ', pr.numero, '/', pr.ano) AS proposicao,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    pr.data_apresentacao,
    pr.descricao_tipo,
    COALESCE(temas.temas, 'Sem tema associado') AS temas,
    COALESCE(autores.autores, 'Sem deputado identificado') AS autores,
    COALESCE(autores.partidos, 'Sem partido identificado') AS partidos,
    COALESCE(autores.quantidade_autores, 0) AS quantidade_autores,
    COALESCE(tram.total_tramitacoes, 0) AS quantidade_tramitacoes,
    ult.data_hora AS data_ultima_tramitacao,
    ult.descricao_situacao,
    ult.descricao_tramitacao,
    o.sigla AS sigla_orgao,
    o.nome AS nome_orgao,
    CONCAT(
        'https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=',
        pr.ID
    ) AS link_camara
FROM Proposicao pr
LEFT JOIN (
    SELECT
        c.fk_Proposicao_ID,
        GROUP_CONCAT(DISTINCT t.nome ORDER BY t.nome SEPARATOR ', ') AS temas
    FROM Classificacao c
    JOIN Tema t
        ON t.Cod = c.fk_Tema_Cod
    GROUP BY
        c.fk_Proposicao_ID
) temas
    ON temas.fk_Proposicao_ID = pr.ID
LEFT JOIN (
    SELECT
        par.fk_Proposicao_ID,
        GROUP_CONCAT(DISTINCT d.nome ORDER BY par.ordem_assinatura SEPARATOR ', ') AS autores,
        GROUP_CONCAT(DISTINCT pa.sigla ORDER BY pa.sigla SEPARATOR ', ') AS partidos,
        COUNT(DISTINCT d.ID) AS quantidade_autores
    FROM Participa par
    JOIN Deputado d
        ON d.ID = par.fk_Deputado_ID
    LEFT JOIN Partido pa
        ON pa.ID = d.fk_Partido_ID
    GROUP BY
        par.fk_Proposicao_ID
) autores
    ON autores.fk_Proposicao_ID = pr.ID
LEFT JOIN (
    SELECT
        fk_Proposicao_ID,
        COUNT(*) AS total_tramitacoes
    FROM Tramitacao
    GROUP BY
        fk_Proposicao_ID
) tram
    ON tram.fk_Proposicao_ID = pr.ID
LEFT JOIN Tramitacao ult
    ON ult.fk_Proposicao_ID = pr.ID
    AND ult.sequencia = (
        SELECT MAX(t2.sequencia)
        FROM Tramitacao t2
        WHERE t2.fk_Proposicao_ID = pr.ID
    )
LEFT JOIN Orgao o
    ON o.ID = ult.fk_Orgao_ID
ORDER BY
    pr.data_apresentacao DESC,
    pr.ID DESC;
"""

TRAMITACOES_PROPOSICAO_QUERY = """
SELECT
    tr.sequencia,
    tr.data_hora,
    tr.descricao_tramitacao,
    tr.descricao_situacao,
    tr.despacho,
    tr.apreciacao,
    o.sigla AS sigla_orgao,
    o.nome AS nome_orgao
FROM Tramitacao tr
LEFT JOIN Orgao o
    ON o.ID = tr.fk_Orgao_ID
WHERE tr.fk_Proposicao_ID = %s
ORDER BY
    tr.data_hora DESC,
    tr.sequencia DESC;
"""
