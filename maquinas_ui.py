from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QDialog, QLabel, QProgressBar, QLineEdit, QComboBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QColor, QIcon, QFont
from design_system import CLOUD_THEME
from db_manager import DatabaseManager
from nuevo_dispositivo_dialog import NuevoDispositivoDialog
from editar_dispositivo_dialog import EditarDispositivoDialog
import qrcode
from datetime import datetime
import csv
import os

class MaquinasUI(QWidget):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.init_ui()
        self.setup_auto_refresh()
        self.cargar_datos()

    def setup_auto_refresh(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.cargar_datos)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header section
        header = QFrame()
        header.setStyleSheet(f"background-color: {CLOUD_THEME['colors']['surface']}; border-radius: 10px; padding: 15px;")
        header_layout = QHBoxLayout(header)

        # Search and filters
        search_box = QFrame()
        search_layout = QHBoxLayout(search_box)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search devices...")
        self.search_input.textChanged.connect(self.filter_devices)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {CLOUD_THEME['colors']['card']};
                color: {CLOUD_THEME['colors']['text']['primary']};
                border: 1px solid {CLOUD_THEME['colors']['primary']};
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
        """)

        self.category_filter = QComboBox()
        self.status_filter = QComboBox()
        for combo in [self.category_filter, self.status_filter]:
            combo.setStyleSheet(f"""
                QComboBox {{
                    background: {CLOUD_THEME['colors']['card']};
                    color: {CLOUD_THEME['colors']['text']['primary']};
                    border: 1px solid {CLOUD_THEME['colors']['primary']};
                    border-radius: 5px;
                    padding: 8px;
                    min-width: 150px;
                }}
            """)

        self.category_filter.addItems(['All Categories', 'Hardware', 'Software', 'Network', 'Storage'])
        self.status_filter.addItems(['All Status', 'Available', 'In Use', 'Maintenance'])
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.category_filter)
        search_layout.addWidget(self.status_filter)

        # Action buttons
        actions = QFrame()
        actions_layout = QHBoxLayout(actions)
        self.btn_nuevo = QPushButton("Add Device")
        self.btn_editar = QPushButton("Edit")
        self.btn_eliminar = QPushButton("Delete")
        self.btn_export = QPushButton("Export")
        self.btn_generar_qr = QPushButton("Generate QR")

        for btn in [self.btn_nuevo, self.btn_editar, self.btn_eliminar, self.btn_export, self.btn_generar_qr]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {CLOUD_THEME['colors']['primary']};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {CLOUD_THEME['colors']['secondary']};
                }}
            """)
            actions_layout.addWidget(btn)

        header_layout.addWidget(search_box)
        header_layout.addWidget(actions)

        # Table
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(['ID', 'Name', 'Category', 'Status', 'Location', 'Last Updated', 'Actions'])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setStyleSheet(f"""
            QTableWidget {{
                background: {CLOUD_THEME['colors']['card']};
                border: none;
                border-radius: 10px;
                gridline-color: {CLOUD_THEME['colors']['surface']};
            }}
            QHeaderView::section {{
                background-color: {CLOUD_THEME['colors']['surface']};
                padding: 10px;
                border: none;
                font-weight: bold;
                color: {CLOUD_THEME['colors']['text']['primary']};
            }}
        """)

        # Status bar
        status_bar = QFrame()
        status_bar.setStyleSheet(f"background-color: {CLOUD_THEME['colors']['surface']}; border-radius: 5px; padding: 10px;")
        status_layout = QHBoxLayout(status_bar)
        self.status_label = QLabel('System Ready')
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {CLOUD_THEME['colors']['card']};
                border: none;
                border-radius: 3px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: {CLOUD_THEME['colors']['primary']};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.hide()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)

        # Connect signals
        self.btn_nuevo.clicked.connect(self.abrir_dialogo_nuevo)
        self.btn_editar.clicked.connect(self.abrir_dialogo_editar)
        self.btn_eliminar.clicked.connect(self.eliminar_dispositivo)
        self.btn_export.clicked.connect(self.export_inventory)
        self.btn_generar_qr.clicked.connect(self.generate_qr_code)
        self.category_filter.currentTextChanged.connect(self.filter_devices)
        self.status_filter.currentTextChanged.connect(self.filter_devices)

        # Add all components to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(self.tabla)
        main_layout.addWidget(status_bar)
        self.setLayout(main_layout)

    def generate_qr_code(self):
        selected_row = self.tabla.currentRow()
        if selected_row >= 0:
            device_id = self.tabla.item(selected_row, 0).text()
            device_name = self.tabla.item(selected_row, 1).text()
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(device_id)
            qr.make(fit=True)
            
            # Save QR code
            qr_filename = f'qr_code_{device_id}.png'
            qr.make_image(fill_color="black", back_color="white").save(qr_filename)
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle('QR Code Generated')
            msg.setText(f'QR Code for device {device_name} has been generated:\n{qr_filename}')
            msg.exec()
        else:
            self.mostrar_error("Selection Required", "Please select a device to generate QR code")

    def cargar_datos(self):
        try:
            self.status_label.setText('Loading data...')
            self.progress_bar.setRange(0, 0)
            self.progress_bar.show()
            
            maquinas = self.db.obtener_maquinas()
            self.tabla.setRowCount(0)
            
            if not maquinas:
                self.mostrar_estado_vacio("No devices registered")
                return

            self.tabla.setRowCount(len(maquinas))
            for i, maquina in enumerate(maquinas):
                self.tabla.setItem(i, 0, QTableWidgetItem(maquina['id']))
                self.tabla.setItem(i, 1, QTableWidgetItem(maquina['nombre']))
                self.tabla.setItem(i, 2, QTableWidgetItem(maquina['categoria']))
                
                # Enhanced status cell with color coding
                status_item = QTableWidgetItem(maquina['estado'])
                status_colors = {
                    'Available': QColor(CLOUD_THEME['colors']['success']),
                    'In Use': QColor(CLOUD_THEME['colors']['error']),
                    'Maintenance': QColor(CLOUD_THEME['colors']['warning'])
                }
                status_item.setBackground(status_colors.get(maquina['estado'], QColor(CLOUD_THEME['colors']['surface'])))
                self.tabla.setItem(i, 3, status_item)
                
                # Location
                self.tabla.setItem(i, 4, QTableWidgetItem(maquina.get('ubicacion', 'N/A')))
                
                # Enhanced supervisor info
                supervisor = self.db.obtener_supervisor_por_id(maquina['supervisor_id'])
                supervisor_text = f"{supervisor['nombre']} ({maquina['supervisor_id']})" if supervisor else 'Unassigned'
                self.tabla.setItem(i, 5, QTableWidgetItem(supervisor_text))
                
                # Last updated timestamp
                self.tabla.setItem(i, 6, QTableWidgetItem(maquina.get('ultima_actualizacion', 'N/A')))
            
            self.status_label.setText(f'Data updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            
        except Exception as e:
            self.mostrar_error("Loading Error", f"Could not load devices: {str(e)}")
        finally:
            self.progress_bar.hide()

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
        msg.setStyleSheet(f"background-color: {CLOUD_THEME['colors']['surface']}; color: {CLOUD_THEME['colors']['text']['primary']};")
        msg.exec()

    def filter_devices(self):
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        status = self.status_filter.currentText()
        
        for row in range(self.tabla.rowCount()):
            device_name = self.tabla.item(row, 1).text().lower()
            device_category = self.tabla.item(row, 2).text()
            device_status = self.tabla.item(row, 3).text()
            
            name_match = search_text in device_name
            category_match = category == 'All Categories' or category == device_category
            status_match = status == 'All Status' or status == device_status
            
            self.tabla.setRowHidden(row, not (name_match and category_match and status_match))

    def export_inventory(self):
        try:
            self.status_label.setText('Exporting inventory data...')
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            
            # Get all visible rows
            data = []
            headers = ['ID', 'Name', 'Category', 'Status', 'Location', 'Supervisor', 'Last Updated']
            data.append(headers)
            
            for row in range(self.tabla.rowCount()):
                if not self.tabla.isRowHidden(row):
                    row_data = []
                    for col in range(self.tabla.columnCount()):
                        item = self.tabla.item(row, col)
                        row_data.append(item.text() if item else '')
                    data.append(row_data)
            
            filename = f'inventory_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            
            self.status_label.setText(f'Export completed: {filename}')
            self.progress_bar.setValue(100)
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle('Export Successful')
            msg.setText(f'Inventory data has been exported to:\n{filename}')
            msg.setStyleSheet(f"background-color: {CLOUD_THEME['colors']['surface']}; color: {CLOUD_THEME['colors']['text']['primary']};")
            msg.exec()
            
        except Exception as e:
            self.mostrar_error('Export Error', f'Could not export inventory data: {str(e)}')
        finally:
            self.progress_bar.hide()

    def abrir_dialogo_nuevo(self):
        dialog = NuevoDispositivoDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.db.crear_maquina({
                'id': data['id'],
                'nombre': data['nombre'],
                'categoria': data['categoria'],
                'estado': data['estado'],
                'ubicacion': data['ubicacion'],
                'supervisor_id': data['supervisor_id']
            })
            self.cargar_datos()

    def abrir_dialogo_editar(self):
        selected_row = self.tabla.currentRow()
        if selected_row >= 0:
            maquina_id = self.tabla.item(selected_row, 0).text()
            dialog = EditarDispositivoDialog(self.db, maquina_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                self.db.actualizar_maquina(
                    data['id'],
                    data['nombre'],
                    data['categoria'],
                    data['estado'],
                    data['ubicacion'],
                    data['supervisor_id']
                )
                self.cargar_datos()
        else:
            self.mostrar_error("Selección requerida", "Por favor, seleccione un dispositivo para editar")

    def eliminar_dispositivo(self):
        selected_row = self.tabla.currentRow()
        if selected_row >= 0:
            maquina_id = self.tabla.item(selected_row, 0).text()
            confirm = QMessageBox()
            confirm.setIcon(QMessageBox.Icon.Question)
            confirm.setWindowTitle("Confirmar eliminación")
            confirm.setText("¿Está seguro de que desea eliminar este dispositivo?")
            confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            confirm.setStyleSheet(f"background-color: {CLOUD_THEME['colors']['surface']}; color: {CLOUD_THEME['colors']['text']['primary']};")
            
            if confirm.exec() == QMessageBox.StandardButton.Yes:
                try:
                    self.db.eliminar_maquina(maquina_id)
                    self.cargar_datos()
                except Exception as e:
                    self.mostrar_error("Error de eliminación", f"No se pudo eliminar el dispositivo: {str(e)}")
        else:
            self.mostrar_error("Selección requerida", "Por favor, seleccione un dispositivo para eliminar")