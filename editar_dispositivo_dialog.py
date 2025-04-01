import re
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from db_manager import DatabaseManager
from design_system import CLOUD_THEME, CLOUD_STYLE

class EditarDispositivoDialog(QDialog):
    def __init__(self, db: DatabaseManager, maquina_id: str):
        super().__init__()
        self.db = db
        self.maquina_id = maquina_id
        self.setWindowTitle('Editar Dispositivo')
        self.setStyleSheet(CLOUD_STYLE)
        self.init_ui()
        self.cargar_datos()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        form.setVerticalSpacing(12)
        
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
            
        form.addRow('Nombre:', self.nombre_input)
        form.addRow('Categoría:', self.categoria_input)
        form.addRow('Estado:', self.estado_combo)
        form.addRow('Ubicación:', self.ubicacion_input)
        form.addRow('Supervisor:', self.supervisor_combo)
        
        buttons = QDialogButtonBox(Qt.Orientation.Horizontal, self)
        buttons.setStandardButtons(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)
    
    def cargar_datos(self):
        try:
            maquina = self.db.obtener_maquina_por_id(self.maquina_id)
            if not maquina:
                self.show_error("Error", "No se encontró el dispositivo")
                self.reject()
                return
                
            self.nombre_input.setText(maquina['nombre'])
            self.categoria_input.setText(maquina['categoria'])
            self.estado_combo.setCurrentText(maquina['estado'])
            self.ubicacion_input.setText(maquina['ubicacion'])
            
            # Set supervisor
            for i in range(self.supervisor_combo.count()):
                if self.supervisor_combo.itemData(i) == maquina['supervisor_id']:
                    self.supervisor_combo.setCurrentIndex(i)
                    break
                    
        except Exception as e:
            self.show_error("Error de carga", f"No se pudo cargar el dispositivo: {str(e)}")
            self.reject()
        
    def validate_and_accept(self):
        nombre = self.nombre_input.text().strip()
        
        if not nombre:
            self.show_error("Campos requeridos", "El nombre es obligatorio")
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
            'id': self.maquina_id,
            'nombre': self.nombre_input.text(),
            'categoria': self.categoria_input.text(),
            'estado': self.estado_combo.currentText(),
            'ubicacion': self.ubicacion_input.text(),
            'supervisor_id': self.supervisor_combo.currentData()
        }