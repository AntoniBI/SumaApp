/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

CREATE DATABASE IF NOT EXISTS `sumalberic` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci */;
USE `sumalberic`;

CREATE TABLE IF NOT EXISTS `instrumentos` (
  `Id_instrumento` int(11) NOT NULL AUTO_INCREMENT,
  `Instrumento` varchar(50) COLLATE utf8mb4_spanish_ci NOT NULL DEFAULT '',
  `Fecha_alta` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `PK_Instrumento` (`Id_instrumento`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

/*!40000 ALTER TABLE `instrumentos` DISABLE KEYS */;
INSERT INTO `instrumentos` (`Id_instrumento`, `Instrumento`, `Fecha_alta`) VALUES
	(1, 'Bombardino', '2025-10-13 18:28:16'),
	(2, 'Clarinet', '2025-10-13 18:28:52'),
	(3, 'Contrabaix', '2025-10-13 18:29:11'),
	(4, 'Director', '2025-10-13 18:29:34'),
	(5, 'Fagot', '2025-10-13 18:29:42'),
	(6, 'Flauta', '2025-10-13 18:29:52'),
	(7, 'Oboe', '2025-10-13 18:29:59'),
	(8, 'Percussio', '2025-10-13 18:30:06'),
	(9, 'Saxo', '2025-10-13 18:30:14'),
	(10, 'Trombo', '2025-10-13 18:30:20'),
	(11, 'Trompa', '2025-10-13 18:30:27'),
	(12, 'Trompeta', '2025-10-13 18:30:32'),
	(13, 'Tuba', '2025-10-13 18:32:15'),
	(14, 'Violoncel', '2025-10-13 18:32:28');
/*!40000 ALTER TABLE `instrumentos` ENABLE KEYS */;

CREATE TABLE IF NOT EXISTS `usuarios` (
  `Id_usuario` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  `usuario` varchar(20) COLLATE utf8mb4_spanish_ci NOT NULL,
  `nombre` varchar(50) COLLATE utf8mb4_spanish_ci NOT NULL,
  `apellidos` varchar(100) COLLATE utf8mb4_spanish_ci NOT NULL,
  `password` varchar(100) COLLATE utf8mb4_spanish_ci NOT NULL,
  `administrador` bit(1) NOT NULL DEFAULT b'0',
  `Id_Instrumento_p` int(11) DEFAULT NULL,
  `Id_Instrumento_s` int(11) DEFAULT NULL,
  `fecha_alta` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_act` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY `PK_Usuario` (`Id_usuario`),
  KEY `FK_Instrumento_Principal` (`Id_Instrumento_p`),
  KEY `FK_Instrumento_Secundario` (`Id_Instrumento_s`),
  CONSTRAINT `FK_Instrumento_Principal` FOREIGN KEY (`Id_Instrumento_p`) REFERENCES `instrumentos` (`Id_instrumento`),
  CONSTRAINT `FK_Instrumento_Secundario` FOREIGN KEY (`Id_Instrumento_s`) REFERENCES `instrumentos` (`Id_instrumento`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` (`Id_usuario`, `usuario`, `nombre`, `apellidos`, `password`, `administrador`, `Id_Instrumento_p`, `Id_Instrumento_s`, `fecha_alta`, `fecha_act`) VALUES
	(1, 'admin', 'nomadminist', 'apellidos admin', '$2y$10$4wbWhFTYF1FRu6NB5Lq0t.4OzQ0lwoSdbVyiueUK2I.qd/uyyfaHm', b'1', NULL, NULL, '2025-10-13 18:35:57', '2025-10-15 17:20:14'),
	(2, 'user', 'nomuserprueba', 'user apellidos', '$2y$10$.f8mbZ/BxxozVp0tjVBfZ.DqgSS0BCanL2bAUm0xFh16qGswknNom', b'0', 8, 9, '2025-10-13 18:36:27', '2025-10-15 16:31:49'),
	(3, 'user2', 'user2nomas ', 'last name', '$2y$10$1mq6sv9w05NFwxwOjssojufYXSXs5YkL9yfpgJlfd5M3pr47prANC', b'0', 12, 2, '2025-10-13 18:37:06', '2025-10-15 18:17:16'),
	(4, 'prova', 'NomProva', 'uno dos', '$2y$10$JIQF5d07Kis6sqPwCAIpROY897.fe/q/Wozg0EPazMa1lMGup1ZRG', b'0', 1, 13, '2025-10-15 17:24:25', '2025-10-15 17:24:25'),
	(6, 'Vik_12', 'Victor', 'Garcia Dauder', '$2y$10$1mHMzJVTlncxhqcoIeUItur/3zbjGUnftBqL7UaFIfzWq11BSolvu', b'1', 12, NULL, '2025-10-15 17:36:07', '2025-10-15 17:36:07'),
	(7, 'prueba2', 'NomProva2', 'tres quatre', '$2y$10$qzzsA5q6UaoKlRUC/Cg1EOnlKfyE7xMdyXdSmNRhBjIr6XnKHN5te', b'0', 6, 13, '2025-10-15 17:39:16', '2025-10-15 17:39:16'),
	(8, 'prueba3', 'NomProva3', 'cinc sis', '$2y$10$tea18AwfoluHwfPBaxxDme2Mhxu57moGVoJLhRrqMcZO6OW1aoHG.', b'1', 4, NULL, '2025-10-15 17:44:15', '2025-10-15 17:44:15'),
	(9, 'prueba4', 'NomProva4', 'set huit', '$2y$10$piPj05kJ8hfqCwVv.62jHO1JfVe0H03I1q0a1Cyj3dk12EIO/zqGy', b'1', 4, NULL, '2025-10-15 17:59:18', '2025-10-15 17:59:18'),
	(10, 'prueba5', 'nomProva5', 'nou deu', '$2y$10$oPYfRBf9nPKMP8f9v/U6AeUPyppop6cBDov3gyvQDH2k4aeZEY6wO', b'0', 7, 11, '2025-10-15 18:17:44', '2025-10-15 18:17:44');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
