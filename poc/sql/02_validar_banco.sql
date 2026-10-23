-- =========================================================
-- VALIDAÇÃO GERAL DO BANCO - FOOTBALL DATA HUB
-- =========================================================


-- 1. QUANTIDADE DE REGISTROS POR TABELA

SELECT 'competicoes' AS tabela, COUNT(*) AS quantidade
FROM competicoes

UNION ALL

SELECT 'temporadas', COUNT(*)
FROM temporadas

UNION ALL

SELECT 'clubes', COUNT(*)
FROM clubes

UNION ALL

SELECT 'jogadores', COUNT(*)
FROM jogadores

UNION ALL

SELECT 'partidas', COUNT(*)
FROM partidas

UNION ALL

SELECT 'jogador_partida', COUNT(*)
FROM jogador_partida

ORDER BY tabela;

-- 2. IDENTIFICADORES DA API DUPLICADOS

SELECT api_id, COUNT(*) AS quantidade
FROM competicoes
GROUP BY api_id
HAVING COUNT(*) > 1;

SELECT api_id, COUNT(*) AS quantidade
FROM clubes
GROUP BY api_id
HAVING COUNT(*) > 1;

SELECT api_id, COUNT(*) AS quantidade
FROM jogadores
GROUP BY api_id
HAVING COUNT(*) > 1;

SELECT api_id, COUNT(*) AS quantidade
FROM partidas
GROUP BY api_id
HAVING COUNT(*) > 1;

-- 3. JOGADORES DUPLICADOS NA MESMA PARTIDA

SELECT
    jogador_id,
    partida_id,
    COUNT(*) AS quantidade
FROM jogador_partida
GROUP BY jogador_id, partida_id
HAVING COUNT(*) > 1;

-- 4. VALIDAÇÃO DAS CHAVES ESTRANGEIRAS

SELECT COUNT(*) AS temporadas_sem_competicao
FROM temporadas t
LEFT JOIN competicoes c ON c.id = t.competicao_id
WHERE c.id IS NULL;

SELECT COUNT(*) AS partidas_sem_temporada
FROM partidas p
LEFT JOIN temporadas t ON t.id = p.temporada_id
WHERE t.id IS NULL;

SELECT COUNT(*) AS partidas_com_clube_inexistente
FROM partidas p
LEFT JOIN clubes mandante ON mandante.id = p.clube_mandante_id
LEFT JOIN clubes visitante ON visitante.id = p.clube_visitante_id
WHERE mandante.id IS NULL
   OR visitante.id IS NULL;

SELECT COUNT(*) AS registros_com_referencia_inexistente
FROM jogador_partida jp
LEFT JOIN jogadores j ON j.id = jp.jogador_id
LEFT JOIN partidas p ON p.id = jp.partida_id
LEFT JOIN clubes c ON c.id = jp.clube_id
WHERE j.id IS NULL
   OR p.id IS NULL
   OR c.id IS NULL;

-- 5. CLUBE DO JOGADOR DEVE PARTICIPAR DA PARTIDA

SELECT COUNT(*) AS jogadores_com_clube_incorreto
FROM jogador_partida jp
JOIN partidas p ON p.id = jp.partida_id
WHERE jp.clube_id NOT IN (
    p.clube_mandante_id,
    p.clube_visitante_id
);

-- 6. RESUMO DE INTEGRIDADE E UNICIDADE

SELECT
    'competicoes_api_id_duplicado' AS verificacao,
    COUNT(*) AS problemas
FROM (
    SELECT api_id
    FROM competicoes
    GROUP BY api_id
    HAVING COUNT(*) > 1
) resultado

UNION ALL

SELECT
    'clubes_api_id_duplicado',
    COUNT(*)
FROM (
    SELECT api_id
    FROM clubes
    GROUP BY api_id
    HAVING COUNT(*) > 1
) resultado

UNION ALL

SELECT
    'jogadores_api_id_duplicado',
    COUNT(*)
FROM (
    SELECT api_id
    FROM jogadores
    GROUP BY api_id
    HAVING COUNT(*) > 1
) resultado

