import json
from PyQt6.QtGui import QColor, QFont, QFontDatabase

CLOUD_THEME = {
    "colors": {
        "primary": "#0078d7",        # Azure Blue
        "primary_dark": "#005a9e",    # Darker Azure Blue
        "secondary": "#232f3e",       # AWS Dark Blue
        "accent": "#ff9900",          # AWS Orange
        "hover": "#2d3033",          # Hover state color
        "success": "#00bc78",         # Modern Green
        "error": "#dc3545",
        "warning": "#ffb900",          # Bootstrap Red
        "info": "#0dcaf0",            # Info Blue
        "background": "#1a1d21",     # GitHub Dark
        "text_light": "#f0f6fc",    # Same as text.primary
        "card": "#2d2d2d",
        "surface": "#24292e",        # GitHub Dark Surface
        "text": {
            "primary": "#f0f6fc",    # GitHub Text
            "secondary": "#8b949e"   # GitHub Secondary
        },
        "border": "#30363d"        # GitHub Border Color
    },
    "typography": {
        "font_family": "'Segoe UI', 'SF Pro Text', system-ui",
        "font_sizes": {
            "h1": 24,
            "h2": 20,
            "body": 14,
            "caption": 12
        },
        "font_weights": {
            "light": 300,
            "regular": 400,
            "medium": 500,
            "bold": 700
        }
    },
    "spacing": {
        "unit": 8,
        "section_padding": "24px",
        "element_spacing": "12px"
    },
    "elevation": {
        "low": "0 2px 4px rgba(0,0,0,0.12)",
        "medium": "0 4px 8px rgba(0,0,0,0.16)",
        "high": "0 8px 16px rgba(0,0,0,0.20)"
    },
    "animations": {
        "short": "200ms",
        "medium": "300ms",
        "long": "400ms",
        "easing": "cubic-bezier(0.4, 0, 0.2, 1)"
    },
    "components": {
        "card": {
            "border_radius": "8px"
        },
        "button": {
            "border_radius": "4px",
            "padding": "8px 16px",
            "hover_effect": "translateY(-1px)"
        },
        "card": {
            "border_radius": "8px",
            "padding": "16px",
            "border": "1px solid rgba(255,255,255,0.12)"
        }
    }
}

CLOUD_STYLE = f"""
/* Base Styles */
QWidget {{
    background-color: {CLOUD_THEME['colors']['background']};
    color: {CLOUD_THEME['colors']['text']['primary']};
    font-family: {CLOUD_THEME['typography']['font_family']};
    font-size: {CLOUD_THEME['typography']['font_sizes']['body']}px;
}}

/* Interactive Elements */
QPushButton {{
    background-color: {CLOUD_THEME['colors']['primary']};
    color: white;
    border-radius: {CLOUD_THEME['components']['button']['border_radius']};
    padding: {CLOUD_THEME['components']['button']['padding']};
    font-weight: {CLOUD_THEME['typography']['font_weights']['medium']};
    transition: all {CLOUD_THEME['animations']['medium']} {CLOUD_THEME['animations']['easing']};
}}

QPushButton:hover {{
    background-color: {CLOUD_THEME['colors']['secondary']};
    transform: {CLOUD_THEME['components']['button']['hover_effect']};
    box-shadow: {CLOUD_THEME['elevation']['medium']};
}}

/* Data Visualization */
QTableView, QTreeView {{
    background: {CLOUD_THEME['colors']['surface']};
    border-radius: {CLOUD_THEME['components']['card']['border_radius']};
    alternate-background-color: rgba(255,255,255,0.05);
}}

/* Form Elements */
QLineEdit, QComboBox {{
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.24);
    border-radius: 4px;
    padding: 8px;
}}

/* Custom Scrollbars */
QScrollBar:vertical {{
    background: {CLOUD_THEME['colors']['surface']};
    width: 10px;
}}

QScrollBar::handle:vertical {{
    background: {CLOUD_THEME['colors']['primary']};
    border-radius: 4px;
}}
"""

def load_fonts():
    QFontDatabase.addApplicationFont(":/fonts/SegoeUI.ttf")
    QFontDatabase.addApplicationFont(":/fonts/SF-Pro-Text-Regular.otf")

APP_FONT = QFont(CLOUD_THEME['typography']['font_family'], 
                CLOUD_THEME['typography']['font_sizes']['body'], 
                QFont.Weight.Normal)

def generate_stylesheet(component: str) -> str:
    return json.dumps(CLOUD_THEME['components'].get(component, {}), indent=4)