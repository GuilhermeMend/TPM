-- =====================================================
-- Tabelas novas para o recurso de fotos e comentários
-- Rode este script no mesmo banco onde já estão as
-- tabelas `aluno`, `gestão` e `turmas`.
-- =====================================================

-- Fotos publicadas pela gestão
CREATE TABLE fotos (
    id_foto INT AUTO_INCREMENT PRIMARY KEY,
    nome_arquivo VARCHAR(255) NOT NULL,
    legenda VARCHAR(255),
    id_gestor INT,
    data_postagem DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_gestor) REFERENCES gestão(id_gestor)
        ON DELETE SET NULL
);

-- Comentários dos alunos em cada foto
CREATE TABLE comentarios (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,
    id_foto INT NOT NULL,
    id_aluno INT NOT NULL,
    texto VARCHAR(500) NOT NULL,
    data_comentario DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_foto) REFERENCES fotos(id_foto)
        ON DELETE CASCADE,
    FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno)
        ON DELETE CASCADE
);
