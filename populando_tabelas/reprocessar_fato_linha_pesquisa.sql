-- ========================================
-- REPROCESSAR FATO_PESQUISADOR_LINHA_PESQUISA
-- ========================================
-- 
-- Este script limpa e reprocessa a tabela fato com o JOIN corrigido.
-- 
-- PROBLEMA: A tabela fato estava usando TRIM() simples no JOIN,
-- mas a dimensão aplica normalização complexa (remove números, aspas, URLs).
-- Resultado: 93% das linhas não davam match!
--
-- SOLUÇÃO: Aplicar a MESMA normalização no JOIN.
--

-- 1. Backup (opcional, para segurança)
-- CREATE TABLE dw.fato_pesquisador_linha_pesquisa_backup AS 
-- SELECT * FROM dw.fato_pesquisador_linha_pesquisa;

-- 2. Limpar tabela fato
TRUNCATE TABLE dw.fato_pesquisador_linha_pesquisa;

-- 3. Verificar limpeza
SELECT 
    'Tabela limpa' as status,
    COUNT(*) as registros_atuais
FROM dw.fato_pesquisador_linha_pesquisa;

-- 4. Agora rode o script Python:
-- cd /Users/marianacunha/Documents/TCC/BI_PRODUCOES_CIENTIFICAS/populando_tabelas
-- python fato_pesquisador_linha_pesquisa.py

