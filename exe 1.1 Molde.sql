-- Criar o banco de dados
CREATE DATABASE IF NOT EXISTS seguranca;
USE seguranca;

-- Tabela de ativos
CREATE TABLE ativos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ip VARCHAR(45) NOT NULL UNIQUE,
    tipo VARCHAR(50) NOT NULL,
    criticidade ENUM('Baixa', 'Media', 'Alta', 'Critica')
        NOT NULL
);

-- Tabela de vulnerabilidades
CREATE TABLE vulnerabilidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cve_id VARCHAR(30) NOT NULL UNIQUE,
    descricao TEXT NOT NULL,
    severidade ENUM('Baixa', 'Media', 'Alta', 'Critica')
        NOT NULL,
    cvss DECIMAL(3,1) NOT NULL,
    CHECK (cvss >= 0 AND cvss <= 10)
);

-- Tabela de relacionamento entre ativos e vulnerabilidades
CREATE TABLE ativo_vulnerabilidade (
    ativo_id INT NOT NULL,
    vuln_id INT NOT NULL,
    status ENUM('Aberta', 'Em_correcao', 'Corrigida')
        NOT NULL DEFAULT 'Aberta',
    detectada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (ativo_id, vuln_id),

    FOREIGN KEY (ativo_id) REFERENCES ativos(id),
    FOREIGN KEY (vuln_id) REFERENCES vulnerabilidades(id)
);