UNION ALL

SELECT
    'partidas_api_id_duplicado',
    COUNT(*)
FROM (
    SELECT api_id
    FROM partidas
    GROUP BY api_id
    HAVING COUNT(*) > 1
) resultado

UNION ALL

SELECT
    'jogador_partida_duplicado',
    COUNT(*)
FROM (
    SELECT jogador_id, partida_id
    FROM jogador_partida
    GROUP BY jogador_id, partida_id
    HAVING COUNT(*) > 1
) resultado

UNION ALL

SELECT
    'temporadas_sem_competicao',
    COUNT(*)
FROM temporadas t
LEFT JOIN competicoes c ON c.id = t.competicao_id
WHERE c.id IS NULL

UNION ALL

SELECT
    'partidas_sem_temporada',
    COUNT(*)
FROM partidas p
LEFT JOIN temporadas t ON t.id = p.temporada_id
WHERE t.id IS NULL

UNION ALL

SELECT
    'partidas_com_clube_inexistente',
    COUNT(*)
FROM partidas p
LEFT JOIN clubes mandante ON mandante.id = p.clube_mandante_id
LEFT JOIN clubes visitante ON visitante.id = p.clube_visitante_id
WHERE mandante.id IS NULL
   OR visitante.id IS NULL

UNION ALL

SELECT
    'jogador_partida_referencia_inexistente',
    COUNT(*)
FROM jogador_partida jp
LEFT JOIN jogadores j ON j.id = jp.jogador_id
LEFT JOIN partidas p ON p.id = jp.partida_id
LEFT JOIN clubes c ON c.id = jp.clube_id
WHERE j.id IS NULL
   OR p.id IS NULL
   OR c.id IS NULL

UNION ALL

SELECT
    'jogador_com_clube_incorreto',
    COUNT(*)
FROM jogador_partida jp
JOIN partidas p ON p.id = jp.partida_id
WHERE jp.clube_id NOT IN (
    p.clube_mandante_id,
    p.clube_visitante_id
);

-- 7. VALIDAÇÃO DOS VALORES DAS PARTIDAS

SELECT
    COUNT(*) FILTER (WHERE rodada <= 0)
        AS rodadas_invalidas,

    COUNT(*) FILTER (
        WHERE clube_mandante_id = clube_visitante_id
    ) AS partidas_com_mesmo_clube,

    COUNT(*) FILTER (
        WHERE gols_mandante < 0 OR gols_visitante < 0
    ) AS gols_negativos,

    COUNT(*) FILTER (
        WHERE penaltis_mandante < 0 OR penaltis_visitante < 0
    ) AS penaltis_negativos,

    COUNT(*) FILTER (WHERE minuto < 0)
        AS minutos_negativos,

    COUNT(*) FILTER (WHERE data_hora IS NULL)
        AS partidas_sem_data,

    COUNT(*) FILTER (WHERE status_partida IS NULL)
        AS partidas_sem_status,

    COUNT(*) FILTER (WHERE temporada_id IS NULL)
        AS partidas_sem_temporada
FROM partidas;

-- 8. VALIDAÇÃO DOS VALORES DE JOGADOR_PARTIDA

SELECT
    'nota_fora_do_intervalo_0_10' AS verificacao,
    COUNT(*) AS problemas
FROM jogador_partida
WHERE nota < 0 OR nota > 10

UNION ALL

SELECT
    'minutos_negativos',
    COUNT(*)
FROM jogador_partida
WHERE minutos_jogados < 0

UNION ALL

SELECT
    'minutos_acima_de_120',
    COUNT(*)
FROM jogador_partida
WHERE minutos_jogados > 120

UNION ALL

SELECT
    'numero_camisa_negativo',
    COUNT(*)
FROM jogador_partida
WHERE numero_camisa < 0

UNION ALL

SELECT
    'estatisticas_inteiras_negativas',
    COUNT(*)
