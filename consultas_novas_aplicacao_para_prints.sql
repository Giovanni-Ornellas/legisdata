/*
Consultas novas/auxiliares da aplicacao Streamlit
Banco de Dados I - ICP489

Este arquivo nao substitui as 6 consultas oficiais da Parte 3.
Ele reune consultas adicionais usadas na aplicacao Web para visao geral,
filtros, qualidade dos dados, orgaos, deputados e detalhamento de proposicoes.

Uso local:
mysql -h 127.0.0.1 -P 3307 -u bdi -p trabalho_final < consultas_novas_aplicacao_para_prints.sql
*/

USE trabalho_final;

-- Consulta A1 - Metricas gerais da aplicacao
-- Serve para exibir os cards da tela inicial: total de proposicoes,
-- deputados, partidos, temas, tramitacoes e relacoes de autoria.
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

-- Consulta A2 - Base unificada de proposicoes para filtros e busca
-- Serve como base principal da aplicacao. Junta proposicoes, temas,
-- autores, partidos, quantidade de tramitacoes e ultima tramitacao.
-- A consulta usa LEFT JOIN para manter proposicoes mesmo quando nao ha
-- tema, autor, tramitacao ou orgao associado.
SELECT
    pr.ID AS proposicao_id,
    CONCAT(pr.Sigla_tipo, ' ', pr.numero, '/', pr.ano) AS proposicao,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    LEFT(pr.ementa, 120) AS ementa,
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
    o.sigla AS sigla_orgao
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
    pr.ID DESC
LIMIT 10;

-- Consulta A3 - Indicadores de qualidade dos dados
-- Serve para a pagina de qualidade dos dados. Mostra cobertura tematica,
-- cobertura de autoria e cobertura de tramitacao, identificando lacunas
-- da carga feita a partir da API.
SELECT
    (SELECT COUNT(*) FROM Proposicao) AS total_proposicoes,
    (
        SELECT COUNT(*)
        FROM Proposicao pr
        WHERE NOT EXISTS (
            SELECT 1
            FROM Classificacao c
            WHERE c.fk_Proposicao_ID = pr.ID
        )
    ) AS proposicoes_sem_tema,
    (
        SELECT COUNT(*)
        FROM Proposicao pr
        WHERE NOT EXISTS (
            SELECT 1
            FROM Tramitacao tr
            WHERE tr.fk_Proposicao_ID = pr.ID
        )
    ) AS proposicoes_sem_tramitacao,
    (
        SELECT COUNT(*)
        FROM Proposicao pr
        WHERE NOT EXISTS (
            SELECT 1
            FROM Participa par
            WHERE par.fk_Proposicao_ID = pr.ID
        )
    ) AS proposicoes_sem_autores,
    (SELECT COUNT(*) FROM Participa) AS total_participa,
    (SELECT COUNT(*) FROM Classificacao) AS total_classificacao;

-- Consulta A4 - Listagem de orgaos cadastrados
-- Serve para a pagina de orgaos, permitindo consultar sigla, nome e tipo
-- de cada orgao registrado no banco.
SELECT
    ID AS orgao_id,
    sigla,
    nome,
    tipo_orgao
FROM Orgao
ORDER BY
    tipo_orgao,
    sigla,
    nome
LIMIT 20;

-- Consulta A5 - Ranking de orgaos por quantidade de tramitacoes
-- Serve para identificar quais orgaos aparecem com maior volume de
-- movimentacoes legislativas no banco.
SELECT
    o.ID AS orgao_id,
    o.sigla,
    o.nome,
    o.tipo_orgao,
    COUNT(tr.sequencia) AS quantidade_tramitacoes,
    COUNT(DISTINCT tr.fk_Proposicao_ID) AS quantidade_proposicoes
FROM Orgao o
LEFT JOIN Tramitacao tr
    ON tr.fk_Orgao_ID = o.ID
GROUP BY
    o.ID,
    o.sigla,
    o.nome,
    o.tipo_orgao
ORDER BY
    quantidade_tramitacoes DESC,
    sigla ASC
LIMIT 10;

-- Consulta A6 - Proposicoes que passaram por um orgao
-- Serve para detalhar um orgao selecionado na aplicacao. A variavel
-- @orgao_id escolhe automaticamente um orgao com tramitacoes para que
-- a consulta rode sem precisar editar o arquivo.
SET @orgao_id := (
    SELECT fk_Orgao_ID
    FROM Tramitacao
    WHERE fk_Orgao_ID IS NOT NULL
    GROUP BY fk_Orgao_ID
    ORDER BY COUNT(*) DESC
    LIMIT 1
);

