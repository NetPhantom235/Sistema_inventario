import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import re
import numpy as np

from PyQt6.QtGui import (
    QFont, QIcon, QColor, QPainter, QLinearGradient
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QStackedWidget, QFormLayout, QMessageBox, QDialog, QComboBox, 
    QGroupBox, QHeaderView, QGridLayout, QFrame, QScrollArea, QSizePolicy,
    QGraphicsDropShadowEffect, QSpacerItem
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QRect, QPropertyAnimation, QEasingCurve
)
from PyQt6.QtCharts import (
    QChart, QChartView, QPieSeries, QPieSlice, 
    QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QLineSeries
)

# Cloud-inspired color palette
from design_system import CLOUD_THEME, CLOUD_STYLE, APP_FONT

class CloudCard(QFrame):
    """A modern card widget with cloud-inspired design"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.initUI()
        
    def initUI(self):
        # Set up card appearance
        self.setObjectName("cloud_card")
        self.setStyleSheet(f"""
            QFrame#cloud_card {{
                background-color: {CLOUD_THEME['colors']['card']};
                border-radius: {CLOUD_THEME['components']['card']['border_radius']};
                border: 1px solid #e0e0e0;
            }}
        """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        
        # Add title if provided
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet(f"""
                font-size: 16px;
                font-weight: 500;
                color: {CLOUD_THEME['colors']['primary']};
            """)
            self.layout.addWidget(title_label)

class MetricCard(CloudCard):
    """A card displaying a key metric with icon and value"""
    def __init__(self, title, value, icon, color=CLOUD_THEME['colors']['primary'], parent=None):
        super().__init__(title="", parent=parent)
        self.metric_title = title
        self.metric_value = value
        self.icon = icon
        self.color = color
        self.setupMetric()
        
    def setupMetric(self):
        # Header with title and icon
        header = QHBoxLayout()
        
        title_label = QLabel(self.metric_title)
        title_label.setStyleSheet(f"""
            color: {CLOUD_THEME['colors']['text_light']};
            font-size: 14px;
        """)
        
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"font-size: 20px;")
        
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(icon_label)
        
        # Value display
        self.value_label = QLabel(str(self.metric_value))
        self.value_label.setStyleSheet(f"""
            color: {self.color};
            font-size: 28px;
            font-weight: bold;
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Add to layout
        self.layout.addLayout(header)
        self.layout.addWidget(self.value_label)
        
    def update_value(self, new_value):
        self.metric_value = new_value
        self.value_label.setText(str(new_value))

class ChartCard(CloudCard):
    """A card containing a chart visualization"""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.chart_view = None
        
    def set_chart(self, chart_view):
        self.chart_view = chart_view
        self.layout.addWidget(self.chart_view)

class PieChartView(QChartView):
    """A modern pie chart visualization"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.chart = QChart()
        self.chart.setTitle(title)
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        self.series = QPieSeries()
        self.chart.addSeries(self.series)
        
        self.setChart(self.chart)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
    def update_data(self, data_list):
        """Update chart with new data
        data_list: List of tuples (name, value)
        """
        self.series.clear()
        
        for name, value in data_list:
            slice = self.series.append(name, value)
            slice.setLabelVisible(True)
            
        # Customize colors
        colors = ["#0073bb", "#ff9900", "#008a00", "#d13438", "#ffb900"]
        for i, slice in enumerate(self.series.slices()):
            color_index = i % len(colors)
            slice.setBrush(QColor(colors[color_index]))
            
        self.chart.update()

class BarChartView(QChartView):
    """A modern bar chart visualization"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.chart = QChart()
        self.chart.setTitle(title)
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        
        self.series = QBarSeries()
        self.chart.addSeries(self.series)
        
        self.axisX = QBarCategoryAxis()
        self.axisY = QValueAxis()
        self.axisY.setLabelFormat("%d")
        
        self.chart.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        
        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)
        
        self.setChart(self.chart)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
    def update_data(self, categories, data_sets):
        """Update chart with new data
        categories: List of category names
        data_sets: List of tuples (set_name, values)
        """
        self.series.clear()
        self.axisX.clear()
        
        for set_name, values in data_sets:
            bar_set = QBarSet(set_name)
            bar_set.append(values)
            self.series.append(bar_set)
        
        self.axisX.append(categories)
        
        # Find max value for Y axis
        max_value = 0
        for _, values in data_sets:
            max_value = max(max_value, max(values))
        
        self.axisY.setRange(0, max_value * 1.1)  # Add 10% padding
        self.chart.update()

