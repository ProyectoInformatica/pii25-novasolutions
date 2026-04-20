-- MariaDB dump - Nova Solutions Sistema de Monitoreo
-- Host: localhost    Database: pii26-novasolutions
-- Server version: 10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE IF NOT EXISTS `pii26-novasolutions`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;
USE `pii26-novasolutions`;

-- ============================================================
-- DROP en orden inverso a las FK para evitar conflictos
-- ============================================================

DROP TABLE IF EXISTS `user_mira_sensor`;
DROP TABLE IF EXISTS `envia_recibe`;
DROP TABLE IF EXISTS `mensaje`;
DROP TABLE IF EXISTS `registros`;
DROP TABLE IF EXISTS `actuador`;
DROP TABLE IF EXISTS `sensor`;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `escuela`;

-- ============================================================
-- ENTIDADES
-- ============================================================

-- ------------------------------------------------------------
-- Tabla: escuela
-- Entidad propia que resuelve la dependencia transitiva que
-- existia en sensor (sensor.escuela TEXT era dependencia
-- transitiva: sensor.id -> id_escuela -> escuela.nombre).
-- Ahora sensor.id_escuela es FK, cumpliendo la 3FN.
-- ------------------------------------------------------------
CREATE TABLE `escuela` (
  `id`         INT           NOT NULL AUTO_INCREMENT,
  `nombre`     VARCHAR(100)  NOT NULL,
  `direccion`  VARCHAR(200)  NOT NULL,
  `activo`     TINYINT(1)    NOT NULL DEFAULT 1,
  `fecha_baja` TIMESTAMP     NULL     DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ------------------------------------------------------------
-- Tabla: user
-- password almacena el hash SHA-256 de (plaintext || salt).
-- foto_perfil es un dato binario (LONGBLOB).
-- activo / fecha_baja permiten baja logica sin borrar filas.
-- ------------------------------------------------------------
CREATE TABLE `user` (
  `id`          INT           NOT NULL AUTO_INCREMENT,
  `nombre`      VARCHAR(100)  NOT NULL,
  `apellido`    VARCHAR(100)  NOT NULL,
  `mail`        VARCHAR(150)  NOT NULL,
  `password`    VARCHAR(64)   NOT NULL,
  `salt`        VARCHAR(64)   NOT NULL,
  `tipo`        ENUM('0','1') NOT NULL DEFAULT '0',
  `foto_perfil` LONGBLOB      DEFAULT NULL,
  `activo`      TINYINT(1)    NOT NULL DEFAULT 1,
  `fecha_baja`  TIMESTAMP     NULL     DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_mail` (`mail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ------------------------------------------------------------
-- Tabla: sensor
-- id_escuela sustituye al antiguo campo TEXT escuela.
-- hora registra cuando se instalo el sensor en el sistema.
-- activo / fecha_baja permiten baja logica.
-- ------------------------------------------------------------
CREATE TABLE `sensor` (
  `id`          INT          NOT NULL AUTO_INCREMENT,
  `tipo_sensor` VARCHAR(50)  NOT NULL,
  `ubicacion`   VARCHAR(100) NOT NULL,
  `id_escuela`  INT          NOT NULL,
  `hora`        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `activo`      TINYINT(1)   NOT NULL DEFAULT 1,
  `fecha_baja`  TIMESTAMP    NULL     DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sensor_escuela` (`id_escuela`),
  CONSTRAINT `fk_sensor_escuela`
    FOREIGN KEY (`id_escuela`) REFERENCES `escuela` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ------------------------------------------------------------
-- Tabla: actuador
-- Estaba en el codigo Python pero faltaba en el esquema SQL.
-- ------------------------------------------------------------
CREATE TABLE `actuador` (
  `id`                  INT          NOT NULL AUTO_INCREMENT,
  `nombre`              VARCHAR(100) NOT NULL,
  `tipo`                VARCHAR(50)  NOT NULL,
  `estado_actual`       TINYINT(1)   NOT NULL DEFAULT 0,
  `id_sensor_vinculado` INT          NOT NULL,
  `activo`              TINYINT(1)   NOT NULL DEFAULT 1,
  `fecha_baja`          TIMESTAMP    NULL     DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_actuador_sensor` (`id_sensor_vinculado`),
  CONSTRAINT `fk_actuador_sensor`
    FOREIGN KEY (`id_sensor_vinculado`) REFERENCES `sensor` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ------------------------------------------------------------
-- Tabla: registros
-- Historial de lecturas de sensores.
-- ------------------------------------------------------------
CREATE TABLE `registros` (
  `id`        INT       NOT NULL AUTO_INCREMENT,
  `medida`    FLOAT     NOT NULL,
  `hora`      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_sensor` INT       NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_registros_sensor` (`id_sensor`),
  CONSTRAINT `fk_registros_sensor`
    FOREIGN KEY (`id_sensor`) REFERENCES `sensor` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ------------------------------------------------------------
-- Tabla: mensaje
-- Mensajes internos del sistema.
-- estado '0' = no leido, '1' = leido.
-- ------------------------------------------------------------
CREATE TABLE `mensaje` (
  `id`         INT           NOT NULL AUTO_INCREMENT,
  `contenido`  TEXT          NOT NULL,
  `hora`       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `estado`     ENUM('0','1') NOT NULL DEFAULT '0',
  `activo`     TINYINT(1)    NOT NULL DEFAULT 1,
  `fecha_baja` TIMESTAMP     NULL     DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================================
-- RELACIONES
-- ============================================================

-- ------------------------------------------------------------
-- Tabla: envia_recibe
-- id_user1 = remitente, id_user2 = destinatario.
-- fecha_envio registra el momento exacto del envio de cada
-- mensaje a su destinatario (antes solo existia hora en mensaje).
-- ------------------------------------------------------------
CREATE TABLE `envia_recibe` (
  `id_mensaje`  INT       NOT NULL,
  `id_user1`    INT       NOT NULL,
  `id_user2`    INT       NOT NULL,
  `fecha_envio` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mensaje`),
  KEY `idx_envia_recibe_user1` (`id_user1`),
  KEY `idx_envia_recibe_user2` (`id_user2`),
  CONSTRAINT `envia_recibe_ibfk_1`
    FOREIGN KEY (`id_mensaje`) REFERENCES `mensaje` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `envia_recibe_ibfk_2`
    FOREIGN KEY (`id_user1`) REFERENCES `user` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `envia_recibe_ibfk_3`
    FOREIGN KEY (`id_user2`) REFERENCES `user` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ------------------------------------------------------------
-- Tabla: user_mira_sensor
-- fecha_asignacion registra cuando se asigno el sensor al
-- usuario (antes la relacion no tenia registro temporal).
-- ------------------------------------------------------------
CREATE TABLE `user_mira_sensor` (
  `id_user`          INT       NOT NULL,
  `id_sensor`        INT       NOT NULL,
  `fecha_asignacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_user`, `id_sensor`),
  KEY `idx_user_mira_sensor_sensor` (`id_sensor`),
  CONSTRAINT `user_mira_sensor_ibfk_1`
    FOREIGN KEY (`id_user`) REFERENCES `user` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user_mira_sensor_ibfk_2`
    FOREIGN KEY (`id_sensor`) REFERENCES `sensor` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ============================================================
-- CONJUNTO DE PRUEBA REPRESENTATIVO
-- ============================================================

-- Escuelas
INSERT INTO `escuela` (`id`, `nombre`, `direccion`) VALUES
(1, 'IES Ramiro de Maeztu', 'Calle Serrano Anguita 10, Madrid'),
(2, 'IES Complutense',      'Calle de la Universidad 1, Alcala de Henares');

-- Usuarios
-- Las contrasenas se almacenan como SHA2(plaintext || salt, 256):
--   director@escuela.com  ->  admin123
--   juan@escuela.com      ->  mante123
--   maria@escuela.com     ->  mante456
-- foto_perfil del director: primeros bytes de cabecera PNG (dato binario de prueba)
INSERT INTO `user` (`id`, `nombre`, `apellido`, `mail`, `password`, `salt`, `tipo`, `foto_perfil`) VALUES
(1, 'Admin', 'Sistema', 'director@escuela.com',
   SHA2(CONCAT('admin123', 'saltdir001'), 256), 'saltdir001', '1',
   0x89504e470d0a1a0a0000000d49484452),
(2, 'Juan',  'Garcia',  'juan@escuela.com',
   SHA2(CONCAT('mante123', 'saltjua001'), 256), 'saltjua001', '0', NULL),
(3, 'Maria', 'Lopez',   'maria@escuela.com',
   SHA2(CONCAT('mante456', 'saltmar001'), 256), 'saltmar001', '0', NULL);

-- Sensores (5 tipos distintos, 2 escuelas)
INSERT INTO `sensor` (`id`, `tipo_sensor`, `ubicacion`, `id_escuela`) VALUES
(1, 'temperature', 'Laboratorio de Fisica', 1),
(2, 'smoke',       'Cocina',                1),
(3, 'light',       'Pasillo Principal',     1),
(4, 'distance',    'Entrada Principal',     1),
(5, 'airQuality',  'Sala de Informatica',   2);

-- Actuadores (uno por tipo de sensor, vinculados a sus sensores)
INSERT INTO `actuador` (`id`, `nombre`, `tipo`, `estado_actual`, `id_sensor_vinculado`) VALUES
(1, 'Ventilador Norte', 'Ventilador',   0, 1),
(2, 'Rociador Cocina',  'Rociador',     0, 2),
(3, 'Luz Principal',    'Luz Exterior', 1, 3),
(4, 'Luz Entrada',      'Luz Pasillo',  0, 4);

-- Registros historicos (lecturas que cubren todos los umbrales de alarma)
INSERT INTO `registros` (`id`, `medida`, `hora`, `id_sensor`) VALUES
-- Temperatura (sensor 1): una lectura supera umbral 35 grados
(1,  22.5, '2026-04-18 08:00:00', 1),
(2,  24.1, '2026-04-18 10:00:00', 1),
(3,  29.8, '2026-04-18 12:00:00', 1),
(4,  35.6, '2026-04-18 14:00:00', 1),
(5,  31.2, '2026-04-18 16:00:00', 1),
(6,  23.0, '2026-04-19 08:00:00', 1),
-- Humo (sensor 2): una lectura supera umbral 0.6
(7,  0.05, '2026-04-18 08:00:00', 2),
(8,  0.12, '2026-04-18 12:00:00', 2),
(9,  0.72, '2026-04-18 13:30:00', 2),
(10, 0.08, '2026-04-18 14:00:00', 2),
-- Luz (sensor 3): lecturas nocturnas por debajo de 400 lux
(11, 520.0, '2026-04-18 08:00:00', 3),
(12, 460.0, '2026-04-18 10:00:00', 3),
(13, 370.0, '2026-04-18 18:00:00', 3),
(14, 290.0, '2026-04-18 20:00:00', 3),
-- Distancia (sensor 4): deteccion de personas (< 50 cm)
(15, 80.0, '2026-04-18 08:00:00', 4),
(16, 42.0, '2026-04-18 09:15:00', 4),
(17, 25.0, '2026-04-18 09:16:00', 4),
(18, 78.0, '2026-04-18 09:20:00', 4),
-- Calidad del aire (sensor 5): variacion diaria
(19, 12.0, '2026-04-18 08:00:00', 5),
(20, 28.0, '2026-04-18 12:00:00', 5),
(21, 65.0, '2026-04-18 15:00:00', 5),
(22, 18.0, '2026-04-19 08:00:00', 5);

-- Mensajes del sistema
INSERT INTO `mensaje` (`id`, `contenido`, `hora`, `estado`) VALUES
(1, 'Alerta: temperatura por encima de 35C en Laboratorio de Fisica.',  '2026-04-18 14:01:00', '0'),
(2, 'Alerta: nivel de humo elevado detectado en Cocina.',               '2026-04-18 13:31:00', '1'),
(3, 'Aviso: nivel de luz bajo en Pasillo Principal, luces activadas.',  '2026-04-18 18:01:00', '0');

-- Relaciones de envio (tecnicos notifican al director)
INSERT INTO `envia_recibe` (`id_mensaje`, `id_user1`, `id_user2`, `fecha_envio`) VALUES
(1, 2, 1, '2026-04-18 14:01:00'),
(2, 3, 1, '2026-04-18 13:31:00'),
(3, 2, 1, '2026-04-18 18:01:00');

-- Asignacion de sensores a usuarios (con fecha de asignacion)
INSERT INTO `user_mira_sensor` (`id_user`, `id_sensor`, `fecha_asignacion`) VALUES
(1, 1, '2026-04-01 09:00:00'),
(1, 2, '2026-04-01 09:00:00'),
(1, 3, '2026-04-01 09:00:00'),
(2, 1, '2026-04-01 09:00:00'),
(2, 3, '2026-04-01 09:00:00'),
(2, 4, '2026-04-01 09:00:00'),
(3, 5, '2026-04-02 10:00:00');


-- ============================================================
-- BAJA LOGICA: como dar de baja sin borrar datos
-- ============================================================

-- Dar de baja un sensor (no se elimina, solo se marca):
-- UPDATE sensor SET activo = 0, fecha_baja = NOW() WHERE id = 5;

-- Dar de baja un usuario de mantenimiento (director protegido por tipo != '1'):
-- UPDATE user SET activo = 0, fecha_baja = NOW() WHERE id = 3 AND tipo != '1';

-- Dar de baja un actuador:
-- UPDATE actuador SET activo = 0, fecha_baja = NOW() WHERE id = 4;


-- ============================================================
-- CONSULTAS DE REFERENCIA PARA EL SISTEMA
-- ============================================================

-- SELECT LOGIN: autenticacion completa en SQL, sin procesado local.
-- La comparacion del hash se realiza integramente en el servidor:
--
-- SELECT id, nombre, apellido, mail, tipo
-- FROM user
-- WHERE mail     = 'director@escuela.com'
--   AND password = SHA2(CONCAT('admin123', salt), 256)
--   AND activo   = 1;

-- SENSORES ACTIVOS con nombre de escuela (JOIN, sin SELECT *):
--
-- SELECT s.id, s.tipo_sensor, s.ubicacion, e.nombre AS escuela
-- FROM sensor s
-- JOIN escuela e ON s.id_escuela = e.id
-- WHERE s.activo = 1
-- ORDER BY e.nombre, s.ubicacion;

-- HISTORIAL de lecturas (acotado con LIMIT y ORDER BY):
--
-- SELECT r.hora, s.tipo_sensor, s.ubicacion, e.nombre AS escuela, r.medida
-- FROM registros r
-- JOIN sensor  s ON r.id_sensor  = s.id
-- JOIN escuela e ON s.id_escuela = e.id
-- ORDER BY r.hora DESC
-- LIMIT 100;

-- ACTUADORES ACTIVOS con su sensor vinculado:
--
-- SELECT a.id, a.nombre, a.tipo, a.estado_actual, s.tipo_sensor
-- FROM actuador a
-- JOIN sensor s ON a.id_sensor_vinculado = s.id
-- WHERE a.activo = 1 AND s.activo = 1
-- ORDER BY a.nombre;

-- INSERT usuario nuevo con hash generado en BD:
--
-- INSERT INTO user (nombre, apellido, mail, password, salt, tipo)
-- VALUES ('Pedro', 'Ruiz', 'pedro@escuela.com',
--         SHA2(CONCAT('clave123', 'saltpedro01'), 256), 'saltpedro01', '0');

-- UPDATE estado actuador por PK:
--
-- UPDATE actuador SET estado_actual = 1 WHERE id = 1;


/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-20
