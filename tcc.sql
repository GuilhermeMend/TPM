-- =====================================================================
-- TPM — banco de dados completo (MySQL 8+ / MariaDB 10.4+)
--
-- Como usar:
--   1) Rode este arquivo inteiro (HeidiSQL: Arquivo > Executar arquivo SQL,
--      ou:  mysql -u root -p < tcc.sql).
--      Ele pode ser rodado mais de uma vez: só cria o que ainda não existe
--      e NÃO apaga nada.
--   2) Crie o primeiro usuário da gestão (pede nome e senha no terminal):
--          python criar_gestor.py
--      Os alunos são cadastrados depois, pela própria gestão (cadastro.html).
--
-- Já tem um banco antigo (de antes desta versão)?
--   Rode:  python atualizar_banco.py   (e, se as senhas ainda estiverem em
--   texto puro, também:  python migrar_senhas.py)
--
-- Este arquivo NÃO traz nenhum usuário nem senha: nada de login dentro
-- do repositório.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `banco de dados` DEFAULT CHARACTER SET utf8mb4;
USE `banco de dados`;


-- ---------------------------------------------------------------------
-- Login do aluno.  `senha` guarda o HASH (~160 caracteres), nunca o texto.
-- `nome` é único porque o login procura o aluno pelo nome.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `aluno` (
  `id_aluno` INT NOT NULL AUTO_INCREMENT,
  `nome`     VARCHAR(50)  NOT NULL,
  `senha`    VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_aluno`),
  UNIQUE KEY `uq_aluno_nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ---------------------------------------------------------------------
-- Login da gestão (também com hash).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `gestão` (
  `id_gestor` INT NOT NULL AUTO_INCREMENT,
  `nome`      VARCHAR(50)  NOT NULL,
  `senha`     VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_gestor`),
  UNIQUE KEY `uq_gestao_nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ---------------------------------------------------------------------
-- Turmas criadas pelo botão "+ Adicionar turma" (existem mesmo vazias).
-- O `codigo` tem que ser igual ao valor de turmas.turma (ex: 3_ano_B).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `turmas_cadastradas` (
  `id_turma`     INT NOT NULL AUTO_INCREMENT,
  `codigo`       VARCHAR(50)  NOT NULL,
  `nome`         VARCHAR(100) NOT NULL,
  `professor`    VARCHAR(100) NOT NULL,
  `turno`        VARCHAR(20)  NOT NULL,
  `cor`          VARCHAR(100) DEFAULT NULL,
  `data_criacao` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_turma`),
  UNIQUE KEY `uq_turmas_cadastradas_codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ---------------------------------------------------------------------
-- Matrícula: 1 linha por aluno (RA + turma).
--   id_login -> aluno.id_aluno: liga a matrícula ao login do aluno.
--               Apagar o login apaga a matrícula junto (CASCADE).
--               Pode ser NULL só em matrículas antigas/de exemplo, que
--               ainda não têm login.
--   ra_aluno é único: o mesmo RA não entra duas vezes.
-- (O nome da coluna id_aluno foi mantido porque o app.py e o front já usam.)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `turmas` (
  `id_aluno`   INT NOT NULL AUTO_INCREMENT,
  `id_login`   INT DEFAULT NULL,
  `ra_aluno`   VARCHAR(50) DEFAULT NULL,
  `nome_aluno` VARCHAR(50) DEFAULT NULL,
  `turma`      VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`id_aluno`),
  UNIQUE KEY `uq_turmas_ra` (`ra_aluno`),
  KEY `idx_turmas_turma` (`turma`),
  CONSTRAINT `fk_turmas_login` FOREIGN KEY (`id_login`)
    REFERENCES `aluno` (`id_aluno`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ---------------------------------------------------------------------
-- Fotos publicadas pela gestão.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `fotos` (
  `id_foto`       INT NOT NULL AUTO_INCREMENT,
  `nome_arquivo`  VARCHAR(255) NOT NULL,
  `legenda`       VARCHAR(255) DEFAULT NULL,
  `id_gestor`     INT DEFAULT NULL,
  `data_postagem` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_foto`),
  KEY `idx_fotos_gestor` (`id_gestor`),
  CONSTRAINT `fk_fotos_gestor` FOREIGN KEY (`id_gestor`)
    REFERENCES `gestão` (`id_gestor`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ---------------------------------------------------------------------
-- Comentários dos alunos nas fotos (somem junto com a foto ou o aluno).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `comentarios` (
  `id_comentario`   INT NOT NULL AUTO_INCREMENT,
  `id_foto`         INT NOT NULL,
  `id_aluno`        INT NOT NULL,
  `texto`           VARCHAR(500) NOT NULL,
  `data_comentario` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_comentario`),
  KEY `idx_comentarios_foto` (`id_foto`),
  KEY `idx_comentarios_aluno` (`id_aluno`),
  CONSTRAINT `fk_comentarios_foto` FOREIGN KEY (`id_foto`)
    REFERENCES `fotos` (`id_foto`) ON DELETE CASCADE,
  CONSTRAINT `fk_comentarios_aluno` FOREIGN KEY (`id_aluno`)
    REFERENCES `aluno` (`id_aluno`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ---------------------------------------------------------------------
-- Mensagens entre alunos e gestão.
--   direcao = 'aluno_para_gestao': id_aluno = quem escreveu, id_gestor NULL
--   direcao = 'gestao_para_aluno': id_aluno = quem recebe (NULL = todos),
--                                  id_gestor = quem escreveu
-- `lida` só vale pra mensagens individuais.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `mensagens` (
  `id_mensagem` INT NOT NULL AUTO_INCREMENT,
  `direcao`     ENUM('aluno_para_gestao', 'gestao_para_aluno') NOT NULL,
  `id_aluno`    INT DEFAULT NULL,
  `id_gestor`   INT DEFAULT NULL,
  `assunto`     VARCHAR(150)  NOT NULL,
  `texto`       VARCHAR(2000) NOT NULL,
  `lida`        TINYINT(1) NOT NULL DEFAULT 0,
  `data_envio`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mensagem`),
  KEY `idx_mensagens_aluno` (`id_aluno`),
  KEY `idx_mensagens_gestor` (`id_gestor`),
  CONSTRAINT `fk_mensagens_aluno` FOREIGN KEY (`id_aluno`)
    REFERENCES `aluno` (`id_aluno`) ON DELETE CASCADE,
  CONSTRAINT `fk_mensagens_gestor` FOREIGN KEY (`id_gestor`)
    REFERENCES `gestão` (`id_gestor`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ---------------------------------------------------------------------
-- Dados de exemplo: só listas de turma fictícias (sem login e sem senha),
-- pra o painel não ficar vazio. Pode apagar quando quiser.
-- INSERT IGNORE: rodar de novo não duplica (o RA é único).
-- ---------------------------------------------------------------------
INSERT IGNORE INTO `turmas` (`ra_aluno`, `nome_aluno`, `turma`) VALUES
  ('98765321',  'davi',     '3_ano_B'),
  ('45678997',  'vitoria',  '3_ano_B'),
  ('23664674',  'felipe',   '8_ano_c'),
  ('329574475', 'ana',      '8_ano_c'),
  ('443847577', 'fernando', '6_ano_c'),
  ('275787257', 'maria',    '6_ano_c');
