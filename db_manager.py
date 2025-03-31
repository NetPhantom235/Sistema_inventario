import mysql.connector
import json
from typing import Optional, Dict, List
from datetime import datetime
from mysql.connector import Error

class DatabaseManager:
    def __init__(self, config_path: str = 'config/db_config.json'):
        self.config = self._load_config(config_path)
        self.connection = self._create_connection()
        self._initialize_database()

    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON format in configuration file: {config_path}")

    def _create_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                autocommit=True
            )
            if connection.is_connected():
                print("[INFO] Database connection established.")
            return connection
        except Error as e:
            raise Exception(f"Error connecting to the database: {e}")

    def _execute_write(self, query: str, params: tuple) -> bool:
        try:
            if not self.connection.is_connected():
                self.connection.reconnect()
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                return True
        except Error as e:
            print(f"[ERROR] Database write error: {e}")
            self.connection.rollback()
            return False

    def _execute_read(self, query: str, params: tuple = None) -> List[Dict]:
        try:
            if not self.connection.is_connected():
                self.connection.reconnect()
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Error as e:
            print(f"[ERROR] Database read error: {e}")
            return []

    def _initialize_database(self):
        try:
            with self.connection.cursor() as cursor:
                # Create tables if they don't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS maquinas (
                        id VARCHAR(36) PRIMARY KEY,
                        nombre VARCHAR(255) NOT NULL,
                        categoria VARCHAR(100),
                        estado ENUM('disponible', 'en_uso', 'mantenimiento'),
                        ultimo_mantenimiento DATE,
                        codigo_qr VARCHAR(255),
                        supervisor_id VARCHAR(36)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS supervisores (
                        id VARCHAR(36) PRIMARY KEY,
                        nombre VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE,
                        telefono VARCHAR(20),
                        permiso ENUM('basico', 'avanzado', 'admin'),
                        fecha_registro DATETIME
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prestamos (
                        id VARCHAR(36) PRIMARY KEY,
                        maquina_id VARCHAR(36) NOT NULL,
                        supervisor_id VARCHAR(36) NOT NULL,
                        fecha_prestamo DATETIME NOT NULL,
                        fecha_devolucion DATETIME,
                        observaciones TEXT,
                        FOREIGN KEY (maquina_id) REFERENCES maquinas(id),
                        FOREIGN KEY (supervisor_id) REFERENCES supervisores(id)
                    )
                """)
                self.connection.commit()
                print("[INFO] Database initialized successfully.")
        except Error as e:
            raise Exception(f"Error initializing the database: {e}")

    def crear_maquina(self, maquina_data: Dict) -> bool:
        if not maquina_data.get('id') or not maquina_data.get('nombre'):
            raise ValueError("Machine ID and name are required.")
        query = """
            INSERT INTO maquinas (id, nombre, categoria, estado, ultimo_mantenimiento, codigo_qr, supervisor_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            maquina_data.get('id'),
            maquina_data.get('nombre'),
            maquina_data.get('categoria'),
            maquina_data.get('estado', 'disponible'),
            maquina_data.get('ultimo_mantenimiento'),
            maquina_data.get('codigo_qr'),
            maquina_data.get('supervisor_id')
        )
        return self._execute_write(query, params)

    def obtener_maquinas(self, filters: Dict = None) -> List[Dict]:
        query = """
            SELECT
                id AS `id`,
                nombre AS `nombre`,
                categoria AS `categoria`,
                estado AS `estado`,
                ultimo_mantenimiento AS `ultimo_mantenimiento`,
                supervisor_id
            FROM maquinas
        """
        params = []
        if filters:
            where_clauses = []
            for key, value in filters.items():
                where_clauses.append(f"{key} = %s")
                params.append(value)
            query += " WHERE " + " AND ".join(where_clauses)
        return self._execute_read(query, tuple(params))

    def crear_supervisor(self, supervisor_data: Dict) -> bool:
        if not supervisor_data.get('id') or not supervisor_data.get('nombre') or not supervisor_data.get('email'):
            raise ValueError("Supervisor ID, name, and email are required.")
        query = """
            INSERT INTO supervisores (id, nombre, email, telefono, permiso, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            supervisor_data.get('id'),
            supervisor_data.get('nombre'),
            supervisor_data.get('email'),
            supervisor_data.get('telefono'),
            supervisor_data.get('permiso', 'basico'),
            datetime.now()
        )
        return self._execute_write(query, params)

    def obtener_supervisores(self, filters: Dict = None) -> List[Dict]:
        query = "SELECT id, nombre, email, telefono, permiso, fecha_registro FROM supervisores"
        params = []
        if filters:
            where_clauses = []
            for key, value in filters.items():
                where_clauses.append(f"{key} = %s")
                params.append(value)
            query += " WHERE " + " AND ".join(where_clauses)
        return self._execute_read(query, tuple(params))

    def crear_prestamo(self, prestamo_data: Dict) -> bool:
        if not prestamo_data.get('id') or not prestamo_data.get('maquina_id') or not prestamo_data.get('supervisor_id'):
            raise ValueError("Loan ID, machine ID, and supervisor ID are required.")
        query = """
            INSERT INTO prestamos (id, maquina_id, supervisor_id, fecha_prestamo, observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            prestamo_data.get('id'),
            prestamo_data.get('maquina_id'),
            prestamo_data.get('supervisor_id'),
            datetime.now(),
            prestamo_data.get('observaciones')
        )
        return self._execute_write(query, params)

    def finalizar_prestamo(self, prestamo_id: str) -> bool:
        query = "UPDATE prestamos SET fecha_devolucion = %s WHERE id = %s"
        params = (datetime.now(), prestamo_id)
        return self._execute_write(query, params)

    def obtener_prestamos(self, filters: Dict = None) -> List[Dict]:
        query = """
            SELECT p.*, m.nombre as maquina_nombre, s.nombre as supervisor_nombre 
            FROM prestamos p
            JOIN maquinas m ON p.maquina_id = m.id
            JOIN supervisores s ON p.supervisor_id = s.id
        """
        params = []
        if filters:
            where_clauses = []
            for key, value in filters.items():
                where_clauses.append(f"p.{key} = %s")
                params.append(value)
            query += " WHERE " + " AND ".join(where_clauses)
        return self._execute_read(query, tuple(params))

    def begin_transaction(self):
        self.connection.start_transaction()

    def commit_transaction(self):
        self.connection.commit()

    def rollback_transaction(self):
        self.connection.rollback()

    def __del__(self):
        if self.connection.is_connected():
            self.connection.close()
            print("[INFO] Database connection closed.")