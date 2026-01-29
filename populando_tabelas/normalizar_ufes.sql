SELECT 
    COUNT(*) as registros_afetados,
    'Serão padronizados para: Universidade Federal do Espírito Santo' as mensagem
FROM dw.dim_pesquisador
WHERE atuacao_profissional ~* 'federal do esp[ií]rito santo'
  AND atuacao_profissional !~* 'instituto'
  AND atuacao_profissional !~* 'regional'
  AND atuacao_profissional !~* 'justiça'
  AND atuacao_profissional !~* 'associa[cç][aã]o';

SELECT 
    id_pesquisador,
    nome,
    atuacao_profissional as valor_atual,
    'Universidade Federal do Espírito Santo' as novo_valor
FROM dw.dim_pesquisador
WHERE atuacao_profissional ~* 'federal do esp[ií]rito santo'
  AND atuacao_profissional !~* 'instituto'
  AND atuacao_profissional !~* 'regional'
  AND atuacao_profissional !~* 'justiça'
  AND atuacao_profissional !~* 'associa[cç][aã]o'
LIMIT 10;


UPDATE dw.dim_pesquisador
SET atuacao_profissional = 'Universidade Federal do Espírito Santo'
WHERE atuacao_profissional ~* 'federal do esp[ií]rito santo'
  AND atuacao_profissional !~* 'instituto'
  AND atuacao_profissional !~* 'regional'
  AND atuacao_profissional !~* 'justiça'
  AND atuacao_profissional !~* 'associa[cç][aã]o';

SELECT 
    COUNT(*) as total_ufes,
    'Universidade Federal do Espírito Santo' as atuacao_padronizada
FROM dw.dim_pesquisador
WHERE atuacao_profissional = 'Universidade Federal do Espírito Santo';

COMMIT;

