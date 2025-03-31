# Sistema de Gestión de Máquinas

## Descripción del Proyecto
Este sistema proporciona una interfaz intuitiva, profesional y bien balanceada visualmente para la gestión de máquinas, préstamos y supervisores. Está inspirado en la claridad y funcionalidad de AWS o Azure, pero con identidad única.

## Estructura del Proyecto

### Archivos de Datos (CSV)
- `data/maquinas.csv`: Almacena información sobre las máquinas (ID, Nombre, Categoría, Estado, Ubicación)
- `data/supervisores.csv`: Almacena información sobre los supervisores (ID, Nombre, Teléfono, Email, Departamento)
- `data/prestamos.csv`: Registra los préstamos de máquinas (Código de Evento, ID Máquina, ID Supervisor, Fechas, Estado)

### Componentes Principales
- **Dashboard**: Resumen ejecutivo con métricas en tiempo real y widgets personalizables
- **Gestión de Recursos**: CRUD para máquinas, supervisores y préstamos
- **Configuración**: Ajustes del sistema y gestión de permisos
- **Reportes**: Exportación de datos y visualización de logs

## Principios de Diseño

### Intuitividad
- Flujo claro entre secciones con menús jerárquicos y rutas visibles
- Iconografía reconocible con tooltips para funciones complejas

### Consistencia
- Sistema de diseño unificado en todas las pantallas (colores, tipografía, espaciado)
- Componentes reutilizables (botones, cards, modales)

### Jerarquía Visual
- Contenido prioritario destacado (métricas clave en dashboards)
- Información progresiva para evitar sobrecarga (acordeones, pestañas)

## Tecnologías Utilizadas
- **Frontend**: PyQt6 con estilos personalizados
- **Backend**: Python con manejo de datos en CSV y MySQL
- **Visualización**: Gráficos interactivos con PyQt6.QtCharts
- **Seguridad**: Autenticación de usuarios y encriptación de datos sensibles

## Funcionalidades por Sección

### Dashboard
- Resumen de máquinas por estado (disponibles, prestadas, en mantenimiento)
- Préstamos activos y próximos a vencer
- Actividad reciente del sistema

### Gestión de Máquinas
- Listado con filtros avanzados
- Creación, edición y eliminación de máquinas
- Generación de códigos QR para identificación

### Gestión de Supervisores
- Registro y administración de supervisores
- Historial de préstamos por supervisor
- Contacto rápido (email, teléfono)

### Gestión de Préstamos
- Registro de nuevos préstamos
- Devolución de máquinas
- Historial y seguimiento de préstamos

### Configuración
- Ajustes del sistema
- Gestión de usuarios y permisos
- Copias de seguridad

### Reportes
- Exportación a PDF/Excel
- Estadísticas de uso
- Logs del sistema

## Instalación y Configuración

### Requisitos
- Python 3.8+
- PyQt6
- MySQL (opcional)
- Dependencias adicionales (ver requirements.txt)

### Configuración
1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar la base de datos (MySQL o usar CSV por defecto)
4. Ejecutar: `python main.py`

## Uso del Sistema

### Acceso
- Usuario por defecto: admin
- Contraseña por defecto: admin123

### Flujo de Trabajo Típico
1. Iniciar sesión en el sistema
2. Navegar al módulo deseado mediante la barra lateral
3. Realizar operaciones CRUD según necesidades
4. Consultar el dashboard para obtener métricas actualizadas
5. Generar reportes según sea necesario

## Mantenimiento

### Copias de Seguridad
- El sistema realiza copias de seguridad automáticas cada hora
- Se pueden realizar copias manuales desde el módulo de configuración

### Logs
- Los eventos del sistema se registran en `system.log`
- Los errores críticos se notifican por email a los administradores