-- =====================================================
-- Tabela para as turmas criadas pelo botão "+ Adicionar turma"
-- (gestao-turmas.html). Rode no mesmo banco das outras tabelas.
--
-- Por que existe: a tabela `turmas` tem 1 linha POR ALUNO
-- (id_aluno, ra_aluno, nome_aluno, turma), então uma turma só
-- "existe" lá depois que tem aluno. Esta tabela guarda a turma
-- em si (código, nome, professor, turno, cor), mesmo vazia.
--
-- O `codigo` tem que ser igual ao valor da coluna `turma` da tabela
-- `turmas` (ex: 3_ano_B) para os alunos aparecerem nela.
-- =====================================================
CREATE TABLE turmas_cadastradas (
    id_turma INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    professor VARCHAR(100) NOT NULL,
    turno VARCHAR(20) NOT NULL,
    cor VARCHAR(100),
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