FROM jogador_partida
WHERE impedimentos < 0
   OR gols < 0
   OR defesas < 0
   OR gols_sofridos < 0
   OR assistencias < 0
   OR dribles_total < 0
   OR dribles_bem_sucedidos < 0
   OR faltas_sofridas < 0
   OR faltas_cometidas < 0
   OR desarmes < 0
   OR interceptacoes < 0
   OR finalizacoes_total < 0
   OR finalizacoes_no_alvo < 0
   OR penaltis_cobrados < 0
   OR penaltis_convertidos < 0
   OR passes_total < 0
   OR passes_certos < 0
   OR passes_chave < 0
   OR cartoes_amarelos < 0
   OR cartoes_vermelhos < 0
   OR segundos_amarelos < 0
   OR duelos_total < 0
   OR duelos_vencidos < 0

UNION ALL

SELECT
    'metricas_esperadas_negativas',
    COUNT(*)
FROM jogador_partida
WHERE xa < 0
   OR xg < 0
   OR xg_no_alvo < 0
   OR xg_no_alvo_sofrido < 0

UNION ALL

SELECT
    'segundo_amarelo_inconsistente',
    COUNT(*)
FROM jogador_partida
WHERE segundos_amarelos > cartoes_vermelhos
   OR (
       segundos_amarelos > 0
       AND cartoes_amarelos < 2
   );

-- 9. VALIDAÇÃO DOS SUBTOTAIS ESTATÍSTICOS

SELECT
    'dribles_bem_sucedidos_maior_que_total' AS verificacao,
    COUNT(*) AS problemas
FROM jogador_partida
WHERE dribles_bem_sucedidos > dribles_total

UNION ALL

SELECT
    'finalizacoes_no_alvo_maior_que_total',
    COUNT(*)
FROM jogador_partida
WHERE finalizacoes_no_alvo > finalizacoes_total

UNION ALL

SELECT
    'penaltis_convertidos_maior_que_cobrados',
    COUNT(*)
FROM jogador_partida
WHERE penaltis_convertidos > penaltis_cobrados

UNION ALL

SELECT
    'passes_certos_maior_que_total',
    COUNT(*)
FROM jogador_partida
WHERE passes_certos > passes_total

UNION ALL

SELECT
    'duelos_vencidos_maior_que_total',
    COUNT(*)
FROM jogador_partida
WHERE duelos_vencidos > duelos_total;

-- 10. DISTRIBUIÇÃO DAS PARTIDAS POR STATUS

SELECT
    status_partida,
    COUNT(*) AS quantidade
FROM partidas
GROUP BY status_partida
ORDER BY quantidade DESC;

-- 11. COBERTURA DOS BOX SCORES

SELECT
    COUNT(*) AS total_partidas,

    COUNT(*) FILTER (
        WHERE EXISTS (
            SELECT 1
            FROM jogador_partida jp
            WHERE jp.partida_id = p.id
        )
    ) AS partidas_com_box_score,

    COUNT(*) FILTER (
        WHERE NOT EXISTS (
            SELECT 1
            FROM jogador_partida jp
            WHERE jp.partida_id = p.id
        )
    ) AS partidas_sem_box_score
FROM partidas p;

-- 12. Partidas finalizadas sem box score

SELECT
    p.api_id,
    p.rodada,
    p.data_hora,
    mandante.nome AS mandante,
    visitante.nome AS visitante,
    p.status_partida
FROM partidas p
JOIN clubes mandante
    ON mandante.id = p.clube_mandante_id
JOIN clubes visitante
    ON visitante.id = p.clube_visitante_id
WHERE LOWER(p.status_partida) = 'finished'
  AND NOT EXISTS (
      SELECT 1
      FROM jogador_partida jp
      WHERE jp.partida_id = p.id
  )
ORDER BY p.rodada, p.data_hora;

-- 13. Resumo dos campos nulos e participação