SELECT
    pr.ID AS proposicao_id,
    CONCAT(pr.Sigla_tipo, ' ', pr.numero, '/', pr.ano) AS proposicao,
    LEFT(pr.ementa, 120) AS ementa,
    pr.data_apresentacao,
    tr.descricao_situacao,
    COUNT(tr.sequencia) AS quantidade_tramitacoes,
    MAX(tr.data_hora) AS ultima_tramitacao_no_orgao
FROM Tramitacao tr
JOIN Proposicao pr
    ON pr.ID = tr.fk_Proposicao_ID
WHERE tr.fk_Orgao_ID = @orgao_id
GROUP BY
    pr.ID,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    pr.data_apresentacao,
    tr.descricao_situacao
ORDER BY
    ultima_tramitacao_no_orgao DESC,
    quantidade_tramitacoes DESC
LIMIT 10;

-- Consulta A7 - Listagem de deputados para detalhamento
-- Serve para a pagina de deputado detalhado, mostrando dados cadastrais
-- basicos, partido e unidade federativa.
SELECT
    d.ID AS deputado_id,
    d.nome,
    d.sigla_uf,
    d.email,
    d.url_foto,
    p.sigla AS partido,
    p.nome AS nome_partido
FROM Deputado d
LEFT JOIN Partido p
    ON p.ID = d.fk_Partido_ID
ORDER BY
    d.nome
LIMIT 20;

-- Consulta A8 - Proposicoes assinadas por um deputado
-- Serve para detalhar a atuacao de um deputado selecionado. A variavel
-- @deputado_id escolhe automaticamente um deputado com autoria registrada.
SET @deputado_id := (
    SELECT fk_Deputado_ID
    FROM Participa
    GROUP BY fk_Deputado_ID
    ORDER BY COUNT(*) DESC
    LIMIT 1
);

SELECT
    pr.ID AS proposicao_id,
    CONCAT(pr.Sigla_tipo, ' ', pr.numero, '/', pr.ano) AS proposicao,
    LEFT(pr.ementa, 120) AS ementa,
    pr.data_apresentacao,
    pr.descricao_tipo,
    par.ordem_assinatura,
    par.proponente,
    COALESCE(
        GROUP_CONCAT(DISTINCT t.nome ORDER BY t.nome SEPARATOR ', '),
        'Sem tema associado'
    ) AS temas
FROM Participa par
JOIN Proposicao pr
    ON pr.ID = par.fk_Proposicao_ID
LEFT JOIN Classificacao c
    ON c.fk_Proposicao_ID = pr.ID
LEFT JOIN Tema t
    ON t.Cod = c.fk_Tema_Cod
WHERE par.fk_Deputado_ID = @deputado_id
GROUP BY
    pr.ID,
    pr.Sigla_tipo,
    pr.numero,
    pr.ano,
    pr.ementa,
    pr.data_apresentacao,
    pr.descricao_tipo,
    par.ordem_assinatura,
    par.proponente
ORDER BY
    pr.data_apresentacao DESC,
    pr.ID DESC
LIMIT 10;

-- Consulta A9 - Temas mais frequentes de um deputado
-- Serve para mostrar os assuntos mais recorrentes nas proposicoes em que
-- um deputado participou.
SELECT
    t.nome AS tema,
    COUNT(DISTINCT pr.ID) AS quantidade_proposicoes
FROM Participa par
JOIN Proposicao pr
    ON pr.ID = par.fk_Proposicao_ID
JOIN Classificacao c
    ON c.fk_Proposicao_ID = pr.ID
JOIN Tema t
    ON t.Cod = c.fk_Tema_Cod
WHERE par.fk_Deputado_ID = @deputado_id
GROUP BY
    t.nome
ORDER BY
    quantidade_proposicoes DESC,
    tema ASC
LIMIT 10;

-- Consulta A10 - Linha do tempo de uma proposicao
-- Serve para a pagina "Entenda uma Proposicao", exibindo as tramitacoes
-- de uma proposicao selecionada. A variavel @proposicao_id escolhe uma
-- proposicao com tramitacoes registradas.
SET @proposicao_id := (
    SELECT fk_Proposicao_ID
    FROM Tramitacao
    GROUP BY fk_Proposicao_ID
    ORDER BY COUNT(*) DESC
    LIMIT 1
);

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
WHERE tr.fk_Proposicao_ID = @proposicao_id
ORDER BY
    tr.data_hora DESC,
    tr.sequencia DESC
LIMIT 20;
