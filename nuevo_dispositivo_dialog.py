import re
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from db_manager import DatabaseManager

CLOUD_STYLE = """
QDialog {
    background: #2F2F2F;
    color: #FFFFFF;
    font-family: 'Segoe UI', Arial, sans-serif;
    border: 1px solid #404040;
    border-radius: 8px;
}

QLineEdit, QComboBox {
    background: #333333;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 8px 12px;
    min-width: 300px;
    font-size: 14px;
}

QLineEdit:focus, QComboBox:focus {
    border: 2px solid #0073bb;
}

QDialogButtonBox {
    border-top: 1px solid #404040;
    padding-top: 16px;
}

QDialogButtonBox::button {
    background-color: #0073bb;
    border-radius: 4px;
    padding: 8px 16px;
    min-width: 80px;
}

QDialogButtonBox::button:hover {
    background-color: #0062A3;
}

QLabel {
    color: #9BA7B0;
    font-weight: 500;
}

QLineEdit:invalid {
    border: 2px solid #d13438;
}

QMessageBox {
    background: #2F2F2F;
    color: #FFFFFF;
}

QMessageBox QLabel {
    color: #FFFFFF;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 8px 16px;
}
"""

class NuevoDispositivoDialog(QDialog):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.setWindowTitle('Registrar Nuevo Dispositivo')
        self.setStyleSheet(CLOUD_STYLE)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        form.setVerticalSpacing(12)
        
        self.id_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.categoria_input = QLineEdit()
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(['Disponible', 'En Uso', 'Mantenimiento'])
        self.ubicacion_input = QLineEdit()
        
        # Supervisor dropdown
        self.supervisor_combo = QComboBox()
        supervisores = self.db.obtener_supervisores()
        for supervisor in supervisores:
            if supervisor.get('nombre') and supervisor.get('id'):
                self.supervisor_combo.addItem(
                    f"{supervisor.get('nombre', '')} ({supervisor.get('id', '')})", 
                    supervisor.get('id')
                )
        
        if self.supervisor_combo.count() == 0:
            self.show_error("Sin supervisores válidos", "No hay supervisores con ID y nombre válidos")
            self.reject()
        form.addRow('ID:', self.id_input)
        form.addRow('Nombre:', self.nombre_input)
        form.addRow('Categoría:', self.categoria_input)
        form.addRow('Estado:', self.estado_combo)
        form.addRow('Ubicación:', self.ubicacion_input)
        form.addRow('Supervisor:', self.supervisor_combo)
        
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
        
        if not id or not nombre:
            self.show_error("Campos requeridos", "ID y Nombre son campos obligatorios")
            return
        
        if not re.match(r'^[A-Z0-9\-]{3,20}$', id):
            self.show_error("ID inválido", "El ID debe contener solo mayúsculas, números y guiones (3-20 caracteres)")
            return
        
        if self.db.maquina_existe(id):
            self.show_error("ID duplicado", "El ID ingresado ya existe en el sistema")
            return
        
        if self.supervisor_combo.count() == 0:
            self.show_error("Sin supervisores", "No hay supervisores registrados")
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
            'categoria': self.categoria_input.text(),
            'estado': self.estado_combo.currentText(),
            'ubicacion': self.ubicacion_input.text(),
            'supervisor_id': self.supervisor_combo.currentData()
        }