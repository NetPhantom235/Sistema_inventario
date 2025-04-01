from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QApplication, QVBoxLayout, QWidget, QLabel,
    QStackedWidget, QFrame, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter, QLinearGradient
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer
from design_system import CLOUD_THEME, CLOUD_STYLE, APP_FONT
from dashboard_cloud import DashboardCloud
from maquinas_ui import MaquinasUI
from supervisores_ui import SupervisoresUI
from prestamos_ui import PrestamosUI
from devolucione_ui import DevolucionesUI
from db_manager import DatabaseManager
import sys

class EnterpriseNavButton(QPushButton):
    def __init__(self, text, icon_path=None):
        super().__init__(text)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CLOUD_THEME['colors']['text']['secondary']};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                text-align: left;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {CLOUD_THEME['colors']['hover']};
                color: {CLOUD_THEME['colors']['text']['primary']};
            }}
            QPushButton:checked {{
                background-color: {CLOUD_THEME['colors']['primary']};
                color: white;
            }}
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        self.setWindowTitle('Enterprise Cloud Management System')
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet(CLOUD_STYLE)
        self.setFont(APP_FONT)

        # Main container
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar navigation
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {CLOUD_THEME['colors']['surface']};
                border-right: 1px solid {CLOUD_THEME['colors']['border']};
            }}
        """)
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(8)

        # Logo and branding
        brand_container = QFrame()
        brand_layout = QHBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 0, 0, 24)

        logo_label = QLabel('🚀')
        logo_label.setStyleSheet('font-size: 32px;')
        title_label = QLabel('CloudSys')
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {CLOUD_THEME['colors']['text']['primary']};
        """)

        brand_layout.addWidget(logo_label)
        brand_layout.addWidget(title_label)
        brand_layout.addStretch()

        sidebar_layout.addWidget(brand_container)

        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ('Dashboard', '📊', DashboardCloud),
            ('Devices', '💻', MaquinasUI),
            ('Supervisors', '👥', SupervisoresUI),
            ('Loans', '📋', PrestamosUI),
            ('Returns', '↩️', DevolucionesUI)
        ]

        for text, icon, _ in nav_items:
            btn = EnterpriseNavButton(f'{icon} {text}')
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # System status
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CLOUD_THEME['colors']['card']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        status_layout = QVBoxLayout(status_frame)

        status_label = QLabel('System Status')
        status_label.setStyleSheet(f'color: {CLOUD_THEME["colors"]["text"]["primary"]};')
        status_value = QLabel('🟢 Operational')
        status_value.setStyleSheet(f'color: {CLOUD_THEME["colors"]["success"]};')

        status_layout.addWidget(status_label)
        status_layout.addWidget(status_value)

        sidebar_layout.addWidget(status_frame)

        # Content area
        content_container = QFrame()
        content_container.setStyleSheet(f'background-color: {CLOUD_THEME["colors"]["background"]};')
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(24, 24, 24, 24)

        # Stacked widget for content
        self.stack = QStackedWidget()
        for i, (_, _, widget_class) in enumerate(nav_items):
            widget = widget_class(self.db)
            self.stack.addWidget(widget)
            self.nav_buttons[i].clicked.connect(lambda checked, idx=i: self.stack.setCurrentIndex(idx))

        content_layout.addWidget(self.stack)

        # Add sidebar and content to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_container)

        self.setCentralWidget(main_widget)
        
        # Set initial active tab
        self.nav_buttons[0].setChecked(True)

    def setup_animations(self):
        self.stack.setStyleSheet('QStackedWidget { transition: all 0.3s ease-in-out; }')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


