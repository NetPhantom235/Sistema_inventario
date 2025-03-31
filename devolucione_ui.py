from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from db_manager import DatabaseManager

CLOUD_STYLE = """
QWidget {
    background: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QTableWidget {
    background: #2c2c2c;
    gridline-color: #404040;
    border-radius: 4px;
    color: #ffffff;
    font-size: 14px;
}

QHeaderView::section {
    background-color: #333333;
    color: white;
    padding: 8px;
    border: none;
    font-weight: bold;
}

QTableWidget::item {
    border-bottom: 1px solid #404040;
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #0078D4;
    color: #ffffff;
}

QPushButton {
    background-color: #0078d7;
    color: #ffffff;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
    font-size: 14px;
    font-weight: bold;
    transition: background-color 0.3s ease;
}

QPushButton:hover {
    background-color: #005a9e;
}

QPushButton:pressed {
    background-color: #003f73;
}

QComboBox {
    background-color: #2c2c2c;
    color: #ffffff;
    border: 1px solid #404040;
    padding: 5px;
    border-radius: 4px;
}
"""

class DevolucionesUI(QWidget):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.setStyleSheet(CLOUD_STYLE)
        self.db = db
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        self.btn_procesar = QPushButton("Procesar Devolución")
        self.btn_historial = QPushButton("Ver Historial Completo")
        self.btn_reporte = QPushButton("Generar Reporte")
        btn_layout.addWidget(self.btn_procesar)
        btn_layout.addWidget(self.btn_historial)
        btn_layout.addWidget(self.btn_reporte)

        # Dual list container
        list_container = QHBoxLayout()
        
        # Available machines list
        self.tabla_disponibles = QTableWidget()
        self.tabla_disponibles.setColumnCount(3)
        self.tabla_disponibles.setHorizontalHeaderLabels(['ID', 'Máquina', 'Ubicación'])
        self.tabla_disponibles.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Assigned machines list
        self.tabla_asignadas = QTableWidget()
        self.tabla_asignadas.setColumnCount(4)
        self.tabla_asignadas.setHorizontalHeaderLabels(['ID', 'Máquina', 'Supervisor', 'Fecha Asignación'])
        self.tabla_asignadas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Action buttons
        btn_scan = QPushButton('Escanear QR')
        btn_asignar = QPushButton('→ Asignar')
        btn_liberar = QPushButton('← Liberar')
        
        # Supervisor selection
        self.combo_supervisores = QComboBox()
        
        # Add components to layout
        list_container.addWidget(self.tabla_disponibles)
        list_container.addLayout(self.create_action_buttons(btn_scan, btn_asignar, btn_liberar))
        list_container.addWidget(self.tabla_asignadas)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.combo_supervisores)
        layout.addLayout(list_container)
        self.setLayout(layout)

    def create_action_buttons(self, btn_scan, btn_asignar, btn_liberar):
        button_layout = QVBoxLayout()
        button_layout.addWidget(btn_scan)
        button_layout.addWidget(btn_asignar)
        button_layout.addWidget(btn_liberar)
        btn_scan.clicked.connect(self.handle_scan)
        btn_asignar.clicked.connect(lambda: self.move_item(self.tabla_disponibles, self.tabla_asignadas))
        btn_liberar.clicked.connect(lambda: self.move_item(self.tabla_asignadas, self.tabla_disponibles))
        return button_layout

    def move_item(self, source, destination):
        selected = source.currentRow()
        if selected >= 0:
            row_data = [source.item(selected, col).text() for col in range(source.columnCount())]
            destination.insertRow(destination.rowCount())
            for col, data in enumerate(row_data):
                destination.setItem(destination.rowCount()-1, col, QTableWidgetItem(data))
            source.removeRow(selected)
            self.actualizar_asignacion_bd(row_data[0])

    def handle_scan(self):
        machine_id = "SCANNED_ID"  # Placeholder for QR/barcode scanning logic
        for row in range(self.tabla_disponibles.rowCount()):
            if self.tabla_disponibles.item(row, 0).text() == machine_id:
                self.move_item(self.tabla_disponibles, self.tabla_asignadas)
                break

    def actualizar_asignacion_bd(self, machine_id):
        supervisor_id = self.combo_supervisores.currentData()
        if supervisor_id:
            self.db.actualizar_supervisor(machine_id, supervisor_id)

    def cargar_datos(self):
        try:
            # Load available machines
            disponibles = self.db.obtener_maquinas_disponibles()
            self.tabla_disponibles.setRowCount(len(disponibles))
            for i, maq in enumerate(disponibles):
                self.tabla_disponibles.setItem(i, 0, QTableWidgetItem(maq['id']))
                self.tabla_disponibles.setItem(i, 1, QTableWidgetItem(maq['nombre']))
                self.tabla_disponibles.setItem(i, 2, QTableWidgetItem(maq['ubicacion']))

            # Load assigned machines
            asignadas = self.db.obtener_maquinas_asignadas()
            self.tabla_asignadas.setRowCount(len(asignadas))
            for i, maq in enumerate(asignadas):
                self.tabla_asignadas.setItem(i, 0, QTableWidgetItem(maq['id']))
                self.tabla_asignadas.setItem(i, 1, QTableWidgetItem(maq['nombre']))
                self.tabla_asignadas.setItem(i, 2, QTableWidgetItem(maq['supervisor']))
                self.tabla_asignadas.setItem(i, 3, QTableWidgetItem(str(maq['fecha_asignacion'])))

            # Load supervisors
            self.combo_supervisores.clear()
            supervisores = self.db.obtener_supervisores()
            for sup in supervisores:
                self.combo_supervisores.addItem(f"{sup['nombre']} ({sup['id']})", sup['id'])

        except Exception as e:
            self.mostrar_error("Error de carga", f"Error al cargar datos: {str(e)}")

        self.aplicar_estilos_filas()

    def aplicar_estilos_filas(self):
        for row in range(self.tabla_asignadas.rowCount()):
            if self.tabla_asignadas.item(row, 3).text() == 'Pendiente':
                for col in range(self.tabla_asignadas.columnCount()):
                    self.tabla_asignadas.item(row, col).setBackground(QColor('#fff4ce'))

    def mostrar_estado_vacio(self, mensaje):
        self.tabla_asignadas.setRowCount(1)
        self.tabla_asignadas.setItem(0, 0, QTableWidgetItem(mensaje))
        self.tabla_asignadas.item(0, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabla_asignadas.setSpan(0, 0, 1, 6)

    def mostrar_error(self, titulo, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(CLOUD_STYLE)
        msg.exec()