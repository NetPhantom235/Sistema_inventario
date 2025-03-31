from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QLinearGradient, QBrush

from db_manager import DatabaseManager

# Azure/AWS design system colors
CLOUD_BLUE = '#0078D4'
AWS_ORANGE = '#FF9900'
CLOUD_GRAY = '#2F2F2F'
BACKGROUND_GRADIENT = QLinearGradient(0, 0, 0, 400)
BACKGROUND_GRADIENT.setColorAt(0, QColor('#1B1B1B'))
BACKGROUND_GRADIENT.setColorAt(1, QColor('#3D3D3D'))

from design_system import CLOUD_THEME, CLOUD_STYLE, APP_FONT

GRADIENT_BG = QLinearGradient(0, 0, 0, 400)
GRADIENT_BG.setColorAt(0, QColor(CLOUD_THEME['colors']['background']))
GRADIENT_BG.setColorAt(1, QColor(CLOUD_THEME['colors']['surface']))

class SupervisoresUI(QWidget):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.setStyleSheet(CLOUD_STYLE)
        self.db = db
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        self.btn_nuevo = QPushButton("Nuevo Supervisor")
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_historial = QPushButton("Historial Préstamos")
        for btn in [self.btn_nuevo, self.btn_editar, self.btn_eliminar, self.btn_historial]:
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
        btn_layout.addWidget(self.btn_historial)
        
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(['ID', 'Nombre', 'Email', 'Teléfono', 'Permiso', 'Fecha Registro'])
        self.tabla.horizontalHeader().setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {CLOUD_THEME['colors']['primary']};
                color: {CLOUD_THEME['colors']['text']['primary']};
                font-size: {CLOUD_THEME['typography']['font_sizes']['body']}px;
                padding: {CLOUD_THEME['spacing']['unit'] * 2}px;
                border-bottom: 2px solid {CLOUD_THEME['colors']['secondary']};
            }}
        """)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.tabla)
        self.setLayout(layout)

    def cargar_datos(self):
        try:
            supervisores = self.db.obtener_supervisores()
            self.tabla.setRowCount(0)
            
            if not supervisores:
                self.mostrar_estado_vacio("No hay supervisores registrados")
                return

            self.tabla.setRowCount(len(supervisores))
            for i, supervisor in enumerate(supervisores):
                self.tabla.setItem(i, 0, QTableWidgetItem(supervisor.get('id', 'N/A')))
                self.tabla.setItem(i, 1, QTableWidgetItem(supervisor.get('nombre', 'N/A')))
                self.tabla.setItem(i, 2, QTableWidgetItem(supervisor['email']))
                self.tabla.setItem(i, 3, QTableWidgetItem(supervisor['telefono']))
                self.tabla.setItem(i, 4, QTableWidgetItem(supervisor['permiso']))
                self.tabla.setItem(i, 5, QTableWidgetItem(str(supervisor['fecha_registro'])))
            
            self.tabla.sortByColumn(5, Qt.SortOrder.DescendingOrder)
            
        except Exception as e:
            self.mostrar_error("Error de carga", f"No se pudieron obtener los supervisores: {str(e)}")

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
