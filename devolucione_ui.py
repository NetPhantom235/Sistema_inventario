from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QComboBox, QFrame, QLineEdit, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from db_manager import DatabaseManager

CLOUD_STYLE = """
QWidget {
    background: #1a1a1a;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 15px;
}

QTableWidget {
    background: #262626;
    gridline-color: #505050;
    border-radius: 6px;
    color: #ffffff;
    font-size: 15px;
    border: 1px solid #505050;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #ffffff;
    padding: 12px;
    border: none;
    font-weight: bold;
    font-size: 16px;
}

QTableWidget::item {
    border-bottom: 1px solid #505050;
    padding: 10px;
}

QTableWidget::item:selected {
    background-color: #0078D4;
    color: #ffffff;
}

QPushButton {
    background-color: #0078d7;
    color: #ffffff;
    border: none;
    padding: 12px 20px;
    border-radius: 6px;
    font-size: 15px;
    font-weight: bold;
    transition: background-color 0.3s ease;
}

QPushButton:hover {
    background-color: #0091ff;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QComboBox {
    background-color: #262626;
    color: #ffffff;
    border: 1px solid #505050;
    padding: 8px;
    border-radius: 6px;
    font-size: 15px;
    min-height: 25px;
}
"""

class DevolucionesUI(QWidget):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.setStyleSheet(CLOUD_STYLE)
        self.db = db
        self.init_ui()
        self.cargar_datos()
        self.setup_auto_refresh()

    def setup_auto_refresh(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.cargar_datos)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with status dashboard
        header = QFrame()
        header.setStyleSheet('background-color: #2D2D2D; border-radius: 10px; padding: 15px;')
        header_layout = QHBoxLayout(header)

        # Status metrics
        metrics_layout = QHBoxLayout()
        self.total_returns = self.create_metric_widget('Total Returns', '0', '📦')
        self.pending_returns = self.create_metric_widget('Pending', '0', '⏳')
        self.completed_returns = self.create_metric_widget('Completed Today', '0', '✅')
        
        for metric in [self.total_returns, self.pending_returns, self.completed_returns]:
            metrics_layout.addWidget(metric)

        header_layout.addLayout(metrics_layout)
        layout.addWidget(header)

        # Action toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet('background-color: #2D2D2D; border-radius: 10px; padding: 15px;')
        toolbar_layout = QHBoxLayout(toolbar)

        # Search and filters
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search devices...')
        self.search_input.textChanged.connect(self.filter_devices)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #3D3D3D;
                border: 1px solid #505050;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
                min-width: 250px;
            }
        """)

        self.status_filter = QComboBox()
        self.status_filter.addItems(['All Status', 'Pending', 'In Progress', 'Completed'])
        self.status_filter.currentTextChanged.connect(self.filter_devices)
        self.status_filter.setStyleSheet("""
            QComboBox {
                background: #3D3D3D;
                border: 1px solid #505050;
                border-radius: 5px;
                padding: 8px;
                color: white;
                min-width: 150px;
            }
        """)

        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addStretch()

        # Action buttons
        self.btn_procesar = self.create_action_button('Process Return', '✔️')
        self.btn_historial = self.create_action_button('View History', '📋')
        self.btn_reporte = self.create_action_button('Generate Report', '📊')
        
        for btn in [self.btn_procesar, self.btn_historial, self.btn_reporte]:
            toolbar_layout.addWidget(btn)

        layout.addWidget(toolbar)

        # Main content area
        content = QFrame()
        content.setStyleSheet('background-color: #2D2D2D; border-radius: 10px; padding: 15px;')
        content_layout = QHBoxLayout(content)

        # Returns management section
        returns_section = QVBoxLayout()

        # Available devices table
        available_label = QLabel('Available Devices')
        available_label.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
        returns_section.addWidget(available_label)

        self.tabla_disponibles = self.create_table(['ID', 'Device', 'Location', 'Last Used'])
        returns_section.addWidget(self.tabla_disponibles)

        # Assigned devices table
        assigned_label = QLabel('Devices to Return')
        assigned_label.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
        returns_section.addWidget(assigned_label)

        self.tabla_asignadas = self.create_table(['ID', 'Device', 'Supervisor', 'Assignment Date', 'Status'])
        returns_section.addWidget(self.tabla_asignadas)

        content_layout.addLayout(returns_section)

        # Action panel
        action_panel = QVBoxLayout()
        action_panel.setSpacing(10)

        # QR Scanner section
        scanner_frame = QFrame()
        scanner_frame.setStyleSheet('background-color: #333333; border-radius: 8px; padding: 15px;')
        scanner_layout = QVBoxLayout(scanner_frame)

        scanner_title = QLabel('Device Scanner')
        scanner_title.setStyleSheet('color: white; font-size: 14px; font-weight: bold;')
        scanner_layout.addWidget(scanner_title)

        btn_scan = QPushButton('Scan QR Code')
        btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        btn_scan.clicked.connect(self.handle_scan)
        scanner_layout.addWidget(btn_scan)

        action_panel.addWidget(scanner_frame)

        # Supervisor selection
        supervisor_frame = QFrame()
        supervisor_frame.setStyleSheet('background-color: #333333; border-radius: 8px; padding: 15px;')
        supervisor_layout = QVBoxLayout(supervisor_frame)

        supervisor_title = QLabel('Return Authorization')
        supervisor_title.setStyleSheet('color: white; font-size: 14px; font-weight: bold;')
        supervisor_layout.addWidget(supervisor_title)

        self.combo_supervisores = QComboBox()
        self.combo_supervisores.setStyleSheet("""
            QComboBox {
                background: #3D3D3D;
                border: 1px solid #505050;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
        """)
        supervisor_layout.addWidget(self.combo_supervisores)

        action_panel.addWidget(supervisor_frame)

        # Transfer buttons
        transfer_frame = QFrame()
        transfer_frame.setStyleSheet('background-color: #333333; border-radius: 8px; padding: 15px;')
        transfer_layout = QVBoxLayout(transfer_frame)

        btn_asignar = QPushButton('→ Process Return')
        btn_liberar = QPushButton('← Cancel Return')
        
        for btn in [btn_asignar, btn_liberar]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 5px 0;
                }
                QPushButton:hover {
                    background-color: #106EBE;
                }
            """)

        btn_asignar.clicked.connect(lambda: self.move_item(self.tabla_disponibles, self.tabla_asignadas))
        btn_liberar.clicked.connect(lambda: self.move_item(self.tabla_asignadas, self.tabla_disponibles))

        transfer_layout.addWidget(btn_asignar)
        transfer_layout.addWidget(btn_liberar)

        action_panel.addWidget(transfer_frame)
        action_panel.addStretch()

        content_layout.addLayout(action_panel)
        layout.addWidget(content)

        # Status bar
        status_bar = QFrame()
        status_bar.setStyleSheet('background-color: #2D2D2D; border-radius: 5px; padding: 10px;')
        status_layout = QHBoxLayout(status_bar)

        self.status_label = QLabel('System Ready')
        self.status_label.setStyleSheet('color: white;')
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #3D3D3D;
                border: none;
                border-radius: 3px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background: #0078D4;
                border-radius: 3px;
            }
        """)
        self.progress_bar.hide()

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)

        layout.addWidget(status_bar)
        self.setLayout(layout)

    def create_action_button(self, text, icon):
        btn = QPushButton(f'{icon} {text}')
        btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        return btn

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

    def create_metric_widget(self, title, value, icon):
        metric_frame = QFrame()
        metric_frame.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: white;
            }
        """)
        
        metric_layout = QVBoxLayout(metric_frame)
        metric_layout.setSpacing(8)
        
        # Header with title and icon
        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet('font-size: 14px; color: #B0B0B0;')
        icon_label = QLabel(icon)
        icon_label.setStyleSheet('font-size: 20px;')
        
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(icon_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet('font-size: 24px; font-weight: bold;')
        
        metric_layout.addLayout(header)
        metric_layout.addWidget(value_label)
        
        return metric_frame

    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                background: #2c2c2c;
                border: none;
                border-radius: 8px;
                color: white;
            }
            QHeaderView::section {
                background-color: #333333;
                padding: 8px;
                border: none;
                color: white;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
        """)
        return table

    def filter_devices(self):
        search_text = self.search_input.text().lower()
        status = self.status_filter.currentText()
        
        for row in range(self.tabla_disponibles.rowCount()):
            device = self.tabla_disponibles.item(row, 1).text().lower()
            should_show = search_text in device
            self.tabla_disponibles.setRowHidden(row, not should_show)
        
        for row in range(self.tabla_asignadas.rowCount()):
            device = self.tabla_asignadas.item(row, 1).text().lower()
            device_status = self.tabla_asignadas.item(row, 4).text() if self.tabla_asignadas.item(row, 4) else ''
            should_show = search_text in device and (status == 'All Status' or status == device_status)
            self.tabla_asignadas.setRowHidden(row, not should_show)