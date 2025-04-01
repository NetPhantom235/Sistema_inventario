-- MySQL Schema for Cloud Inventory System
-- Enterprise-grade structure with AWS/Azure/Google Cloud patterns

CREATE DATABASE IF NOT EXISTS cloud_inventory
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cloud_inventory;

-- Core Entities
CREATE TABLE IF NOT EXISTS maquinas (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    categoria VARCHAR(100),
    estado ENUM('disponible', 'en_uso', 'mantenimiento') NOT NULL DEFAULT 'disponible',
    ultimo_mantenimiento DATE,
    codigo_qr VARCHAR(255),
    supervisor_id VARCHAR(36),
    ubicacion VARCHAR(100),
    especificaciones JSON,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_estado (estado),
    INDEX idx_categoria (categoria),
    INDEX idx_ubicacion (ubicacion)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS supervisores (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    permiso ENUM('basico', 'avanzado', 'admin') NOT NULL DEFAULT 'basico',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME,
    INDEX idx_permiso (permiso)
) ENGINE=InnoDB;

-- Resource Tracking
CREATE TABLE IF NOT EXISTS prestamos (
    id VARCHAR(36) PRIMARY KEY,
    maquina_id VARCHAR(36) NOT NULL,
    supervisor_id VARCHAR(36) NOT NULL,
    fecha_prestamo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_devolucion DATETIME,
    observaciones TEXT,
    estado ENUM('activo', 'completado', 'vencido') NOT NULL DEFAULT 'activo',
    codigo_prestamo VARCHAR(128) UNIQUE,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id),
    FOREIGN KEY (supervisor_id) REFERENCES supervisores(id),
    INDEX idx_estado_prestamo (estado),
    INDEX idx_fechas (fecha_prestamo, fecha_devolucion)
) ENGINE=InnoDB;

-- Maintenance System
CREATE TABLE IF NOT EXISTS mantenimientos (
    id VARCHAR(36) PRIMARY KEY,
    maquina_id VARCHAR(36) NOT NULL,
    supervisor_id VARCHAR(36) NOT NULL,
    severidad ENUM('critica', 'alta', 'media', 'baja') NOT NULL,
    descripcion_problema TEXT NOT NULL,
    detalles_resolucion TEXT,
    estado ENUM('reportado', 'en_progreso', 'resuelto') NOT NULL DEFAULT 'reportado',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion DATETIME,
    costo DECIMAL(10,2),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id),
    FOREIGN KEY (supervisor_id) REFERENCES supervisores(id),
    INDEX idx_estado_mant (estado)
) ENGINE=InnoDB;

-- Audit System
CREATE TABLE IF NOT EXISTS auditoria (
    id VARCHAR(36) PRIMARY KEY,
    tabla_afectada VARCHAR(100) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    usuario_id VARCHAR(36) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos_anteriores TEXT,
    datos_nuevos TEXT,
    INDEX idx_auditoria_fecha (fecha),
    INDEX idx_auditoria_usuario (usuario_id)
) ENGINE=InnoDB;

-- Movement History
CREATE TABLE IF NOT EXISTS historial_movimientos (
    id VARCHAR(36) PRIMARY KEY,
    maquina_id VARCHAR(36) NOT NULL,
    ubicacion_anterior VARCHAR(100),
    ubicacion_nueva VARCHAR(100) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    supervisor_id VARCHAR(36) NOT NULL,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id),
    FOREIGN KEY (supervisor_id) REFERENCES supervisores(id),
    INDEX idx_movimientos_fecha (fecha)
) ENGINE=InnoDB;

-- Reference Tables
CREATE TABLE IF NOT EXISTS ubicaciones (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    zona ENUM('norte', 'sur', 'este', 'oeste', 'central') NOT NULL,
    descripcion TEXT,
    capacidad INT,
    INDEX idx_zona (zona)
) ENGINE=InnoDB;

-- Security Tables
CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB;

-- Versioning Table
CREATE TABLE IF NOT EXISTS version_schema (
    version VARCHAR(32) PRIMARY KEY,
    fecha_aplicacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64) NOT NULL
) ENGINE=InnoDB;