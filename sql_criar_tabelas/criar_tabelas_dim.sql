CREATE TABLE dw.dim_area (
    id_area SERIAL PRIMARY KEY,
    grande_area VARCHAR(255),
    area VARCHAR(255)
);

CREATE TABLE dw.dim_linha_pesquisa (
    id_linha_pesquisa SERIAL PRIMARY KEY,
    linha_pesquisa VARCHAR(500) NOT NULL
);

CREATE TABLE dw.dim_pesquisador (
    id_pesquisador SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100),
    nome VARCHAR(100),
    atuacao_profissional TEXT
);

CREATE TABLE dw.dim_tempo (
    id_tempo SERIAL PRIMARY KEY,
    ano INT NOT NULL
);

CREATE TABLE dw.dim_tipo_producao (
    id_tipo_producao SERIAL PRIMARY KEY,
    tipo_producao VARCHAR(100)
);

CREATE TABLE dw.dim_localizacao_trabalhos (
    id_localizacao_trabalhos SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    instituicao VARCHAR(500),
    pais VARCHAR(100)
);

