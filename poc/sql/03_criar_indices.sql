CREATE INDEX IF NOT EXISTS idx_temporadas_competicao
    ON temporadas (competicao_id);

CREATE INDEX IF NOT EXISTS idx_partidas_temporada
    ON partidas (temporada_id);

CREATE INDEX IF NOT EXISTS idx_partidas_mandante
    ON partidas (clube_mandante_id);

CREATE INDEX IF NOT EXISTS idx_partidas_visitante
    ON partidas (clube_visitante_id);

CREATE INDEX IF NOT EXISTS idx_jogador_partida_partida
    ON jogador_partida (partida_id);

CREATE INDEX IF NOT EXISTS idx_jogador_partida_clube
    ON jogador_partida (clube_id);