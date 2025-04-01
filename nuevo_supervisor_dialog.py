import re
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from db_manager import DatabaseManager
from design_system import CLOUD_THEME, CLOUD_STYLE

class NuevoSupervisorDialog(QDialog):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.setWindowTitle('Registrar Nuevo Supervisor')
        self.setStyleSheet(CLOUD_STYLE)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        form.setVerticalSpacing(12)
        
        self.id_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.email_input = QLineEdit()
        self.telefono_input = QLineEdit()
        
        self.permiso_combo = QComboBox()
        self.permiso_combo.addItems(['basic', 'admin', 'auditor'])
        
        form.addRow('ID:', self.id_input)
        form.addRow('Nombre:', self.nombre_input)
        form.addRow('Email:', self.email_input)
        form.addRow('Teléfono:', self.telefono_input)
        form.addRow('Permiso:', self.permiso_combo)
        
        buttons = QDialogButtonBox(Qt.Orientation.Horizontal, self)
        buttons.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)
        
    def validate_and_accept(self):
        id = self.id_input.text().strip()
        nombre = self.nombre_input.text().strip()
        email = self.email_input.text().strip()
        telefono = self.telefono_input.text().strip()
        
        if not all([id, nombre, email, telefono]):
            self.show_error("Campos requeridos", "Todos los campos son obligatorios")
            return
        
        if not re.match(r'^[A-Z0-9\-]{3,20}$', id):
            self.show_error("ID inválido", "El ID debe contener solo mayúsculas, números y guiones (3-20 caracteres)")
            return
        
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            self.show_error("Email inválido", "Por favor ingrese un email válido")
            return
        
        if not re.match(r'^\+?\d{8,15}$', telefono):
            self.show_error("Teléfono inválido", "Por favor ingrese un número de teléfono válido")
            return
        
        if self.db.supervisor_existe(id):
            self.show_error("ID duplicado", "El ID ingresado ya existe en el sistema")
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
            'id': self.id_input.text(),
            'nombre': self.nombre_input.text(),
            'email': self.email_input.text(),
            'telefono': self.telefono_input.text(),
            'permiso': self.permiso_combo.currentText(),
            'auth_provider': 'azure_ad'  # Default auth provider
        }