-- Sample data for Cloud Inventory System

-- Insert supervisors
INSERT INTO supervisores (id, nombre, email, telefono, permiso) VALUES
('sup001', 'Juan Martinez', 'juan.martinez@empresa.com', '555-0101', 'admin'),
('sup002', 'Ana Garcia', 'ana.garcia@empresa.com', '555-0102', 'avanzado'),
('sup003', 'Carlos Rodriguez', 'carlos.rodriguez@empresa.com', '555-0103', 'basico');

-- Insert machines
INSERT INTO maquinas (id, nombre, categoria, estado, ultimo_mantenimiento, codigo_qr, supervisor_id) VALUES
('maq001', 'Laptop Dell XPS', 'Computadoras', 'disponible', '2024-01-15', 'QR001', 'sup001'),
('maq002', 'Impresora HP LaserJet', 'Impresoras', 'en_uso', '2024-01-10', 'QR002', 'sup002'),
('maq003', 'Proyector Epson', 'Proyectores', 'mantenimiento', '2024-01-05', 'QR003', 'sup001'),
('maq004', 'MacBook Pro', 'Computadoras', 'disponible', '2024-01-20', 'QR004', 'sup002'),
('maq005', 'Scanner Fujitsu', 'Scanners', 'en_uso', '2024-01-12', 'QR005', 'sup003');

-- Insert loans
INSERT INTO prestamos (id, maquina_id, supervisor_id, fecha_prestamo, fecha_devolucion, observaciones) VALUES
('pres001', 'maq002', 'sup002', '2024-01-16 09:00:00', NULL, 'Prestamo para proyecto A'),
('pres002', 'maq005', 'sup003', '2024-01-17 14:30:00', NULL, 'Prestamo para digitalizacion'),
('pres003', 'maq001', 'sup001', '2024-01-10 11:00:00', '2024-01-15 16:00:00', 'Prestamo completado');

-- Insert maintenance records
INSERT INTO mantenimientos (id, maquina_id, supervisor_id, severidad, descripcion_problema, estado) VALUES
('mant001', 'maq003', 'sup001', 'media', 'Revision periodica del proyector', 'en_progreso');