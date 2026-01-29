CREATE TABLE stg.pesquisador (
    id_lattes VARCHAR(100) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    atuacao_profissional TEXT
);

CREATE TABLE stg.linha_pesquisa (
    id SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    linha_pesquisa VARCHAR(500) NOT NULL
);

CREATE TABLE stg.areas_atuacao (
    id SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    nome_grande_area VARCHAR(255),
    nome_area VARCHAR(255) NOT NULL,
    nome_sub_area VARCHAR(255),
    nome_especialidade VARCHAR(255)
);

CREATE TABLE stg.projetos_pesquisa (
    id SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    ano_inicio VARCHAR(10),
    ano_fim VARCHAR(10),
    nome_projeto VARCHAR(500) NOT NULL,
    descricao_projeto TEXT,
    situacao VARCHAR(100),           
    natureza VARCHAR(100)            
);

CREATE TABLE stg.artigos (
    id SERIAL PRIMARY KEY,           
    id_lattes VARCHAR(100) NOT NULL, 
    ano VARCHAR(10),
    titulo VARCHAR(1000) NOT NULL,
    doi VARCHAR(255),
    idioma VARCHAR(50),
    natureza VARCHAR(50),
    meio_divulgacao VARCHAR(50),
    titulo_periodico VARCHAR(500),
    volume VARCHAR(20),
    pagina_inicial VARCHAR(10),
    pagina_final VARCHAR(10),
    issn VARCHAR(20),
    local_publicacao VARCHAR(255),
    autores TEXT                        
);

CREATE TABLE stg.livros (
    id SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    ano VARCHAR(10),
    titulo VARCHAR(1000) NOT NULL,
    numero_edicao VARCHAR(50),
    cidade_editora VARCHAR(255),
    nome_editora VARCHAR(255),
    numero_volumes VARCHAR(50),
    numero_paginas VARCHAR(50),
    autores TEXT
);


CREATE TABLE stg.capitulos_livros (
    id SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    ano VARCHAR(10),
    titulo_capitulo VARCHAR(1000) NOT NULL,
    titulo_livro VARCHAR(1000),
    doi VARCHAR(255),
    idioma VARCHAR(50),
    meio_divulgacao VARCHAR(50),
    numero_edicao VARCHAR(50),
    cidade_editora VARCHAR(255),
    nome_editora VARCHAR(255),
    isbn VARCHAR(50),
    pagina_inicial VARCHAR(10),
    pagina_final VARCHAR(10),
    organizadores VARCHAR(1000),
    autores TEXT
);

CREATE TABLE stg.textos_jornais (
    id SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    ano VARCHAR(10),
    titulo VARCHAR(1000) NOT NULL,
    titulo_jornal VARCHAR(500),
    doi VARCHAR(255),
    idioma VARCHAR(50),
    natureza VARCHAR(100),             
    meio_divulgacao VARCHAR(50),
    data_publicacao VARCHAR(20),       
    local_publicacao VARCHAR(255),
    pagina_inicial VARCHAR(10),
    pagina_final VARCHAR(10),
    volume VARCHAR(20),
    issn VARCHAR(20),
    autores TEXT
);

CREATE TABLE stg.trabalhos_eventos (
    id SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    ano VARCHAR(10),
    titulo VARCHAR(1000) NOT NULL,
    nome_evento VARCHAR(500),
    titulo_anais VARCHAR(500),
    doi VARCHAR(255),
    idioma VARCHAR(50),
    natureza VARCHAR(50),                  
    meio_divulgacao VARCHAR(50),
    pais_evento VARCHAR(100),
    ano_realizacao VARCHAR(10),
    cidade_evento VARCHAR(255),
    classificacao_evento VARCHAR(50),      
    nome_editora VARCHAR(255),
    cidade_editora VARCHAR(255),
    isbn VARCHAR(50),
    volume VARCHAR(20),
    pagina_inicial VARCHAR(10),
    pagina_final VARCHAR(10),
    autores TEXT
);

CREATE TABLE stg.apresentacoes_trabalho (
    id SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    ano VARCHAR(10),
    titulo VARCHAR(1000) NOT NULL,
    doi VARCHAR(255),
    idioma VARCHAR(50),
    natureza VARCHAR(100),             
    pais VARCHAR(100),
    nome_evento VARCHAR(500),
    cidade_apresentacao VARCHAR(255),
    local_apresentacao VARCHAR(255),
    instituicao_promotora VARCHAR(500),
    autores TEXT
);

CREATE TABLE stg.outras_producoes (
    id SERIAL PRIMARY KEY,
    id_lattes VARCHAR(100) NOT NULL,
    ano VARCHAR(10),
    titulo VARCHAR(1000) NOT NULL,
    doi VARCHAR(255),
    idioma VARCHAR(50),
    natureza VARCHAR(200),             
    meio_divulgacao VARCHAR(50),
    pais_publicacao VARCHAR(100),
    cidade_editora VARCHAR(255),
    editora VARCHAR(500),
    issn_isbn VARCHAR(50),
    numero_paginas VARCHAR(20),
    autores TEXT
);