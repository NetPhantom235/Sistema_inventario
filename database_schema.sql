-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- -----------------------------------------------------
-- Schema gestion_maquinas
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `gestion_maquinas` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- -----------------------------------------------------
-- Table `gestion_maquinas`.`supervisores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gestion_maquinas`.`supervisores` (
  `id` CHAR(36) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `telefono` VARCHAR(20) NULL,
  `permiso` ENUM('basico', 'avanzado', 'admin') NOT NULL DEFAULT 'basico',
  `fecha_registro` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `gestion_maquinas`.`maquinas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gestion_maquinas`.`maquinas` (
  `id` CHAR(36) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `categoria` VARCHAR(100) NOT NULL,
  `estado` ENUM('disponible', 'en_uso', 'mantenimiento') NOT NULL DEFAULT 'disponible',
  `ultimo_mantenimiento` DATE NULL,
  `codigo_qr` VARCHAR(255) NULL,
  `supervisor_id` CHAR(36) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_maquinas_supervisores_idx` (`supervisor_id` ASC) VISIBLE,
  INDEX `idx_estado` (`estado` ASC) VISIBLE,
  CONSTRAINT `fk_maquinas_supervisores`
    FOREIGN KEY (`supervisor_id`)
    REFERENCES `gestion_maquinas`.`supervisores` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `gestion_maquinas`.`prestamos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gestion_maquinas`.`prestamos` (
  `id` CHAR(36) NOT NULL,
  `maquina_id` CHAR(36) NOT NULL,
  `supervisor_id` CHAR(36) NOT NULL,
  `fecha_prestamo` DATETIME NOT NULL,
  `fecha_devolucion` DATETIME NULL,
  `observaciones` TEXT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_prestamos_maquinas_idx` (`maquina_id` ASC) VISIBLE,
  INDEX `fk_prestamos_supervisores_idx` (`supervisor_id` ASC) VISIBLE,
  INDEX `idx_fecha_prestamo` (`fecha_prestamo` DESC) VISIBLE,
  CONSTRAINT `fk_prestamos_maquinas`
    FOREIGN KEY (`maquina_id`)
    REFERENCES `gestion_maquinas`.`maquinas` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_prestamos_supervisores`
    FOREIGN KEY (`supervisor_id`)
    REFERENCES `gestion_maquinas`.`supervisores` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `gestion_maquinas`.`mantenimientos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gestion_maquinas`.`mantenimientos` (
  `id` CHAR(36) NOT NULL,
  `maquina_id` CHAR(36) NOT NULL,
  `fecha_inicio` DATETIME NOT NULL,
  `fecha_fin` DATETIME NULL,
  `descripcion` TEXT NOT NULL,
  `tecnico` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_mantenimientos_maquinas_idx` (`maquina_id` ASC) VISIBLE,
  CONSTRAINT `fk_mantenimientos_maquinas`
    FOREIGN KEY (`maquina_id`)
    REFERENCES `gestion_maquinas`.`maquinas` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data Population Script
-- -----------------------------------------------------
-- Add sample supervisors
INSERT INTO supervisores (id, nombre, email, telefono, permiso, fecha_registro) VALUES
(UUID(), 'Juan Perez', 'juan@empresa.com', '+54912345678', 'admin', NOW()),
(UUID(), 'Maria Gomez', 'maria@empresa.com', '+54987654321', 'avanzado', NOW());

-- Add maintenance user
CREATE USER 'gestion_app'@'localhost' IDENTIFIED BY 'SecurePass123!';
GRANT ALL PRIVILEGES ON gestion_maquinas.* TO 'gestion_app'@'localhost';
FLUSH PRIVILEGES;