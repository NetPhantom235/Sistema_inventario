from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QLinearGradient, QBrush

# Azure/AWS inspired color palette
CLOUD_BLUE = '#0078D4'
AWS_ORANGE = '#FF9900'
CLOUD_GRAY = '#2F2F2F'
BACKGROUND_GRADIENT = QLinearGradient(0, 0, 0, 400)
BACKGROUND_GRADIENT.setColorAt(0, QColor('#1B1B1B'))
BACKGROUND_GRADIENT.setColorAt(1, QColor('#3D3D3D'))

# Modern cloud-style QSS
CLOUD_STYLE = f"""
QWidget {{
    background: {CLOUD_GRAY};
    color: #FFFFFF;
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QPushButton {{
    background-color: {CLOUD_BLUE};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: #0062A3;
}}

QTableWidget {{
    background: {CLOUD_GRAY};
    gridline-color: #404040;
    border-radius: 4px;
}}

QHeaderView::section {{
    background-color: #333333;
    color: white;
    padding: 8px;
    border: none;
}}

QTableWidget::item {{
    border-bottom: 1px solid #404040;
    padding: 8px;
}}

QTableWidget::item:selected {{
    background-color: {CLOUD_BLUE};
}}
"""
from design_system import CLOUD_THEME
from db_manager import DatabaseManager
from nuevo_dispositivo_dialog import NuevoDispositivoDialog
from design_system import CLOUD_THEME

class MaquinasUI(QWidget):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        self.btn_nuevo = QPushButton("Nuevo dispositivo")
        self.btn_nuevo.clicked.connect(self.abrir_dialogo_nuevo)
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_generar_qr = QPushButton("Generar QR")
        for btn in [self.btn_nuevo, self.btn_editar, self.btn_eliminar, self.btn_generar_qr]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {CLOUD_THEME['colors']['primary']};
                    border-radius: {CLOUD_THEME['components']['button']['border_radius']};
                    padding: {CLOUD_THEME['components']['button']['padding']};
                    font-weight: {CLOUD_THEME['typography']['font_weights']['medium']};
                }}
                QPushButton:hover {{
                    background-color: {CLOUD_THEME['colors']['secondary']};
                    transform: {CLOUD_THEME['components']['button']['hover_effect']};
                }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(self.btn_nuevo)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_generar_qr)
        
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(['ID', 'Nombre', 'Categoría', 'Estado', 'ubicacion', 'supervisor'])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.tabla)
        self.setLayout(layout)

    def cargar_datos(self):
        try:
            maquinas = self.db.obtener_maquinas()
            self.tabla.setRowCount(0)
            
            if not maquinas:
                self.mostrar_estado_vacio("No hay máquinas registradas")
                return

            self.tabla.setRowCount(len(maquinas))
            for i, maquina in enumerate(maquinas):
                self.tabla.setItem(i, 0, QTableWidgetItem(maquina['id']))
                self.tabla.setItem(i, 1, QTableWidgetItem(maquina['nombre']))
                self.tabla.setItem(i, 2, QTableWidgetItem(maquina['categoria']))
                self.tabla.setItem(i, 3, QTableWidgetItem(maquina['estado']))
                self.tabla.setItem(i, 4, QTableWidgetItem(str(maquina['ultimo_mantenimiento'])))
                self.tabla.setItem(i, 5, QTableWidgetItem(maquina['supervisor_id']))
            
        except Exception as e:
            self.mostrar_error("Error de carga", f"No se pudieron obtener las máquinas: {str(e)}")

    def mostrar_estado_vacio(self, mensaje):
        self.tabla.setRowCount(1)
        self.tabla.setItem(0, 0, QTableWidgetItem(mensaje))
        self.tabla.item(0, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabla.setSpan(0, 0, 1, 6)

    def mostrar_error(self, titulo, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(CLOUD_STYLE)
        msg.exec()

    def abrir_dialogo_nuevo(self):
        dialog = NuevoDispositivoDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.db.insertar_maquina(
                data['id'],
                data['nombre'],
                data['categoria'],
                data['estado'],
                data['ubicacion'],
                data['supervisor_id']
            )
            self.cargar_datos()