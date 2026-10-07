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