class ActivityList(QWidget):
    """A list showing recent activities or alerts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        
    def add_activity(self, title, description, time, status="info"):
        item = ActivityItem(title, description, time, status)
        self.layout.addWidget(item)
        
    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class ActivityItem(QFrame):
    """A single activity item with title, description and timestamp"""
    def __init__(self, title, description, time, status="info", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.time = time
        self.status = status
        self.initUI()
        
    def initUI(self):
        self.setObjectName("activity_item")
        
        # Set status color
        status_colors = {
            "info": CLOUD_THEME['colors']['secondary'],
            "success": CLOUD_THEME['colors']['success'],
            "warning": CLOUD_THEME['colors']['warning'],
            "error": CLOUD_THEME['colors']['error']
        }
        color = status_colors.get(self.status, status_colors["info"])
        
        self.setStyleSheet(f"""
            QFrame#activity_item {{
                background-color: {CLOUD_THEME['colors']['card']};
                border-radius: {CLOUD_THEME['components']['card']['border_radius']};
                border-left: 4px solid {color};
                padding: 8px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Header with title and time
        header = QHBoxLayout()
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-weight: bold;
            color: {CLOUD_THEME['colors']['text']};
        """)
        
        time_label = QLabel(self.time)
        time_label.setStyleSheet(f"""
            color: {CLOUD_THEME['colors']['text_light']};
            font-size: 12px;
        """)
        
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(time_label)
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet(f"""
            color: {CLOUD_THEME['colors']['text']};
            font-size: 13px;
        """)
        desc_label.setWordWrap(True)
        
        layout.addLayout(header)
        layout.addWidget(desc_label)

class DashboardCloud(QWidget):
    """Main dashboard widget with cloud provider inspired design"""
    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setStyleSheet(CLOUD_STYLE)
        self.setFont(APP_FONT)
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Dashboard Cloud - Estadísticas de Gestión")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #0078d7;
            margin-bottom: 20px;
        """)
        layout.addWidget(title)

        # KPI metrics row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)

        self.total_card = MetricCard("Total Inventory", 0, "📦", CLOUD_THEME['colors']['primary'])
        self.in_use_card = MetricCard("In Use", 0, "🔧", CLOUD_THEME['colors']['secondary'])
        self.available_card = MetricCard("Available", 0, "✅", CLOUD_THEME['colors']['success'])
        self.alerts_card = MetricCard("Alerts", 0, "⚠️", CLOUD_THEME['colors']['warning'])
        
        # Add hover effects
        for card in [self.total_card, self.in_use_card, self.available_card, self.alerts_card]:
            card.setGraphicsEffect(self.create_hover_effect())

        metrics_layout.addWidget(self.total_card)
        metrics_layout.addWidget(self.in_use_card)
        metrics_layout.addWidget(self.available_card)
        metrics_layout.addWidget(self.alerts_card)

        layout.addLayout(metrics_layout)
        self.setLayout(layout)

    def create_hover_effect(self):
        """Create a hover effect for dashboard cards"""
        hover_effect = QGraphicsDropShadowEffect(self)
        hover_effect.setBlurRadius(15)
        hover_effect.setColor(QColor(CLOUD_THEME['colors']['primary']))
        hover_effect.setOffset(0, 3)
        return hover_effect
        
    def initUI(self):
        # Main layout with proper spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # Dashboard header
        header = QHBoxLayout()
        title = QLabel("Cloud Dashboard")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {CLOUD_THEME['colors']['primary']};
        """)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(f"""
            background-color: {CLOUD_THEME['colors']['secondary']};
            color: white;
            border: none;
            border-radius: {CLOUD_THEME['components']['card']['border_radius']};
            padding: 8px 16px;
            font-weight: 500;
        """)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_data)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh_btn)
        
        # KPI metrics row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)
        
        self.total_card = MetricCard("Total Inventory", 0, "📦", CLOUD_THEME['colors']['primary'])
        self.in_use_card = MetricCard("In Use", 0, "🔧", CLOUD_THEME['colors']['secondary'])
        self.available_card = MetricCard("Available", 0, "✅", CLOUD_THEME['colors']['success'])
        self.alerts_card = MetricCard("Alerts", 0, "⚠️", CLOUD_THEME['colors']['warning'])
        
        # Add hover effects
        for card in [self.total_card, self.in_use_card, self.available_card, self.alerts_card]:
            card.setGraphicsEffect(self.create_hover_effect())
        
        metrics_layout.addWidget(self.total_card)
        metrics_layout.addWidget(self.in_use_card)
        metrics_layout.addWidget(self.available_card)
        metrics_layout.addWidget(self.alerts_card)
        
        # Charts row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)
        
        # Status distribution chart
        status_chart_card = ChartCard("Estado de Máquinas")
        self.status_chart = PieChartView()
        status_chart_card.set_chart(self.status_chart)
        
        # Category distribution chart
        category_chart_card = ChartCard("Distribución por Categoría")
        self.category_chart = PieChartView()
        category_chart_card.set_chart(self.category_chart)
        
        charts_layout.addWidget(status_chart_card)
        charts_layout.addWidget(category_chart_card)
        
        # Recent activity and alerts section
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)
        
        # Recent activity table
        activity_card = CloudCard("Actividad Reciente")
        activity_layout = QVBoxLayout()
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["ID", "Máquina", "Estado", "Fecha"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                background-color: {CLOUD_THEME['colors']['card']};
            }}
            QHeaderView::section {{
                background-color: {CLOUD_THEME['colors']['primary']};
                color: white;
                padding: 8px;
                font-weight: 500;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QTableWidget::item:selected {{
                background-color: {CLOUD_THEME['colors']['secondary']};
                color: white;
            }}
        """)
        
        activity_layout.addWidget(self.activity_table)
        activity_card.layout.addLayout(activity_layout)
        
        # Alerts list
        alerts_card = CloudCard("Alertas y Notificaciones")
        self.alerts_list = ActivityList()
        alerts_scroll = QScrollArea()
        alerts_scroll.setWidgetResizable(True)
        alerts_scroll.setWidget(self.alerts_list)
        alerts_scroll.setStyleSheet("border: none;")
        alerts_card.layout.addWidget(alerts_scroll)
        
        bottom_layout.addWidget(activity_card)
        bottom_layout.addWidget(alerts_card)
        
        # Add all sections to main layout
        main_layout.addLayout(header)
        main_layout.addLayout(metrics_layout)
        main_layout.addLayout(charts_layout)
        main_layout.addLayout(bottom_layout)
        
    def load_data(self):
        """Load and display all dashboard data"""
        try:
            self.show_loading_state(True)
            
            # Get fresh data from database
            maquinas = self.db_manager.obtener_maquinas()
            prestamos = self.db_manager.obtener_prestamos()
            supervisores = self.db_manager.obtener_supervisores()

            if not maquinas:
                self.show_info_overlay("No hay datos disponibles", "Registre dispositivos para comenzar")
                return

            self.update_metrics(maquinas, prestamos)
            self.update_charts(maquinas)
            self.update_activity_table(prestamos, supervisores)
            self.update_alerts(maquinas, prestamos)
            
            if any(p['fecha_devolucion'] is None for p in prestamos):
                self.alerts_list.add_activity("Préstamos activos", "Existen préstamos pendientes de devolución", 
                    datetime.now().strftime('%Y-%m-%d %H:%M'), "warning")
        
        except Exception as e:
            self.log_error(f"Dashboard Error: {str(e)}")
            self.show_error_overlay("Error de carga", "No se pudieron obtener los datos")
        finally:
            self.show_loading_state(False)
            self.refresh_timer.start()
    
    def update_metrics(self, maquinas, prestamos):
        """Update the KPI metric cards with real data"""
        total = len(maquinas)
        in_use = sum(1 for m in maquinas if m['estado'] == 'en_uso')
        available = sum(1 for m in maquinas if m['estado'] == 'disponible')
        alerts = sum(1 for p in prestamos if 
                    (datetime.now() - p['fecha_prestamo']).days > 7 and 
                    p['fecha_devolucion'] is None)
        
        self.total_card.update_value(total)
        self.in_use_card.update_value(in_use)
        self.available_card.update_value(available)
        self.alerts_card.update_value(alerts)
    
    def update_charts(self, maquinas):
        """Update all chart visualizations with real data"""
        # Status distribution
        status_counts = {
            'Disponible': sum(1 for m in maquinas if m['estado'] == 'disponible'),
            'En Uso': sum(1 for m in maquinas if m['estado'] == 'en_uso'),
            'Mantenimiento': sum(1 for m in maquinas if m['estado'] == 'mantenimiento')
        }
        self.status_chart.update_data(list(status_counts.items()))
        
        # Category distribution
        category_counts = {}
        for m in maquinas:
            cat = m['categoria'] or 'Sin categoría'
            category_counts[cat] = category_counts.get(cat, 0) + 1
        self.category_chart.update_data(list(category_counts.items()))
    
    def update_activity_table(self, prestamos, supervisores):
        """Update the recent activity table with real data"""
        self.activity_table.setRowCount(0)
        supervisores_dict = {s['id']: s['nombre'] for s in supervisores}
        
        for p in prestamos[-10:]:  # Last 10 loans
            row = self.activity_table.rowCount()
            self.activity_table.insertRow(row)
            
            self.activity_table.setItem(row, 0, QTableWidgetItem(p['id']))
            self.activity_table.setItem(row, 1, QTableWidgetItem(
                self.db_manager.obtener_maquina(p['maquina_id'])['nombre']))
            self.activity_table.setItem(row, 2, QTableWidgetItem(
                'Prestado' if p['fecha_devolucion'] is None else 'Devuelto'))
            self.activity_table.setItem(row, 3, QTableWidgetItem(
                p['fecha_prestamo'].strftime('%Y-%m-%d %H:%M')))
    
    def update_alerts(self):
        """Update the alerts and notifications list"""
        # Clear existing alerts
        self.alerts_list.clear()
        
        # Sample alerts - would be fetched from database in real implementation
        alerts = [
            {"title": "Mantenimiento requerido", "description": "Impresora HP-001 requiere mantenimiento programado", "time": "Hace 2 horas", "status": "warning"},
            {"title": "Préstamo vencido", "description": "Zebra Z-123 tiene préstamo vencido por 3 días", "time": "Hace 1 día", "status": "error"},
            {"title": "Nuevo equipo registrado", "description": "Laptop Dell XPS-15 ha sido registrada en el sistema", "time": "Hace 3 días", "status": "info"},
            {"title": "Devolución completada", "description": "Scanner S-456 ha sido devuelto correctamente", "time": "Hace 4 días", "status": "success"}
        ]
        
        for alert in alerts:
            self.alerts_list.add_activity(
                alert["title"],
                alert["description"],
                alert["time"],
                alert["status"]
            )

# For testing the dashboard independently
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = DashboardCloud()
    dashboard.setWindowTitle("Sistema de Gestión de Máquinas - Dashboard")
    dashboard.setMinimumSize(1200, 800)
    dashboard.show()
    sys.exit(app.exec())