import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import re
import numpy as np

from PyQt6.QtGui import (
    QFont, QIcon, QColor, QPainter, QLinearGradient, QBrush, QPen, QRadialGradient
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QStackedWidget, QFormLayout, QMessageBox, QDialog, QComboBox, 
    QGroupBox, QHeaderView, QGridLayout, QFrame, QScrollArea, QSizePolicy,
    QGraphicsDropShadowEffect, QSpacerItem, QCalendarWidget, QTimeEdit,
    QProgressBar, QSlider, QDial
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QRect, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QSequentialAnimationGroup, pyqtSignal, QThread
)
from PyQt6.QtCharts import (
    QChart, QChartView, QPieSeries, QPieSlice, QSplineSeries,
    QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QLineSeries,
    QAreaSeries, QScatterSeries, QCandlestickSeries, QBoxPlotSeries
)

from design_system import CLOUD_THEME, CLOUD_STYLE, APP_FONT
from db_manager import DatabaseManager

class EnterpriseCard(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setupUI()
        self.setupAnimations()

    def setupUI(self):
        self.setObjectName("enterprise_card")
        self.setStyleSheet(f"""
            QFrame#enterprise_card {{
                background-color: {CLOUD_THEME['colors']['surface']};
                border-radius: 12px;
                border: 1px solid {CLOUD_THEME['colors']['border']};
            }}
        """)
        
        # Enhanced shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(16)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet(f"""
                font-size: 18px;
                font-weight: 600;
                color: {CLOUD_THEME['colors']['text']['primary']};
            """)
            self.layout.addWidget(title_label)

    def setupAnimations(self):
        self.hover_animation = QPropertyAnimation(self, b"maximumHeight")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event):
        self.hover_animation.setStartValue(self.height())
        self.hover_animation.setEndValue(self.height() + 10)
        self.hover_animation.start()

    def leaveEvent(self, event):
        self.hover_animation.setStartValue(self.height())
        self.hover_animation.setEndValue(self.height() - 10)
        self.hover_animation.start()

class MetricCard(EnterpriseCard):
    def __init__(self, title, value, icon, trend=0, color=CLOUD_THEME['colors']['primary'], parent=None):
        super().__init__(title="", parent=parent)
        self.metric_title = title
        self.metric_value = value
        self.icon = icon
        self.trend = trend
        self.color = color
        self.setupMetric()

    def setupMetric(self):
        # Header with title and icon
        header = QHBoxLayout()
        
        title_label = QLabel(self.metric_title)
        title_label.setStyleSheet(f"""
            color: {CLOUD_THEME['colors']['text']['secondary']};
            font-size: 16px;
            font-weight: 500;
        """)
        
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"font-size: 24px;")
        
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(icon_label)
        
        # Value with trend indicator
        value_container = QHBoxLayout()
        
        value_label = QLabel(str(self.metric_value))
        value_label.setStyleSheet(f"""
            color: {self.color};
            font-size: 32px;
            font-weight: bold;
        """)
        
        if self.trend != 0:
            trend_label = QLabel(f"{'+' if self.trend > 0 else ''}{self.trend}%")
            trend_label.setStyleSheet(f"""
                color: {'#22c55e' if self.trend > 0 else '#ef4444'};
                font-size: 14px;
                font-weight: 500;
                margin-left: 8px;
            """)
            value_container.addWidget(trend_label)
        
        value_container.addWidget(value_label)
        value_container.addStretch()
        
        self.layout.addLayout(header)
        self.layout.addLayout(value_container)

class ChartCard(EnterpriseCard):
    def __init__(self, title, chart_type="line", parent=None):
        super().__init__(title, parent)
        self.chart_type = chart_type
        self.setupChart()

    def setupChart(self):
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self.chart.setBackgroundBrush(QBrush(QColor("transparent")))
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet("background: transparent;")
        
        self.layout.addWidget(self.chart_view)

    def update_data(self, data):
        self.chart.removeAllSeries()
        
        if self.chart_type == "pie":
            series = QPieSeries()
            for label, value in data:
                slice = series.append(label, value)
                slice.setLabelVisible(True)
            self.chart.addSeries(series)
            
        elif self.chart_type == "bar":
            series = QBarSeries()
            categories = []
            for category, values in data.items():
                bar_set = QBarSet(category)
                bar_set.append(values)
                series.append(bar_set)
                categories.extend(values)
            
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axis_x)
            
            axis_y = QValueAxis()
            self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(axis_y)
            
            self.chart.addSeries(series)
            
        elif self.chart_type == "line":
            for series_name, points in data.items():
                series = QSplineSeries()
                series.setName(series_name)
                for point in points:
                    series.append(point[0], point[1])
                self.chart.addSeries(series)
                
            axis_x = QValueAxis()
            axis_y = QValueAxis()
            self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            
            for series in self.chart.series():
                series.attachAxis(axis_x)
                series.attachAxis(axis_y)

class ActivityList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)

    def add_activity(self, title, description, time, status="info", icon=None):
        item = ActivityItem(title, description, time, status, icon)
        self.layout.addWidget(item)

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class ActivityItem(QFrame):
    def __init__(self, title, description, time, status="info", icon=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.time = time
        self.status = status
        self.icon = icon
        self.setupUI()

    def setupUI(self):
        self.setObjectName("activity_item")
        
        status_colors = {
            "info": CLOUD_THEME['colors']['info'],
            "success": CLOUD_THEME['colors']['success'],
            "warning": CLOUD_THEME['colors']['warning'],
            "error": CLOUD_THEME['colors']['error']
        }
        color = status_colors.get(self.status, status_colors["info"])
        
        self.setStyleSheet(f"""
            QFrame#activity_item {{
                background-color: {CLOUD_THEME['colors']['surface']};
                border-radius: 8px;
                border-left: 4px solid {color};
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet(f"font-size: 24px; margin-right: 12px;")
            layout.addWidget(icon_label)
        
        content = QVBoxLayout()
        
        header = QHBoxLayout()
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-weight: 600;
            color: {CLOUD_THEME['colors']['text']['primary']};
            font-size: 14px;
        """)
        
        time_label = QLabel(self.time)
        time_label.setStyleSheet(f"""
            color: {CLOUD_THEME['colors']['text']['secondary']};
            font-size: 12px;
        """)
        
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(time_label)
        
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet(f"""
            color: {CLOUD_THEME['colors']['text']['secondary']};
            font-size: 13px;
        """)
        desc_label.setWordWrap(True)
        
        content.addLayout(header)
        content.addWidget(desc_label)
        
        layout.addLayout(content)

class DashboardCloud(QWidget):
    refresh_requested = pyqtSignal()
    
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setupUI()
        self.setupRefreshTimer()
        self.loadData()

    def setupUI(self):
        self.setStyleSheet(CLOUD_STYLE)
        self.setFont(APP_FONT)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Enterprise Cloud Dashboard")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {CLOUD_THEME['colors']['text']['primary']};
        """)
        
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CLOUD_THEME['colors']['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {CLOUD_THEME['colors']['primary_dark']};
            }}
        """)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.loadData)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh_btn)
        
        # Metrics Grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(16)
        
        self.total_devices = MetricCard("Total Devices", 0, "🖥️", color=CLOUD_THEME['colors']['primary'])
        self.active_devices = MetricCard("Active Devices", 0, "✨", trend=5, color=CLOUD_THEME['colors']['success'])
        self.alerts = MetricCard("Active Alerts", 0, "⚠️", color=CLOUD_THEME['colors']['warning'])
        self.system_health = MetricCard("System Health", "98%", "💪", color=CLOUD_THEME['colors']['info'])
        
        metrics_grid.addWidget(self.total_devices, 0, 0)
        metrics_grid.addWidget(self.active_devices, 0, 1)
        metrics_grid.addWidget(self.alerts, 0, 2)
        metrics_grid.addWidget(self.system_health, 0, 3)
        
        # Charts Section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)
        
        self.usage_chart = ChartCard("Resource Usage", "line")
        self.distribution_chart = ChartCard("Device Distribution", "pie")
        self.performance_chart = ChartCard("Performance Metrics", "bar")
        
        charts_layout.addWidget(self.usage_chart)
        charts_layout.addWidget(self.distribution_chart)
        charts_layout.addWidget(self.performance_chart)
        
        # Activity and Alerts Section
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)
        
        # Recent Activity
        activity_card = EnterpriseCard("Recent Activity")
        self.activity_list = ActivityList()
        activity_scroll = QScrollArea()
        activity_scroll.setWidget(self.activity_list)
        activity_scroll.setWidgetResizable(True)
        activity_scroll.setStyleSheet("border: none; background: transparent;")
        activity_card.layout.addWidget(activity_scroll)
        
        # Active Alerts
        alerts_card = EnterpriseCard("Active Alerts")
        self.alerts_list = ActivityList()
        alerts_scroll = QScrollArea()
        alerts_scroll.setWidget(self.alerts_list)
        alerts_scroll.setWidgetResizable(True)
        alerts_scroll.setStyleSheet("border: none; background: transparent;")
        alerts_card.layout.addWidget(alerts_scroll)
        
        bottom_layout.addWidget(activity_card)
        bottom_layout.addWidget(alerts_card)
        
        # Add all sections to main layout
        layout.addLayout(header)
        layout.addLayout(metrics_grid)
        layout.addLayout(charts_layout)
        layout.addLayout(bottom_layout)
        
        # Status bar
        self.status_bar = QFrame()
        self.status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {CLOUD_THEME['colors']['surface']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        status_layout = QHBoxLayout(self.status_bar)
        
        self.status_label = QLabel("System Ready")
        self.status_label.setStyleSheet(f"color: {CLOUD_THEME['colors']['text']['secondary']};")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {CLOUD_THEME['colors']['surface']};
                border: none;
                border-radius: 3px;
                text-align: center;
                color: white;
            }}
            QProgressBar::chunk {{
                background: {CLOUD_THEME['colors']['primary']};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.hide()
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.status_bar)

    def setupRefreshTimer(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.loadData)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def loadData(self):
        try:
            self.showLoadingState(True)
            
            # Fetch data from database
            devices = self.db_manager.obtener_maquinas()
            loans = self.db_manager.obtener_prestamos()
            supervisors = self.db_manager.obtener_supervisores()
            
            # Reset all metrics and charts to empty state
            self.total_devices.metric_value = 0
            self.active_devices.metric_value = 0
            self.alerts.metric_value = 0
            self.system_health.metric_value = "N/A"
            
            # Clear activity and alerts lists
            self.activity_list.clear()
            self.alerts_list.clear()
            
            if not any([devices, loans, supervisors]):
                self.showMessage("No Data Available", "Please add devices, supervisors, and create loans to get started.", "info")
                self.status_label.setText("No data available - System ready for data input")
                self.showLoadingState(False)
                return
            
            if not devices:
                self.showMessage("No Devices Found", "Please add some devices to get started", "info")
            else:
                self.updateMetrics(devices, loans)
                self.updateCharts(devices, loans)
            
            if loans and supervisors:
                self.updateActivityList(loans, supervisors)
                self.updateAlerts(devices, loans)
            
            self.showLoadingState(False)
            self.status_label.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            self.showMessage("Error", f"Failed to load dashboard data: {str(e)}", "error")
            self.showLoadingState(False)
            self.status_label.setText("Error loading data - Check system logs")

    def updateMetrics(self, devices, loans):
        total = len(devices)
        active = sum(1 for d in devices if d['estado'] == 'en_uso')
        alerts_count = sum(1 for l in loans if 
            l['fecha_devolucion'] is None and 
            (datetime.now() - l['fecha_prestamo']).days > 7)
        
        self.total_devices.metric_value = float(total)
        self.active_devices.metric_value = float(active)
        self.alerts.metric_value = float(alerts_count)
        
        # Update system health based on various factors
        health_score = 100 - (alerts_count * 5)
        self.system_health.metric_value = float(max(0, health_score))

    def updateCharts(self, devices, loans):
        # Update usage chart
        usage_data = self.calculateUsageData(devices)
        self.usage_chart.update_data(usage_data)
        
        # Update distribution chart
        distribution_data = self.calculateDistributionData(devices)
        self.distribution_chart.update_data(distribution_data)
        
        # Update performance chart
        performance_data = self.calculatePerformanceData(devices, loans)
        self.performance_chart.update_data(performance_data)

    def updateActivityList(self, loans, supervisors):
        self.activity_list.clear()
        
        recent_activities = self.getRecentActivities(loans, supervisors)
        for activity in recent_activities:
            self.activity_list.add_activity(
                activity['title'],
                activity['description'],
                activity['time'],
                activity['status'],
                activity.get('icon')
            )

    def updateAlerts(self, devices, loans):
        self.alerts_list.clear()
        
        alerts = self.generateAlerts(devices, loans)
        for alert in alerts:
            self.alerts_list.add_activity(
                alert['title'],
                alert['description'],
                alert['time'],
                'warning',
                '⚠️'
            )

    def showLoadingState(self, loading):
        if loading:
            self.progress_bar.setRange(0, 0)
            self.progress_bar.show()
            self.status_label.setText("Loading data...")
        else:
            self.progress_bar.hide()

    def showMessage(self, title, message, level="info"):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        
        if level == "error":
            msg.setIcon(QMessageBox.Icon.Critical)
        elif level == "warning":
            msg.setIcon(QMessageBox.Icon.Warning)
        else:
            msg.setIcon(QMessageBox.Icon.Information)
        
        msg.exec()

    def calculateUsageData(self, devices):
        # Calculate usage trends over time
        now = datetime.now()
        usage_data = {}
        
        # Calculate device usage over the last 7 days
        for i in range(7):
            date = now - timedelta(days=i)
            active_count = len([d for d in devices if d['estado'] == 'en_uso'])
            available_count = len([d for d in devices if d['estado'] == 'disponible'])
            maintenance_count = len([d for d in devices if d['estado'] == 'mantenimiento'])
            
            usage_data[f'Activos'] = usage_data.get('Activos', []) + [(i, active_count)]
            usage_data[f'Disponibles'] = usage_data.get('Disponibles', []) + [(i, available_count)]
            usage_data[f'Mantenimiento'] = usage_data.get('Mantenimiento', []) + [(i, maintenance_count)]
        
        return usage_data

    def calculateDistributionData(self, devices):
        # Calculate device distribution by category
        categories = {}
        for device in devices:
            category = device.get('categoria', 'Other')
            categories[category] = categories.get(category, 0) + 1
        
        return [(cat, count) for cat, count in categories.items()]

    def calculatePerformanceData(self, devices, loans):
        # Calculate real performance metrics from database data
        total_devices = len(devices)
        if total_devices == 0:
            return {}

        # Calculate device utilization
        devices_in_use = len([d for d in devices if d['estado'] == 'en_uso'])
        utilization_rate = (devices_in_use / total_devices) * 100

        # Calculate device availability
        available_devices = len([d for d in devices if d['estado'] == 'disponible'])
        availability_rate = (available_devices / total_devices) * 100

        # Calculate maintenance rate
        devices_in_maintenance = len([d for d in devices if d['estado'] == 'mantenimiento'])
        maintenance_rate = (devices_in_maintenance / total_devices) * 100

        performance_data = {
            'Utilización': [float(utilization_rate)],
            'Disponibilidad': [float(availability_rate)],
            'Mantenimiento': [float(maintenance_rate)]
        }
        
        return performance_data

    def getRecentActivities(self, loans, supervisors):
        activities = []
        
        for loan in loans[:5]:  # Get 5 most recent loans
            supervisor = next((s for s in supervisors if s['id'] == loan['supervisor_id']), None)
            
            activities.append({
                'title': f"Device Loan",
                'description': f"Device {loan['maquina_id']} loaned to {supervisor['nombre'] if supervisor else 'Unknown'}",
                'time': loan['fecha_prestamo'].strftime('%Y-%m-%d %H:%M'),
                'status': 'info',
                'icon': '📱'
            })
        
        return activities

    def generateAlerts(self, devices, loans):
        alerts = []
        
        # Check for overdue loans
        for loan in loans:
            if loan['fecha_devolucion'] is None:
                days_loaned = (datetime.now() - loan['fecha_prestamo']).days
                if days_loaned > 7:
                    alerts.append({
                        'title': 'Overdue Device',
                        'description': f"Device {loan['maquina_id']} has been loaned for {days_loaned} days",
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'status': 'warning'
                    })
        
        # Check for inactive devices
        inactive_devices = [d for d in devices if d['estado'] == 'inactive']
        if inactive_devices:
            alerts.append({
                'title': 'Inactive Devices',
                'description': f"Found {len(inactive_devices)} inactive devices",
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'status': 'warning'
            })
        
        return alerts