SELECT
    COUNT(*) AS total_registros,

    COUNT(*) FILTER (
        WHERE minutos_jogados = 0
    ) AS registros_com_zero_minutos,

    COUNT(*) FILTER (
        WHERE minutos_jogados = 0 AND titular = TRUE
    ) AS titulares_com_zero_minutos,

    COUNT(*) FILTER (
        WHERE nota IS NULL
    ) AS notas_nulas,

    COUNT(*) FILTER (
        WHERE nota IS NULL AND minutos_jogados > 0
    ) AS notas_nulas_com_participacao,

    COUNT(*) FILTER (
        WHERE posicao_partida IS NULL
           OR TRIM(posicao_partida) = ''
    ) AS posicoes_ausentes
FROM jogador_partida;

-- 14. COMPARAÇÃO ENTRE GOLS DOS JOGADORES E PLACARES

WITH gols_por_partida AS (
    SELECT
        p.id,
        p.api_id,
        p.rodada,
        p.gols_mandante,
        p.gols_visitante,

        COALESCE(
            SUM(jp.gols) FILTER (
                WHERE jp.clube_id = p.clube_mandante_id
            ),
            0
        ) AS gols_jogadores_mandante,

        COALESCE(
            SUM(jp.gols) FILTER (
                WHERE jp.clube_id = p.clube_visitante_id
            ),
            0
        ) AS gols_jogadores_visitante

    FROM partidas p

    JOIN jogador_partida jp
        ON jp.partida_id = p.id

    WHERE LOWER(p.status_partida) = 'finished'

    GROUP BY
        p.id,
        p.api_id,
        p.rodada,
        p.gols_mandante,
        p.gols_visitante
)

SELECT
    COUNT(*) AS partidas_com_diferenca_nos_gols
FROM gols_por_partida
WHERE gols_jogadores_mandante <> gols_mandante
   OR gols_jogadores_visitante <> gols_visitante;

-- 15. DETALHAMENTO DAS DIFERENÇAS DE GOLS

WITH gols_por_partida AS (
    SELECT
        p.id,
        p.api_id,
        p.rodada,
        p.data_hora,
        mandante.nome AS mandante,
        visitante.nome AS visitante,
        p.gols_mandante,
        p.gols_visitante,

        COALESCE(
            SUM(jp.gols) FILTER (
                WHERE jp.clube_id = p.clube_mandante_id
            ),
            0
        ) AS gols_jogadores_mandante,

        COALESCE(
            SUM(jp.gols) FILTER (
                WHERE jp.clube_id = p.clube_visitante_id
            ),
            0
        ) AS gols_jogadores_visitante

    FROM partidas p

    JOIN clubes mandante
        ON mandante.id = p.clube_mandante_id

    JOIN clubes visitante
        ON visitante.id = p.clube_visitante_id

    JOIN jogador_partida jp
        ON jp.partida_id = p.id

    WHERE LOWER(p.status_partida) = 'finished'

    GROUP BY
        p.id,
        p.api_id,
        p.rodada,
        p.data_hora,
        mandante.nome,
        visitante.nome,
        p.gols_mandante,
        p.gols_visitante
)

SELECT
    api_id,
    rodada,
    mandante,
    visitante,
    gols_mandante,
    gols_jogadores_mandante,
    gols_visitante,
    gols_jogadores_visitante,
    gols_mandante - gols_jogadores_mandante
        AS diferenca_mandante,
    gols_visitante - gols_jogadores_visitante
        AS diferenca_visitante
FROM gols_por_partida
WHERE gols_jogadores_mandante <> gols_mandante
   OR gols_jogadores_visitante <> gols_visitante
ORDER BY rodada, data_hora;

-- OBSERVAÇÃO SOBRE A VALIDAÇÃO DOS GOLS
--
-- Foram identificadas 27 partidas em que a soma dos gols
-- atribuídos aos jogadores ficou exatamente uma unidade abaixo
-- do placar de um dos clubes.
--
-- Não foram encontradas somas maiores que o placar nem diferenças
-- superiores a um gol.
--
-- O padrão é compatível com gols contra, pois eles aparecem no
-- placar da partida, mas não são contabilizados em goalsScored
-- para nenhum jogador do clube beneficiado.
--
-- Portanto, esses registros não foram alterados.