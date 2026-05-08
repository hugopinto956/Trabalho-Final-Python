use  troca_livros;
-- Tabela UTILIZADOR
CREATE TABLE UTILIZADOR (
    id_utilizador INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    localizacao VARCHAR(100),
    avaliacao INT DEFAULT 0
);

-- Tabela LIVRO
CREATE TABLE LIVRO (
    id_livro INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(200) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    genero VARCHAR(50),
    estado_conservacao VARCHAR(50),
    id_utilizador INT NOT NULL,
    FOREIGN KEY (id_utilizador) REFERENCES UTILIZADOR(id_utilizador) 
        ON DELETE CASCADE
);

-- Tabela TROCA
CREATE TABLE TROCA (
    id_troca INT PRIMARY KEY AUTO_INCREMENT,
    data_troca DATE NOT NULL,
    estado_troca VARCHAR(50) DEFAULT 'pendente',
    id_livro INT NOT NULL,
    id_utilizador_origem INT NOT NULL,
    id_utilizador_destino INT NOT NULL,
    FOREIGN KEY (id_livro) REFERENCES LIVRO(id_livro) 
        ON DELETE CASCADE,
    FOREIGN KEY (id_utilizador_origem) REFERENCES UTILIZADOR(id_utilizador) 
        ON DELETE CASCADE,
    FOREIGN KEY (id_utilizador_destino) REFERENCES UTILIZADOR(id_utilizador) 
        ON DELETE CASCADE
);

ALTER TABLE LIVRO
ADD disponivel BOOLEAN DEFAULT TRUE;

select * from LIVRO;
select * from utilizador;