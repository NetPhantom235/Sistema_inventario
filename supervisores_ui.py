from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QLineEdit, QComboBox, QLabel, QFrame,
    QProgressBar, QScrollArea, QGridLayout, QSpacerItem, QSizePolicy, QDialog)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPalette, QLinearGradient
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from db_manager import DatabaseManager
from nuevo_supervisor_dialog import NuevoSupervisorDialog
from datetime import datetime, timedelta
import uuid

class EnterpriseMetricCard(QFrame):
    def __init__(self, title, value, icon_path=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2D2D2D;
                border-radius: 10px;
                padding: 15px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet('font-size: 14px; color: #B0B0B0;')
        header.addWidget(title_label)
        if icon_path:
            icon = QLabel()
            icon.setPixmap(QIcon(icon_path).pixmap(QSize(24, 24)))
            header.addWidget(icon)
        layout.addLayout(header)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet('font-size: 24px; font-weight: bold; color: #FFFFFF;')
        layout.addWidget(value_label)

class SupervisoresUI(QWidget):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.setup_auto_refresh()
        self.cargar_datos()

    def setup_auto_refresh(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.cargar_datos)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header with search and filters
        header = QFrame()
        header.setStyleSheet('background-color: #2D2D2D; border-radius: 10px; padding: 15px;')
        header_layout = QGridLayout(header)

        # Search bar
        search_box = QFrame()
        search_layout = QHBoxLayout(search_box)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search supervisors...')
        self.search_input.textChanged.connect(self.filter_supervisors)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #3D3D3D;
                border: 1px solid #505050;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
        """)
        search_layout.addWidget(self.search_input)

        # Filters
        self.role_filter = QComboBox()
        self.role_filter.addItems(['All Roles', 'Admin', 'Manager', 'Supervisor'])
        self.status_filter = QComboBox()
        self.status_filter.addItems(['All Status', 'Active', 'Inactive', 'Pending'])
        
        for combo in [self.role_filter, self.status_filter]:
            combo.setStyleSheet("""
                QComboBox {
                    background: #3D3D3D;
                    border: 1px solid #505050;
                    border-radius: 5px;
                    padding: 8px;
                    color: white;
                    min-width: 150px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: url(icons/dropdown.png);
                    width: 12px;
                    height: 12px;
                }
            """)

        search_layout.addWidget(self.role_filter)
        search_layout.addWidget(self.status_filter)

        # Action buttons
        action_box = QFrame()
        action_layout = QHBoxLayout(action_box)
        
        self.btn_nuevo = QPushButton('Add Supervisor')
        self.btn_editar = QPushButton('Edit')
        self.btn_eliminar = QPushButton('Delete')
        self.btn_export = QPushButton('Export')
        self.btn_audit = QPushButton('Audit Log')

        for btn in [self.btn_nuevo, self.btn_editar, self.btn_eliminar, self.btn_export, self.btn_audit]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106EBE;
                }
            """)
            action_layout.addWidget(btn)

        header_layout.addWidget(search_box, 0, 0)
        header_layout.addWidget(action_box, 0, 1)

        # Metrics Dashboard
        metrics = QFrame()
        metrics.setStyleSheet('background-color: #2D2D2D; border-radius: 10px; padding: 15px;')
        metrics_layout = QHBoxLayout(metrics)
        
        total_card = EnterpriseMetricCard('Total Supervisors', '0', 'icons/users.png')
        active_card = EnterpriseMetricCard('Active', '0', 'icons/active.png')
        pending_card = EnterpriseMetricCard('Pending', '0', 'icons/pending.png')
        
        for card in [total_card, active_card, pending_card]:
            metrics_layout.addWidget(card)

        # Main content area
        content = QFrame()
        content.setStyleSheet('background-color: #2D2D2D; border-radius: 10px;')
        content_layout = QVBoxLayout(content)

        # Enhanced table
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            'ID', 'Name', 'Email', 'Phone', 'Role', 'Status',
            'Last Active', 'Actions'
        ])
        
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: #2D2D2D;
                border: none;
                gridline-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
                color: white;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                padding: 8px;
                border: none;
                color: white;
                font-weight: bold;
            }
        """)
        
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        content_layout.addWidget(self.tabla)

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

        # Add all components to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(metrics)
        main_layout.addWidget(content)
        main_layout.addWidget(status_bar)

        # Connect signals
        self.btn_nuevo.clicked.connect(self.abrir_dialogo_nuevo)
        self.btn_editar.clicked.connect(self.abrir_dialogo_editar)
        self.btn_eliminar.clicked.connect(self.eliminar_supervisor)
        self.btn_export.clicked.connect(self.export_data)
        self.btn_audit.clicked.connect(self.show_audit_log)
        self.role_filter.currentTextChanged.connect(self.filter_supervisors)
        self.status_filter.currentTextChanged.connect(self.filter_supervisors)

    def cargar_datos(self):
        try:
            self.status_label.setText('Loading data...')
            self.progress_bar.setRange(0, 0)
            self.progress_bar.show()
            
            supervisores = self.db.obtener_supervisores()
            self.tabla.setRowCount(0)
            
            if not supervisores:
                self.mostrar_estado_vacio('No supervisors registered')
                return

            self.tabla.setRowCount(len(supervisores))
            for i, supervisor in enumerate(supervisores):
                self.tabla.setItem(i, 0, QTableWidgetItem(supervisor.get('id', 'N/A')))
                self.tabla.setItem(i, 1, QTableWidgetItem(supervisor.get('nombre', 'N/A')))
                self.tabla.setItem(i, 2, QTableWidgetItem(supervisor['email']))
                self.tabla.setItem(i, 3, QTableWidgetItem(supervisor['telefono']))
                self.tabla.setItem(i, 4, QTableWidgetItem(supervisor['permiso']))
                
                # Enhanced status cell with color coding
                status_item = QTableWidgetItem(supervisor.get('status', 'Active'))
                status_colors = {
                    'Active': '#28A745',
                    'Inactive': '#DC3545',
                    'Pending': '#FFC107'
                }
                status_item.setBackground(
                    QColor(status_colors.get(supervisor.get('status', 'Active'), '#6C757D'))
                )
                self.tabla.setItem(i, 5, status_item)
                
                # Last active timestamp
                last_active = supervisor.get('ultima_actividad', datetime.now())
                if isinstance(last_active, str):
                    last_active = datetime.fromisoformat(last_active)
                self.tabla.setItem(i, 6, QTableWidgetItem(last_active.strftime('%Y-%m-%d %H:%M')))
                
                # Action buttons cell
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                
                btn_view = QPushButton(QIcon('icons/view.png'), '')
                btn_edit = QPushButton(QIcon('icons/edit.png'), '')
                btn_delete = QPushButton(QIcon('icons/delete.png'), '')
                
                for btn in [btn_view, btn_edit, btn_delete]:
                    btn.setFixedSize(24, 24)
                    btn.setStyleSheet('background: transparent; border: none;')
                    actions_layout.addWidget(btn)
                
                self.tabla.setCellWidget(i, 7, actions_widget)
            
            self.status_label.setText(f'Data updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            
        except Exception as e:
            self.mostrar_error('Loading Error', f'Could not load supervisors: {str(e)}')
        finally:
            self.progress_bar.hide()

    def filter_supervisors(self):
        search_text = self.search_input.text().lower()
        role = self.role_filter.currentText()
        status = self.status_filter.currentText()
        
        for row in range(self.tabla.rowCount()):
            name = self.tabla.item(row, 1).text().lower()
            supervisor_role = self.tabla.item(row, 4).text()
            supervisor_status = self.tabla.item(row, 5).text()
            
            name_match = search_text in name
            role_match = role == 'All Roles' or role == supervisor_role
            status_match = status == 'All Status' or status == supervisor_status
            
            self.tabla.setRowHidden(row, not (name_match and role_match and status_match))

    def export_data(self):
        try:
            self.status_label.setText('Exporting data...')
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            
            filename = f'supervisors_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = ['ID', 'Name', 'Email', 'Phone', 'Role', 'Status', 'Last Active']
                writer.writerow(headers)
                
                for row in range(self.tabla.rowCount()):
                    if not self.tabla.isRowHidden(row):
                        row_data = []
                        for col in range(self.tabla.columnCount() - 1):  # Exclude actions column
                            item = self.tabla.item(row, col)
                            row_data.append(item.text() if item else '')
                        writer.writerow(row_data)
            
            self.status_label.setText(f'Export completed: {filename}')
            self.progress_bar.setValue(100)
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle('Export Successful')
            msg.setText(f'Data has been exported to:\n{filename}')
            msg.exec()
            
        except Exception as e:
            self.mostrar_error('Export Error', f'Could not export data: {str(e)}')
        finally:
            self.progress_bar.hide()

    def show_audit_log(self):
        selected_row = self.tabla.currentRow()
        if selected_row >= 0:
            supervisor_id = self.tabla.item(selected_row, 0).text()
            try:
                audit_logs = self.db.obtener_audit_logs(supervisor_id)
                dialog = AuditLogDialog(audit_logs, self)
                dialog.exec()
            except Exception as e:
                self.mostrar_error('Audit Log Error', f'Could not load audit logs: {str(e)}')
        else:
            self.mostrar_error('Selection Required', 'Please select a supervisor to view audit logs')

    def mostrar_estado_vacio(self, mensaje):
        self.tabla.setRowCount(1)
        self.tabla.setItem(0, 0, QTableWidgetItem(mensaje))
        self.tabla.item(0, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabla.setSpan(0, 0, 1, self.tabla.columnCount())

    def mostrar_error(self, titulo, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.exec()

    def abrir_dialogo_nuevo(self):
        dialog = NuevoSupervisorDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                self.db.insertar_supervisor(
                    data['id'],
                    data['nombre'],
                    data['email'],
                    data['telefono'],
                    data['permiso'],
                    data['auth_provider']
                )
                self.cargar_datos()
            except Exception as e:
                self.mostrar_error('Error', f'Could not create supervisor: {str(e)}')

    def abrir_dialogo_editar(self):
        selected_row = self.tabla.currentRow()
        if selected_row >= 0:
            supervisor_id = self.tabla.item(selected_row, 0).text()
            try:
                dialog = EditarSupervisorDialog(self.db, supervisor_id)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    self.db.actualizar_supervisor(
                        data['id'],
                        data['nombre'],
                        data['email'],
                        data['telefono'],
                        data['permiso'],
                        data['auth_provider']
                    )
                    self.cargar_datos()
            except Exception as e:
                self.mostrar_error('Error', f'Could not edit supervisor: {str(e)}')
        else:
            self.mostrar_error('Selection Required', 'Please select a supervisor to edit')

    def eliminar_supervisor(self):
        selected_row = self.tabla.currentRow()
        if selected_row >= 0:
            supervisor_id = self.tabla.item(selected_row, 0).text()
            confirm = QMessageBox()
            confirm.setIcon(QMessageBox.Icon.Question)
            confirm.setWindowTitle('Confirm Deletion')
            confirm.setText('Are you sure you want to delete this supervisor?')
            confirm.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm.exec() == QMessageBox.StandardButton.Yes:
                try:
                    self.db.eliminar_supervisor(supervisor_id)
                    self.cargar_datos()
                except Exception as e:
                    self.mostrar_error('Deletion Error', f'Could not delete supervisor: {str(e)}')
        else:
            self.mostrar_error('Selection Required', 'Please select a supervisor to delete')

class AuditLogDialog(QDialog):
    def __init__(self, logs, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Audit Log')
        self.setMinimumSize(600, 400)
        self.setup_ui(logs)

    def setup_ui(self, logs):
        layout = QVBoxLayout(self)
        
        # Log table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Timestamp', 'Action', 'Details', 'User'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2D2D2D;
                border: none;
                color: white;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        
        # Populate logs
        self.table.setRowCount(len(logs))
        for i, log in enumerate(logs):
            self.table.setItem(i, 0, QTableWidgetItem(log['timestamp']))
            self.table.setItem(i, 1, QTableWidgetItem(log['action']))
            self.table.setItem(i, 2, QTableWidgetItem(log['details']))
            self.table.setItem(i, 3, QTableWidgetItem(log['user']))
        
        layout.addWidget(self.table)
        
        # Close button
        btn_close = QPushButton('Close')
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        
        layout.addWidget(btn_close)
