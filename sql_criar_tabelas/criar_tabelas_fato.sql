CREATE TABLE dw.fato_pesquisador_producoes (
    id_fato_pesquisador_producoes SERIAL PRIMARY KEY,
    id_pesquisador INT NOT NULL,
    id_tempo INT NOT NULL,
    id_tipo_producao INT NOT NULL,
    qtd_producoes INT NOT NULL
);


CREATE TABLE dw.fato_pesquisador_area_atuacao (
    id_fato_pesquisador_area SERIAL PRIMARY KEY,
    id_pesquisador INT NOT NULL,
    id_area INT NOT NULL,
    presenca INT NOT NULL DEFAULT 1,
    CONSTRAINT uq_fato_pesquisador_area UNIQUE (id_pesquisador, id_area)
);

CREATE TABLE dw.fato_pesquisador_linha_pesquisa (
    id_fato_pesquisador_linha SERIAL PRIMARY KEY,
    id_pesquisador INT NOT NULL,
    id_linha_pesquisa INT NOT NULL,
    presenca INT NOT NULL DEFAULT 1,
    CONSTRAINT uq_fato_pesquisador_linha UNIQUE (id_pesquisador, id_linha_pesquisa)
);

CREATE TABLE dw.fato_pesquisador_producao_localizacao (
    id_fato_pesq_prod_loc SERIAL PRIMARY KEY,
    id_pesquisador INT NOT NULL,
    id_tempo INT NOT NULL,
    id_tipo_producao INT NOT NULL,
    id_localizacao_trabalhos INT NOT NULL,
    qtd_producoes INT NOT NULL,
    CONSTRAINT uq_fato_pesq_prod_loc UNIQUE (
        id_pesquisador,
        id_tempo,
        id_tipo_producao,
        id_localizacao_trabalhos
    )
);