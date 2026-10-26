-- =====================================================
-- Tabela nova para o recurso de mensagens (caixa de entrada)
-- Rode este script no mesmo banco onde já estão as
-- tabelas `aluno`, `gestão`, `turmas`, `fotos` e `comentarios`.
-- =====================================================

-- Mensagens trocadas entre alunos (home) e gestão.
--
-- direcao = 'aluno_para_gestao'
--     id_aluno  = aluno que ESCREVEU a mensagem
--     id_gestor = NULL (qualquer gestor vê na caixa de entrada)
--
-- direcao = 'gestao_para_aluno'
--     id_aluno  = aluno que RECEBE (NULL = todos os alunos)
--     id_gestor = gestor que escreveu
--
-- lida só é usada em mensagens individuais (aluno -> gestão e
-- gestão -> um aluno). Aviso para "todos" aparece sempre como lido.
CREATE TABLE mensagens (
    id_mensagem INT AUTO_INCREMENT PRIMARY KEY,
    direcao ENUM('aluno_para_gestao', 'gestao_para_aluno') NOT NULL,
    id_aluno INT NULL,
    id_gestor INT NULL,
    assunto VARCHAR(150) NOT NULL,
    texto VARCHAR(2000) NOT NULL,
    lida TINYINT(1) NOT NULL DEFAULT 0,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno)
        ON DELETE CASCADE,
    FOREIGN KEY (id_gestor) REFERENCES gestão(id_gestor)
        ON DELETE SET NULL
);
