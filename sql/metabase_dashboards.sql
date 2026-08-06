-- ===================================================================
-- CONSULTAS SQL PRONTAS PARA CRIAR OS DASHBOARDS NO METABASE
-- Projeto: Inteligência Eleitoral - Campanha Wilder Morais (Goiás)
-- ===================================================================

-- -------------------------------------------------------------------
-- DASHBOARD 1: Termômetro Regional (246 Cidades de Goiás + PostGIS Pin Map)
-- -------------------------------------------------------------------
SELECT 
    m.nome AS cidade,
    m.eleitores_tse,
    m.latitude,
    m.longitude,
    COALESCE(w.alcance, 0) AS alcance_digital,
    COALESCE(w.investimento, 0.00) AS investimento_trafego_pago,
    COALESCE(w.cliques, 0) AS cliques_anuncios,
    ROUND((COALESCE(w.alcance, 0)::numeric / NULLIF(m.eleitores_tse, 0)::numeric) * 100, 2) AS taxa_penetracao_eleitoral_pct
FROM municipios_goias m
LEFT JOIN (
    SELECT DISTINCT ON (cidade) cidade, alcance, investimento, cliques
    FROM metricas_wilder
    ORDER BY cidade, data DESC
) w ON LOWER(m.nome) = LOWER(w.cidade)
ORDER BY m.eleitores_tse DESC;


-- -------------------------------------------------------------------
-- DASHBOARD 2: Guerra de Concorrentes (Daniel Vilela vs Marconi Perillo vs Wilder Morais)
-- -------------------------------------------------------------------
SELECT 
    data,
    candidato_nome,
    seguidores AS seguidores_instagram_tiktok,
    taxa_engajamento,
    facebook_seguidores
FROM concorrentes_historico
ORDER BY data DESC, seguidores DESC;


-- -------------------------------------------------------------------
-- DASHBOARD 3: Matriz de Notícias & Sentimento Anticrise
-- -------------------------------------------------------------------
SELECT 
    sentimento,
    COUNT(*) AS total_materias,
    ROUND((COUNT(*)::numeric / (SELECT COUNT(*) FROM clipping_noticias)::numeric) * 100, 1) AS percentual
FROM clipping_noticias
GROUP BY sentimento
ORDER BY total_materias DESC;


-- -------------------------------------------------------------------
-- DASHBOARD 4: Últimas Notícias e Alertas de Crise Registrados
-- -------------------------------------------------------------------
SELECT 
    data,
    titulo,
    portal,
    sentimento,
    resumo,
    link
FROM clipping_noticias
ORDER BY data DESC
LIMIT 20;


-- -------------------------------------------------------------------
-- DASHBOARD 5: Google Trends Goiás (Pautas e Candidatos em Alta)
-- -------------------------------------------------------------------
SELECT 
    data,
    termo,
    interesse_relativo,
    regiao_mais_buscada,
    assuntos_relacionados
FROM google_trends_goias
ORDER BY data DESC, interesse_relativo DESC;


-- -------------------------------------------------------------------
-- DASHBOARD 6: Histórico de Briefings Diários & Roteiros do Social Media
-- -------------------------------------------------------------------
SELECT 
    data,
    resumo_cenario,
    pautas_google_trends,
    ideias_roteiros
FROM briefings_diarios
ORDER BY data DESC;


-- -------------------------------------------------------------------
-- DASHBOARD 7: Performance do Canal do YouTube (@WilderMoraisGoias)
-- -------------------------------------------------------------------
SELECT 
    data,
    inscritos,
    visualizacoes_totais,
    videos_totais,
    visualizacoes_diarias,
    engajamento_medio
FROM youtube_performance
ORDER BY data DESC;


-- -------------------------------------------------------------------
-- DASHBOARD 8: Radar de Social Listening & Reclamações Populares por Cidade
-- -------------------------------------------------------------------
SELECT 
    created_at AS data,
    cidade,
    pauta_chave,
    reclamacao_texto,
    fonte,
    impacto_politico,
    oportunidade_criativo
FROM reclamacoes_cidadaos
ORDER BY created_at DESC;
