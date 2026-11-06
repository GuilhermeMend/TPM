-- --------------------------------------------------------
-- Servidor:                     127.0.0.1
-- Versão do servidor:           12.2.2-MariaDB - MariaDB Server
-- OS do Servidor:               Win64
-- HeidiSQL Versão:              12.14.0.7165
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Copiando estrutura do banco de dados para banco de dados
CREATE DATABASE IF NOT EXISTS `banco de dados` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `banco de dados`;

-- Copiando estrutura para tabela banco de dados.aluno
CREATE TABLE IF NOT EXISTS `aluno` (
  `id_aluno` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) DEFAULT NULL,
  `senha` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_aluno`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Copiando dados para a tabela banco de dados.aluno: ~5 rows (aproximadamente)
INSERT INTO `aluno` (`id_aluno`, `nome`, `senha`) VALUES
	(2, 'aluno', 'lea'),
	(24, 'DAVI', '018KIWI'),
	(27, 'Eduardo Leandro Nascimento', '1234'),
	(28, 'Guilherme Mendonça', 'senha'),
	(29, 'Thalys Lopes', 'Marvel');

-- Copiando estrutura para tabela banco de dados.comentarios
CREATE TABLE IF NOT EXISTS `comentarios` (
  `id_comentario` int(11) NOT NULL AUTO_INCREMENT,
  `id_foto` int(11) NOT NULL,
  `id_aluno` int(11) NOT NULL,
  `texto` varchar(500) NOT NULL,
  `data_comentario` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id_comentario`),
  KEY `id_foto` (`id_foto`),
  KEY `id_aluno` (`id_aluno`),
  CONSTRAINT `1` FOREIGN KEY (`id_foto`) REFERENCES `fotos` (`id_foto`) ON DELETE CASCADE,
  CONSTRAINT `2` FOREIGN KEY (`id_aluno`) REFERENCES `aluno` (`id_aluno`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Copiando dados para a tabela banco de dados.comentarios: ~0 rows (aproximadamente)

-- Copiando estrutura para tabela banco de dados.fotos
CREATE TABLE IF NOT EXISTS `fotos` (
  `id_foto` int(11) NOT NULL AUTO_INCREMENT,
  `nome_arquivo` varchar(255) NOT NULL,
  `legenda` varchar(255) DEFAULT NULL,
  `id_gestor` int(11) DEFAULT NULL,
  `data_postagem` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id_foto`),
  KEY `id_gestor` (`id_gestor`),
  CONSTRAINT `1` FOREIGN KEY (`id_gestor`) REFERENCES `gestão` (`id_gestor`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Copiando dados para a tabela banco de dados.fotos: ~0 rows (aproximadamente)

-- Copiando estrutura para tabela banco de dados.gestão
CREATE TABLE IF NOT EXISTS `gestão` (
  `id_gestor` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) DEFAULT NULL,
  `senha` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_gestor`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Copiando dados para a tabela banco de dados.gestão: ~2 rows (aproximadamente)
INSERT INTO `gestão` (`id_gestor`, `nome`, `senha`) VALUES
	(1, 'prof', 'admin'),
	(2, 'black', '01867');

-- Copiando estrutura para tabela banco de dados.turmas
CREATE TABLE IF NOT EXISTS `turmas` (
  `id_aluno` int(11) NOT NULL AUTO_INCREMENT,
  `ra_aluno` varchar(50) DEFAULT NULL,
  `nome_aluno` varchar(50) DEFAULT NULL,
  `turma` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_aluno`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Copiando dados para a tabela banco de dados.turmas: ~6 rows (aproximadamente)
INSERT INTO `turmas` (`id_aluno`, `ra_aluno`, `nome_aluno`, `turma`) VALUES
	(3, '98765321', 'davi', '3_ano_B'),
	(4, '45678997', 'vitoria', '3_ano_B'),
	(5, '23664674', 'felipe', '8_ano_c'),
	(6, '329574475', 'ana', '8_ano_c'),
	(7, '443847577', 'fernando', '6_ano_c'),
	(8, '275787257', 'maria', '6_ano_c');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

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

-- =====================================================
-- Senhas com hash: a coluna precisa de mais espaço (o hash tem
-- ~160 caracteres). Depois de rodar este script, rode UMA vez
-- `python migrar_senhas.py` para converter as senhas de exemplo.
-- =====================================================
ALTER TABLE `aluno` MODIFY `senha` VARCHAR(255);
ALTER TABLE `gestão` MODIFY `senha` VARCHAR(255);
