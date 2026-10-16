CREATE TABLE competicoes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    api_id BIGINT NOT NULL UNIQUE,
    nome VARCHAR(50) NOT NULL,
    logo TEXT,
    pais_codigo CHAR(2) NOT NULL,
    pais_nome VARCHAR(50) NOT NULL,
    pais_logo TEXT 
);

CREATE TABLE temporadas (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ano SMALLINT NOT NULL,
    competicao_id BIGINT NOT NULL,
    FOREIGN KEY (competicao_id) REFERENCES competicoes(id),
    UNIQUE (competicao_id, ano)
);

CREATE TABLE clubes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    api_id BIGINT NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    logo TEXT
);

CREATE TABLE jogadores (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    api_id BIGINT NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    logo TEXT,
    posicao_principal VARCHAR(50)
);

CREATE TABLE partidas (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    api_id BIGINT NOT NULL UNIQUE,
    rodada SMALLINT NOT NULL,
    data_hora TIMESTAMPTZ NOT NULL,
    clube_mandante_id BIGINT NOT NULL,
    clube_visitante_id BIGINT NOT NULL,
    gols_mandante SMALLINT,
    gols_visitante SMALLINT,
    penaltis_mandante SMALLINT,
    penaltis_visitante SMALLINT,
    minuto SMALLINT,
    status_partida VARCHAR(30) NOT NULL,
    temporada_id BIGINT NOT NULL,
    FOREIGN KEY (clube_mandante_id) REFERENCES clubes (id), 
    FOREIGN KEY (clube_visitante_id) REFERENCES clubes (id), 
    FOREIGN KEY (temporada_id) REFERENCES temporadas (id),
    CHECK (rodada > 0),
    CHECK (gols_mandante >= 0), 
    CHECK (gols_visitante >= 0),
    CHECK (penaltis_mandante >= 0 ), 
    CHECK (penaltis_visitante >= 0 ),
    CHECK (minuto >= 0),
    CHECK (clube_mandante_id <> clube_visitante_id) 
);

CREATE TABLE jogador_partida (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    jogador_id BIGINT NOT NULL,
    partida_id BIGINT NOT NULL,
    clube_id BIGINT NOT NULL,
    numero_camisa SMALLINT NOT NULL,
    posicao_partida VARCHAR(50) NOT NULL,
    nota NUMERIC(4,2),
    capitao BOOLEAN NOT NULL,
    minutos_jogados SMALLINT NOT NULL,
    titular BOOLEAN NOT NULL,
    impedimentos SMALLINT NOT NULL DEFAULT 0,
    gols SMALLINT NOT NULL DEFAULT 0,
    defesas SMALLINT NOT NULL DEFAULT 0,
    gols_sofridos SMALLINT NOT NULL DEFAULT 0,
    assistencias SMALLINT NOT NULL DEFAULT 0,
    dribles_total SMALLINT NOT NULL DEFAULT 0,
    dribles_bem_sucedidos SMALLINT NOT NULL DEFAULT 0,
    faltas_sofridas SMALLINT NOT NULL DEFAULT 0,
    faltas_cometidas SMALLINT NOT NULL DEFAULT 0,
    desarmes SMALLINT NOT NULL DEFAULT 0,
    interceptacoes SMALLINT NOT NULL DEFAULT 0,
    finalizacoes_total SMALLINT NOT NULL DEFAULT 0,
    finalizacoes_no_alvo SMALLINT NOT NULL DEFAULT 0,
    penaltis_cobrados SMALLINT NOT NULL DEFAULT 0,
    penaltis_convertidos SMALLINT NOT NULL DEFAULT 0,
    passes_total SMALLINT NOT NULL DEFAULT 0,
    passes_certos SMALLINT NOT NULL DEFAULT 0,
    passes_chave SMALLINT NOT NULL DEFAULT 0,
    cartoes_amarelos SMALLINT NOT NULL DEFAULT 0,
    cartoes_vermelhos SMALLINT NOT NULL DEFAULT 0,
    segundos_amarelos SMALLINT NOT NULL DEFAULT 0,
    duelos_total SMALLINT NOT NULL DEFAULT 0,
    duelos_vencidos SMALLINT NOT NULL DEFAULT 0,
    xa NUMERIC(8,4),
    xg NUMERIC(8,4),
    xg_no_alvo NUMERIC(8,4),
    xg_no_alvo_sofrido NUMERIC(8,4),
    gols_evitados_esperados NUMERIC(8,4),
    FOREIGN KEY (jogador_id) REFERENCES jogadores(id),
    FOREIGN KEY (partida_id) REFERENCES partidas(id),
    FOREIGN KEY (clube_id) REFERENCES clubes(id),
    UNIQUE (jogador_id, partida_id),
    CONSTRAINT ck_jogador_partida_nota
        CHECK (nota BETWEEN 0 AND 10),

    CONSTRAINT ck_jogador_partida_valores_nao_negativos
        CHECK (
            numero_camisa >= 0
            AND minutos_jogados >= 0
            AND impedimentos >= 0
            AND gols >= 0
            AND defesas >= 0
            AND gols_sofridos >= 0
            AND assistencias >= 0
            AND dribles_total >= 0
            AND dribles_bem_sucedidos >= 0
            AND faltas_sofridas >= 0
            AND faltas_cometidas >= 0
            AND desarmes >= 0
            AND interceptacoes >= 0
            AND finalizacoes_total >= 0
            AND finalizacoes_no_alvo >= 0
            AND penaltis_cobrados >= 0
            AND penaltis_convertidos >= 0
            AND passes_total >= 0
            AND passes_certos >= 0
            AND passes_chave >= 0
            AND cartoes_amarelos >= 0
            AND cartoes_vermelhos >= 0
            AND segundos_amarelos >= 0
            AND duelos_total >= 0
            AND duelos_vencidos >= 0
        ),

    CONSTRAINT ck_jogador_partida_subtotais
        CHECK (
            dribles_bem_sucedidos <= dribles_total
            AND finalizacoes_no_alvo <= finalizacoes_total
            AND penaltis_convertidos <= penaltis_cobrados
            AND passes_certos <= passes_total
            AND duelos_vencidos <= duelos_total
        ),

    CONSTRAINT ck_jogador_partida_metricas_esperadas
        CHECK (
            xa >= 0
            AND xg >= 0
            AND xg_no_alvo >= 0
            AND xg_no_alvo_sofrido >= 0
        )
);