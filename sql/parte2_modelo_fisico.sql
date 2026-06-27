/*
Parte 2 - Modelo fisico
Banco de Dados I - ICP489

Script de criacao do banco relacional em MySQL para dados legislativos
da Camara dos Deputados. O script e idempotente para criacao inicial:
nao remove tabelas nem apaga dados existentes.
*/

CREATE DATABASE IF NOT EXISTS trabalho_final
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE trabalho_final;

CREATE TABLE IF NOT EXISTS Partido (
    ID INTEGER PRIMARY KEY,
    sigla VARCHAR(15),
    nome VARCHAR(255)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Orgao (
    ID INTEGER PRIMARY KEY,
    sigla VARCHAR(20),
    nome VARCHAR(255),
    tipo_orgao VARCHAR(100)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Tema (
    Cod INTEGER PRIMARY KEY,
    nome VARCHAR(255),
    descricao TEXT
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Proposicao (
    ID BIGINT PRIMARY KEY,
    Sigla_tipo VARCHAR(10),
    Cod_tipo VARCHAR(20),
    numero INTEGER,
    ano INTEGER,
    ementa TEXT,
    data_apresentacao DATE,
    descricao_tipo VARCHAR(255),
    INDEX idx_proposicao_tipo_ano_numero (Sigla_tipo, ano, numero),
    INDEX idx_proposicao_data_apresentacao (data_apresentacao)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Deputado (
    ID INTEGER PRIMARY KEY,
    nome VARCHAR(255),
    sigla_uf CHAR(2),
    url_foto VARCHAR(500),
    email VARCHAR(255),
    fk_Partido_ID INTEGER,
    INDEX idx_deputado_partido (fk_Partido_ID),
    CONSTRAINT FK_Deputado_Partido
        FOREIGN KEY (fk_Partido_ID)
        REFERENCES Partido (ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Tramitacao (
    sequencia INTEGER,
    data_hora TIMESTAMP NULL DEFAULT NULL,
    descricao_tramitacao TEXT,
    descricao_situacao VARCHAR(255),
    despacho TEXT,
    apreciacao VARCHAR(255),
    fk_Proposicao_ID BIGINT,
    fk_Orgao_ID INTEGER,
    PRIMARY KEY (fk_Proposicao_ID, sequencia),
    INDEX idx_tramitacao_orgao (fk_Orgao_ID),
    INDEX idx_tramitacao_data_hora (data_hora),
    CONSTRAINT FK_Tramitacao_Proposicao
        FOREIGN KEY (fk_Proposicao_ID)
        REFERENCES Proposicao (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT FK_Tramitacao_Orgao
        FOREIGN KEY (fk_Orgao_ID)
        REFERENCES Orgao (ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Participa (
    fk_Deputado_ID INTEGER,
    fk_Proposicao_ID BIGINT,
    ordem_assinatura INTEGER,
    proponente BOOLEAN,
    PRIMARY KEY (fk_Deputado_ID, fk_Proposicao_ID),
    INDEX idx_participa_proposicao (fk_Proposicao_ID),
    CONSTRAINT FK_Participa_Deputado
        FOREIGN KEY (fk_Deputado_ID)
        REFERENCES Deputado (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT FK_Participa_Proposicao
        FOREIGN KEY (fk_Proposicao_ID)
        REFERENCES Proposicao (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Classificacao (
    fk_Proposicao_ID BIGINT,
    fk_Tema_Cod INTEGER,
    PRIMARY KEY (fk_Proposicao_ID, fk_Tema_Cod),
    INDEX idx_classificacao_tema (fk_Tema_Cod),
    CONSTRAINT FK_Classificacao_Proposicao
        FOREIGN KEY (fk_Proposicao_ID)
        REFERENCES Proposicao (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT FK_Classificacao_Tema
        FOREIGN KEY (fk_Tema_Cod)
        REFERENCES Tema (Cod)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
