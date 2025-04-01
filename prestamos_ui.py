from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QComboBox, QLineEdit, QLabel, QInputDialog, QDialog, QProgressBar, QFrame, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QLinearGradient, QBrush, QImage, QPixmap, QIcon
from db_manager import DatabaseManager
import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
import uuid

# Enterprise Cloud Theme
CLOUD_BLUE = '#0078D4'
AWS_ORANGE = '#FF9900'
GCP_RED = '#EA4335'
AZURE_BLUE = '#008AD7'
CLOUD_GRAY = '#2F2F2F'
BACKGROUND_GRADIENT = QLinearGradient(0, 0, 0, 400)
BACKGROUND_GRADIENT.setColorAt(0, QColor('#1B1B1B'))
BACKGROUND_GRADIENT.setColorAt(1, QColor('#3D3D3D'))

from design_system import CLOUD_THEME, CLOUD_STYLE, APP_FONT

class EnterpriseTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #2c2c2c;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QTableWidget::item:selected {
                background-color: #0078D4;
                color: #ffffff;
            }
        """)
        self.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #333333;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #404040;
                font-weight: bold;
                color: #ffffff;
            }
        """)
        self.verticalHeader().hide()
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)

class CloudButton(QPushButton):
    def __init__(self, text, icon_path=None, primary=False):
        super().__init__(text)
        if icon_path:
            self.setIcon(QIcon(icon_path))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#0078D4' if primary else '#2c2c2c'};
                color: #ffffff;
                border: {'none' if primary else '1px solid #404040'};
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {'#106EBE' if primary else '#3c3c3c'};
            }}
            QPushButton:pressed {{
                background-color: {'#005A9E' if primary else '#1c1c1c'};
            }}
        """)

class PrestamosUI(QWidget):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.setStyleSheet(CLOUD_STYLE)
        self.setFont(APP_FONT)
        self.db = db
        self.init_ui()
        self.cargar_datos()
        self.setup_auto_refresh()

    def setup_auto_refresh(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.cargar_datos)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Header with metadata
        header = QFrame()
        header.setStyleSheet("background-color: #333333; border-radius: 4px; padding: 16px; color: #ffffff;")
        header_layout = QHBoxLayout(header)
        
        # Supervisor selection
        supervisor_widget = QFrame()
        supervisor_layout = QVBoxLayout(supervisor_widget)
        supervisor_layout.addWidget(QLabel('Supervisor:'))
        self.combo_supervisores = QComboBox()
        self.combo_supervisores.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                background: white;
            }
        """)
        supervisor_layout.addWidget(self.combo_supervisores)
        
        # Location and event code
        metadata_widget = QFrame()
        metadata_layout = QVBoxLayout(metadata_widget)
        self.txt_ubicacion = QLineEdit()
        self.txt_ubicacion.setPlaceholderText('Ubicación')
        self.txt_codigo_evento = QLineEdit()
        self.txt_codigo_evento.setPlaceholderText('Código de Evento')
        metadata_layout.addWidget(QLabel('Ubicación:'))
        metadata_layout.addWidget(self.txt_ubicacion)
        metadata_layout.addWidget(QLabel('Código de Evento:'))
        metadata_layout.addWidget(self.txt_codigo_evento)
        
        header_layout.addWidget(supervisor_widget)
        header_layout.addWidget(metadata_widget)
        header_layout.addStretch()
        
        main_layout.addWidget(header)
        
        # Tables container
        tables_container = QHBoxLayout()
        
        # Available machines
        available_frame = QFrame()
        available_layout = QVBoxLayout(available_frame)
        available_layout.addWidget(QLabel('Máquinas Disponibles'))
        self.tabla_disponibles = EnterpriseTableWidget()
        self.tabla_disponibles.setColumnCount(4)
        self.tabla_disponibles.setHorizontalHeaderLabels(['ID', 'Máquina', 'Categoría', 'Ubicación'])
        available_layout.addWidget(self.tabla_disponibles)
        
        # Control buttons
        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(buttons_frame)
        btn_scan = CloudButton('Escanear QR/Código', primary=True)
        btn_asignar = CloudButton('→ Asignar')
        btn_liberar = CloudButton('← Liberar')
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_scan)
        buttons_layout.addWidget(btn_asignar)
        buttons_layout.addWidget(btn_liberar)
        buttons_layout.addStretch()
        
        # Assigned machines
        assigned_frame = QFrame()
        assigned_layout = QVBoxLayout(assigned_frame)
        assigned_layout.addWidget(QLabel('Máquinas Asignadas'))
        self.tabla_asignadas = EnterpriseTableWidget()
        self.tabla_asignadas.setColumnCount(5)
        self.tabla_asignadas.setHorizontalHeaderLabels(['ID', 'Máquina', 'Supervisor', 'Ubicación', 'Tiempo'])
        assigned_layout.addWidget(self.tabla_asignadas)
        
        tables_container.addWidget(available_frame)
        tables_container.addWidget(buttons_frame)
        tables_container.addWidget(assigned_frame)
        
        main_layout.addLayout(tables_container)
        
        # Status bar
        status_bar = QFrame()
        status_bar.setStyleSheet("background-color: #333333; border-radius: 4px; padding: 8px; color: #ffffff;")
        status_layout = QHBoxLayout(status_bar)
        self.status_label = QLabel('Sistema listo')
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        main_layout.addWidget(status_bar)
        
        self.setLayout(main_layout)
        
        # Connect signals
        btn_scan.clicked.connect(self.handle_scan)
        btn_asignar.clicked.connect(self.handle_asignar)
        btn_liberar.clicked.connect(self.handle_liberar)

    def handle_asignar(self):
        selected_row = self.tabla_disponibles.currentRow()
        if selected_row >= 0:
            if not self.combo_supervisores.currentText():
                self.mostrar_error("Error", "Debe seleccionar un supervisor")
                return
            if not self.txt_ubicacion.text():
                self.mostrar_error("Error", "Debe especificar una ubicación")
                return
            
            self.move_item(self.tabla_disponibles, self.tabla_asignadas)
            self.status_label.setText('Máquina asignada exitosamente')

    def handle_liberar(self):
        selected_row = self.tabla_asignadas.currentRow()
        if selected_row >= 0:
            self.move_item(self.tabla_asignadas, self.tabla_disponibles)
            self.status_label.setText('Máquina liberada exitosamente')

    def handle_scan(self):
        self.status_label.setText('Iniciando escaneo...')
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise Exception("No se pudo acceder a la cámara")
            
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("Escáner QR/Código de Barras")
            preview_layout = QVBoxLayout(preview_dialog)
            preview_label = QLabel()
            preview_layout.addWidget(preview_label)
            preview_dialog.show()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Update preview
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
                preview_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                    640, 480, Qt.AspectRatioMode.KeepAspectRatio))
                
                # Detect codes
                codes = decode(frame)
                if codes:
                    code_data = codes[0].data.decode('utf-8')
                    cap.release()
                    preview_dialog.close()
                    
                    # Find and move the device
                    found = False
                    for row in range(self.tabla_disponibles.rowCount()):
                        if self.tabla_disponibles.item(row, 0).text() == code_data:
                            self.tabla_disponibles.selectRow(row)
                            if self.combo_supervisores.currentText() and self.txt_ubicacion.text():
                                self.handle_asignar()
                                found = True
                                self.status_label.setText(f'Dispositivo {code_data} asignado exitosamente')
                            else:
                                self.mostrar_error("Datos Requeridos", "Por favor seleccione un supervisor y especifique una ubicación")
                            break
                    
                    if not found:
                        self.mostrar_error("Error", f"Dispositivo {code_data} no encontrado o no disponible")
                    break
                
                QApplication.processEvents()
                
        except Exception as e:
            self.mostrar_error("Error de Escaneo", str(e))
        finally:
            if 'cap' in locals() and cap.isOpened():
                cap.release()
            self.progress_bar.hide()
            self.status_label.setText('Sistema listo')

    def process_scanned_code(self, code_data):
        # Find and select the machine in available table
        for row in range(self.tabla_disponibles.rowCount()):
            if self.tabla_disponibles.item(row, 0).text() == code_data:
                self.tabla_disponibles.selectRow(row)
                self.handle_asignar()
                return
        
        self.mostrar_error("Error", "Máquina no encontrada o no disponible")

    def move_item(self, source, destination):
        selected_row = source.currentRow()
        if selected_row >= 0:
            machine_id = source.item(selected_row, 0).text()
            machine_name = source.item(selected_row, 1).text()
            
            if destination == self.tabla_asignadas:
                # Moving to assigned
                prestamo_id = str(uuid.uuid4())
                prestamo_data = {
                    'id': prestamo_id,
                    'maquina_id': machine_id,
                    'supervisor_id': self.combo_supervisores.currentData(),
                    'observaciones': f"Ubicación: {self.txt_ubicacion.text()}, Evento: {self.txt_codigo_evento.text()}"
                }
                
                if self.db.crear_prestamo(prestamo_data):
                    row_position = destination.rowCount()
                    destination.insertRow(row_position)
                    destination.setItem(row_position, 0, QTableWidgetItem(machine_id))
                    destination.setItem(row_position, 1, QTableWidgetItem(machine_name))
                    destination.setItem(row_position, 2, QTableWidgetItem(self.combo_supervisores.currentText()))
                    destination.setItem(row_position, 3, QTableWidgetItem(self.txt_ubicacion.text()))
                    destination.setItem(row_position, 4, QTableWidgetItem(datetime.now().strftime('%Y-%m-%d %H:%M')))
                    source.removeRow(selected_row)
            else:
                # Moving to available
                prestamos = self.db.obtener_prestamos({'maquina_id': machine_id})
                if prestamos:
                    prestamo_id = prestamos[0]['id']
                    if self.db.finalizar_prestamo(prestamo_id):
                        row_position = destination.rowCount()
                        destination.insertRow(row_position)
                        destination.setItem(row_position, 0, QTableWidgetItem(machine_id))
                        destination.setItem(row_position, 1, QTableWidgetItem(machine_name))
                        destination.setItem(row_position, 2, QTableWidgetItem(''))
                        destination.setItem(row_position, 3, QTableWidgetItem(self.txt_ubicacion.text()))
                        source.removeRow(selected_row)

    def cargar_datos(self):
        try:
            # Load available machines
            disponibles = self.db.obtener_maquinas_disponibles()
            self.tabla_disponibles.setRowCount(len(disponibles))
            for i, maq in enumerate(disponibles):
                self.tabla_disponibles.setItem(i, 0, QTableWidgetItem(maq['id']))
                self.tabla_disponibles.setItem(i, 1, QTableWidgetItem(maq['nombre']))
                self.tabla_disponibles.setItem(i, 2, QTableWidgetItem(maq['categoria']))
                self.tabla_disponibles.setItem(i, 3, QTableWidgetItem(maq.get('ubicacion', '')))

            # Load active loans
            prestamos = self.db.obtener_prestamos({'fecha_devolucion': None})
            self.tabla_asignadas.setRowCount(len(prestamos))
            for i, prestamo in enumerate(prestamos):
                self.tabla_asignadas.setItem(i, 0, QTableWidgetItem(prestamo['maquina_id']))
                self.tabla_asignadas.setItem(i, 1, QTableWidgetItem(prestamo['maquina_nombre']))
                self.tabla_asignadas.setItem(i, 2, QTableWidgetItem(prestamo['supervisor_nombre']))
                self.tabla_asignadas.setItem(i, 3, QTableWidgetItem(prestamo.get('ubicacion', '')))
                loan_time = datetime.now() - prestamo['fecha_prestamo']
                self.tabla_asignadas.setItem(i, 4, QTableWidgetItem(f"{loan_time.days}d {loan_time.seconds//3600}h"))

            # Load supervisors
            self.combo_supervisores.clear()
            supervisores = self.db.obtener_supervisores()
            for sup in supervisores:
                self.combo_supervisores.addItem(f"{sup['nombre']} ({sup['id']})", sup['id'])

            self.status_label.setText('Datos actualizados: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
        except Exception as e:
            self.mostrar_error("Error de carga", f"Error al cargar datos: {str(e)}")

    def mostrar_error(self, titulo, mensaje):
        QMessageBox.critical(self, titulo, mensaje)