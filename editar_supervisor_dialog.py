import re
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from db_manager import DatabaseManager
from design_system import CLOUD_THEME, CLOUD_STYLE

class EditarSupervisorDialog(QDialog):
    def __init__(self, db: DatabaseManager, supervisor_id: str):
        super().__init__()
        self.db = db
        self.supervisor_id = supervisor_id
        self.setWindowTitle('Editar Supervisor')
        self.setStyleSheet(CLOUD_STYLE)
        self.init_ui()
        self.cargar_datos()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        form.setVerticalSpacing(12)
        
        self.nombre_input = QLineEdit()
        self.email_input = QLineEdit()
        self.telefono_input = QLineEdit()
        
        self.permiso_combo = QComboBox()
        self.permiso_combo.addItems(['basic', 'admin', 'auditor'])
        
        form.addRow('Nombre:', self.nombre_input)
        form.addRow('Email:', self.email_input)
        form.addRow('Teléfono:', self.telefono_input)
        form.addRow('Permiso:', self.permiso_combo)
        
        buttons = QDialogButtonBox(Qt.Orientation.Horizontal, self)
        buttons.setStandardButtons(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)
    
    def cargar_datos(self):
        try:
            supervisor = self.db.obtener_supervisor_por_id(self.supervisor_id)
            if not supervisor:
                self.show_error("Error", "No se encontró el supervisor")
                self.reject()
                return
                
            self.nombre_input.setText(supervisor['nombre'])
            self.email_input.setText(supervisor['email'])
            self.telefono_input.setText(supervisor['telefono'])
            self.permiso_combo.setCurrentText(supervisor['permiso'])
                    
        except Exception as e:
            self.show_error("Error de carga", f"No se pudo cargar el supervisor: {str(e)}")
            self.reject()
        
    def validate_and_accept(self):
        nombre = self.nombre_input.text().strip()
        email = self.email_input.text().strip()
        telefono = self.telefono_input.text().strip()
        
        if not all([nombre, email, telefono]):
            self.show_error("Campos requeridos", "Todos los campos son obligatorios")
            return
        
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            self.show_error("Email inválido", "Por favor ingrese un email válido")
            return
        
        if not re.match(r'^\+?\d{8,15}$', telefono):
            self.show_error("Teléfono inválido", "Por favor ingrese un número de teléfono válido")
            return
        
        self.accept()

    def show_error(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet(CLOUD_STYLE)
        msg.exec()

    def get_data(self):
        return {
            'id': self.supervisor_id,
            'nombre': self.nombre_input.text(),
            'email': self.email_input.text(),
            'telefono': self.telefono_input.text(),
            'permiso': self.permiso_combo.currentText(),
            'auth_provider': 'azure_ad'  # Maintain existing auth provider
        }