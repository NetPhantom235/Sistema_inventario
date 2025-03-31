from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from design_system import CLOUD_THEME, CLOUD_STYLE, APP_FONT
from dashboard_cloud import DashboardCloud
from maquinas_ui import MaquinasUI
from supervisores_ui import SupervisoresUI
from prestamos_ui import PrestamosUI
from devolucione_ui import DevolucionesUI
from db_manager import DatabaseManager
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Sistema de Gestión de Máquinas')
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('icon.png'))  # Añadimos un ícono para la ventana

        # Aplicamos un tema oscuro estilizado con transiciones suaves
        self.setStyleSheet(CLOUD_STYLE)
        self.setFont(APP_FONT)

        # Creamos un contenedor principal
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        # Añadimos un encabezado personalizado con estilo moderno
        header = QLabel("Sistema de Gestión de Máquinas")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont(APP_FONT))
        header.setStyleSheet(f"""
            font-size: {CLOUD_THEME['typography']['font_sizes']['h1']}px;
            font-weight: {CLOUD_THEME['typography']['font_weights']['bold']};
            color: {CLOUD_THEME['colors']['primary']};
            margin-bottom: {CLOUD_THEME['spacing']['section_padding']};
        """)
        main_layout.addWidget(header)

        # Creamos las pestañas
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)  # Posición de las pestañas
        tabs.setMovable(True)  # Permitir mover las pestañas
        tabs.setDocumentMode(True)  # Estilo más limpio para las pestañas

        # Añadimos las pestañas
        tabs.addTab(MaquinasUI(self.db), "Máquinas")
        tabs.addTab(SupervisoresUI(self.db), "Supervisores")
        tabs.addTab(PrestamosUI(self.db), "Préstamos")
        tabs.addTab(DashboardCloud(self.db), "Dashboard")
        tabs.addTab(DevolucionesUI(self.db), "Devoluciones")

        main_layout.addWidget(tabs)
        self.setCentralWidget(main_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno de PyQt
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


