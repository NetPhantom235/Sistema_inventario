from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QComboBox, QLineEdit, QLabel, QInputDialog, QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QLinearGradient, QBrush, QImage, QPixmap
from db_manager import DatabaseManager
import cv2
from pyzbar.pyzbar import decode

# Azure/AWS hybrid styling
CLOUD_BLUE = '#0078D4'
AWS_ORANGE = '#FF9900'
CLOUD_GRAY = '#2F2F2F'
BACKGROUND_GRADIENT = QLinearGradient(0, 0, 0, 400)
BACKGROUND_GRADIENT.setColorAt(0, QColor('#1B1B1B'))
BACKGROUND_GRADIENT.setColorAt(1, QColor('#3D3D3D'))

from design_system import CLOUD_THEME, CLOUD_STYLE, APP_FONT

class PrestamosUI(QWidget):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.setStyleSheet(CLOUD_STYLE)
        self.setFont(APP_FONT)
        self.db = db
        self.init_ui()
        self.cargar_datos()

    def mostrar_estado_vacio(self, mensaje):
        self.tabla.setRowCount(1)
        self.tabla.setItem(0, 0, QTableWidgetItem(mensaje))
        self.tabla.item(0, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabla.setSpan(0, 0, 1, 7)

    def mostrar_error(self, titulo, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(CLOUD_STYLE)
        msg.exec()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Supervisor selection and metadata
        top_controls = QHBoxLayout()
        self.combo_supervisores = QComboBox()
        self.txt_ubicacion = QLineEdit(placeholderText='Ubicación')
        self.txt_codigo_evento = QLineEdit(placeholderText='Código de Evento')
        top_controls.addWidget(QLabel('Supervisor:'))
        top_controls.addWidget(self.combo_supervisores)
        top_controls.addWidget(self.txt_ubicacion)
        top_controls.addWidget(self.txt_codigo_evento)
        
        # Main list container
        list_container = QHBoxLayout()
        
        # Available machines list
        self.tabla_disponibles = QTableWidget()
        self.tabla_disponibles.setColumnCount(3)
        self.tabla_disponibles.setHorizontalHeaderLabels(['ID', 'Máquina', 'Ubicación'])
        self.tabla_disponibles.horizontalHeader().setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {CLOUD_THEME['colors']['primary']};
                color: {CLOUD_THEME['colors']['text']['primary']};
                font-size: {CLOUD_THEME['typography']['font_sizes']['body']}px;
                padding: {CLOUD_THEME['spacing']['unit'] * 2}px;
                border-bottom: 2px solid {CLOUD_THEME['colors']['secondary']};
            }}
        """)
        self.tabla_disponibles.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Assigned machines list
        self.tabla_asignadas = QTableWidget()
        self.tabla_asignadas.setColumnCount(4)
        self.tabla_asignadas.setHorizontalHeaderLabels(['ID', 'Máquina', 'Supervisor', 'Ubicación'])
        self.tabla_asignadas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Action buttons
        btn_scan = QPushButton('Escanear QR/CODIGO')
        btn_asignar = QPushButton('→ Asignar')
        btn_liberar = QPushButton('← Liberar')
        
        # Button layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(btn_scan)
        button_layout.addWidget(btn_asignar)
        button_layout.addWidget(btn_liberar)
        
        # Add components to layout
        list_container.addWidget(self.tabla_disponibles)
        list_container.addLayout(button_layout)
        list_container.addWidget(self.tabla_asignadas)
        
        # Add all sections to main layout
        layout.addLayout(top_controls)
        layout.addLayout(list_container)
        self.setLayout(layout)
        
        # Connect signals
        btn_scan.clicked.connect(self.handle_scan)
        btn_asignar.clicked.connect(lambda: self.move_item(self.tabla_disponibles, self.tabla_asignadas))
        btn_liberar.clicked.connect(lambda: self.move_item(self.tabla_asignadas, self.tabla_disponibles))

    def handle_scan(self):
        cap = cv2.VideoCapture(0)
        detected = False
        
        while not detected:
            ret, frame = cap.read()
            if not ret:
                self.mostrar_error("Error de cámara", "No se pudo acceder a la cámara")
                break
            
            # Convertir frame a RGB para PyQt
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # Detección de códigos
            codes = decode(frame)
            for code in codes:
                (x, y, w, h) = code.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                machine_id = code.data.decode('utf-8')
                detected = True
                
                # Buscar y mover el item correspondiente
                for row in range(self.tabla_disponibles.rowCount()):
                    if self.tabla_disponibles.item(row, 0).text() == machine_id:
                        self.move_item(self.tabla_disponibles, self.tabla_asignadas, row)
                        break
                break
            
            # Mostrar vista previa estilo AWS/Azure
            preview = QLabel()
            preview.setPixmap(pixmap.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio))
            preview.setStyleSheet("""
                QLabel {
                    border: 2px solid #0078D4;
                    border-radius: 8px;
                    margin: 16px;
                }
            """)
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Escaneo en tiempo real")
            dialog.setLayout(QVBoxLayout())
            dialog.layout().addWidget(preview)
            QTimer.singleShot(100, dialog.show)
            
        cap.release()
        
        if not detected:
            # Fallback a entrada manual
            machine_id, ok = QInputDialog.getText(self, 'Escaneo manual', 'Ingrese ID escaneado:')
            if ok and machine_id:
                for row in range(self.tabla_disponibles.rowCount()):
                    if self.tabla_disponibles.item(row, 0).text() == machine_id:
                        self.move_item(self.tabla_disponibles, self.tabla_asignadas, row)
                        break

    def move_item(self, source, destination, row=None):
        selected = source.currentRow() if row is None else row
        if selected >= 0:
            row_data = [source.item(selected, col).text() for col in range(source.columnCount())]
            
            # Add supervisor and location data
            row_data.append(self.combo_supervisores.currentText())
            row_data.append(self.txt_ubicacion.text())
            
            destination.insertRow(destination.rowCount())
            for col, data in enumerate(row_data):
                destination.setItem(destination.rowCount()-1, col, QTableWidgetItem(data))
            source.removeRow(selected)
            self.actualizar_asignacion_bd(row_data[0])

    def actualizar_asignacion_bd(self, machine_id):
        supervisor_id = self.combo_supervisores.currentData()
        ubicacion = self.txt_ubicacion.text()
        codigo_evento = self.txt_codigo_evento.text()
        
        if supervisor_id and ubicacion:
            self.db.asignar_maquina(machine_id, supervisor_id, ubicacion, codigo_evento)

    def cargar_datos(self):
        try:
            # Load available machines
            disponibles = self.db.obtener_maquinas_disponibles()
            self.tabla_disponibles.setRowCount(len(disponibles))
            for i, maq in enumerate(disponibles):
                self.tabla_disponibles.setItem(i, 0, QTableWidgetItem(maq['id']))
                self.tabla_disponibles.setItem(i, 1, QTableWidgetItem(maq['nombre']))
                self.tabla_disponibles.setItem(i, 2, QTableWidgetItem(maq['ubicacion']))

            # Load supervisors
            self.combo_supervisores.clear()
            supervisores = self.db.obtener_supervisores()
            for sup in supervisores:
                self.combo_supervisores.addItem(f"{sup['nombre']} ({sup['id']})", sup['id'])

        except Exception as e:
            self.mostrar_error("Error de carga", f"Error al cargar datos: {str(e)}")

    def cargar_datos(self):
        try:
            prestamos = self.db.obtener_prestamos()
            self.tabla.setRowCount(0)
            
            if not prestamos:
                self.mostrar_estado_vacio("No hay préstamos registrados")
                return

            self.tabla.setRowCount(len(prestamos))
            for i, prestamo in enumerate(prestamos):
                self.agregar_fila_tabla(i, prestamo)
                
            self.aplicar_estilos_filas()
            self.tabla.sortByColumn(3, Qt.SortOrder.DescendingOrder)
            
        except Exception as e:
            self.mostrar_error("Error de datos", f"No se pudieron cargar los préstamos: {str(e)}")

    def agregar_fila_tabla(self, row, prestamo):
        self.tabla.insertRow(row)
        self.tabla.setItem(row, 0, QTableWidgetItem(prestamo['id']))
        self.tabla.setItem(row, 1, QTableWidgetItem(prestamo['maquina_nombre']))
        self.tabla.setItem(row, 2, QTableWidgetItem(prestamo['supervisor_nombre']))
        self.tabla.setItem(row, 3, QTableWidgetItem(str(prestamo['fecha_prestamo'])))
        
        estado_item = QTableWidgetItem('Devuelto' if prestamo['fecha_devolucion'] else 'Activo')
        estado_item.setBackground(QColor('#008a00' if prestamo['fecha_devolucion'] else '#d13438'))
        estado_item.setForeground(QColor('#ffffff'))
        
        self.tabla.setItem(row, 4, QTableWidgetItem(
            str(prestamo['fecha_devolucion']) if prestamo['fecha_devolucion'] else 'Pendiente'))
        self.tabla.setItem(row, 5, estado_item)
        self.tabla.setItem(row, 6, QTableWidgetItem(prestamo['observaciones']))

    def aplicar_estilos_filas(self):
        for row in range(self.tabla.rowCount()):
            if self.tabla.item(row, 5).text() == 'Activo':
                for col in range(self.tabla.columnCount()):
                    self.tabla.item(row, col).setBackground(QColor('#fff4ce'))