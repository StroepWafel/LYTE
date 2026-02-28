# =============================================================================
# THEME ENGINE - Converts JSON themes to Qt stylesheets (QSS)
# =============================================================================

import logging
from typing import Optional

# Theme color key to Qt/CSS mapping
_COLOR_KEYS = [
    "WindowBg", "FrameBg", "Button", "ButtonHovered", "ButtonActive",
    "Text", "SliderGrab", "SliderGrabActive", "Header", "ScrollbarBg",
    "ScrollbarGrab", "ScrollbarGrabHovered", "ScrollbarGrabActive",
    "CheckMark", "HeaderHovered", "HeaderActive", "Tab", "TabHovered",
    "TabActive", "TitleBg", "TitleBgActive", "TitleBgCollapsed",
    "MenuBarBg", "Border", "Separator", "PopupBg", "TextSelectedBg"
]


def _rgba_to_hex(rgba: list) -> str:
    """Convert [R, G, B, A] to #RRGGBB hex string (alpha ignored for CSS)."""
    if len(rgba) >= 3:
        r, g, b = int(rgba[0]), int(rgba[1]), int(rgba[2])
        return f"#{r:02x}{g:02x}{b:02x}"
    return "#000000"


def _rgba_to_rgba_css(rgba: list) -> str:
    """Convert [R, G, B, A] to rgba(R, G, B, A) CSS string."""
    if len(rgba) >= 4:
        return f"rgba({rgba[0]}, {rgba[1]}, {rgba[2]}, {rgba[3]/255:.2f})"
    if len(rgba) >= 3:
        return f"rgb({rgba[0]}, {rgba[1]}, {rgba[2]})"
    return "rgba(0, 0, 0, 1)"


def theme_data_to_qss(theme_data: dict) -> str:
    """
    Convert theme JSON data to Qt stylesheet string.
    
    Args:
        theme_data: Dict with 'colors' and 'styles' keys
        
    Returns:
        str: QSS string to apply to QApplication
    """
    colors = theme_data.get("colors", {})
    styles = theme_data.get("styles", {})
    
    # Build CSS variables
    bg = _rgba_to_hex(colors.get("WindowBg", [25, 25, 25, 255]))
    frame_bg = _rgba_to_hex(colors.get("FrameBg", [35, 35, 35, 255]))
    btn = _rgba_to_hex(colors.get("Button", [60, 70, 60, 255]))
    btn_hover = _rgba_to_hex(colors.get("ButtonHovered", [80, 120, 80, 255]))
    btn_active = _rgba_to_hex(colors.get("ButtonActive", [100, 150, 100, 255]))
    text = _rgba_to_hex(colors.get("Text", [220, 220, 220, 255]))
    slider_grab = _rgba_to_hex(colors.get("SliderGrab", [100, 150, 100, 255]))
    slider_active = _rgba_to_hex(colors.get("SliderGrabActive", [120, 180, 120, 255]))
    border = _rgba_to_hex(colors.get("Border", [70, 90, 70, 255]))
    menu_bg = _rgba_to_hex(colors.get("MenuBarBg", [30, 30, 30, 255]))
    popup_bg = _rgba_to_hex(colors.get("PopupBg", [35, 35, 35, 240]))
    
    rounding = styles.get("FrameRounding", 8)
    window_rounding = styles.get("WindowRounding", 12)
    
    qss = f"""
QWidget {{
    background-color: {bg};
    color: {text};
}}

QMainWindow, QDialog {{
    background-color: {bg};
}}

QMenuBar {{
    background-color: {menu_bg};
    color: {text};
}}

QMenuBar::item:selected {{
    background-color: {btn_hover};
}}

QMenu {{
    background-color: {popup_bg};
    color: {text};
}}

QMenu::item:selected {{
    background-color: {btn_hover};
}}

QPushButton {{
    background-color: {btn};
    color: {text};
    border: 1px solid {border};
    border-radius: {rounding}px;
    padding: 8px 16px;
}}

QPushButton:hover {{
    background-color: {btn_hover};
}}

QPushButton:pressed {{
    background-color: {btn_active};
}}

QPushButton:disabled {{
    background-color: {frame_bg};
    color: gray;
}}

QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QComboBox {{
    background-color: {frame_bg};
    color: {text};
    border: 1px solid {border};
    border-radius: {rounding}px;
    padding: 6px;
}}

QComboBox::drop-down {{
    background-color: {btn};
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {popup_bg};
    color: {text};
}}

QSlider::groove:horizontal {{
    background: {frame_bg};
    height: 8px;
    border-radius: 4px;
}}

QSlider::handle:horizontal {{
    background: {slider_grab};
    width: 16px;
    margin: -4px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {slider_active};
}}

QScrollBar:vertical {{
    background: {frame_bg};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background: {btn};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {btn_hover};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QListWidget {{
    background-color: {frame_bg};
    color: {text};
    border: 1px solid {border};
    border-radius: {rounding}px;
}}

QListWidget::item:selected {{
    background-color: {btn_hover};
}}

QListWidget::item:hover {{
    background-color: {btn};
}}

QCheckBox {{
    color: {text};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {border};
    background-color: {frame_bg};
}}

QCheckBox::indicator:checked {{
    background-color: {slider_grab};
}}

QGroupBox {{
    color: {text};
    border: 1px solid {border};
    border-radius: {rounding}px;
    margin-top: 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
}}

QToolTip {{
    background-color: {popup_bg};
    color: {text};
    border: 1px solid {border};
    border-radius: {rounding}px;
    padding: 6px;
}}
"""
    return qss


def get_theme_colors(theme_data: dict) -> dict:
    """Extract colors dict from theme data for custom widgets."""
    return theme_data.get("colors", {})


def get_theme_styles(theme_data: dict) -> dict:
    """Extract styles dict from theme data for custom widgets."""
    return theme_data.get("styles", {})


def apply_theme_to_app(app, theme_name: str, load_theme_from_file,
                       get_theme_type=None, load_qss_from_file=None) -> bool:
    """
    Apply a theme to a QApplication instance.
    Supports both JSON themes (converted to QSS) and raw .qss files.

    Args:
        app: QApplication instance
        theme_name: Theme identifier (e.g. "dark_theme" or "my_custom")
        load_theme_from_file: Function to load JSON theme data (from theme_helpers)
        get_theme_type: Optional function returning "json" or "qss"
        load_qss_from_file: Optional function to load raw QSS content

    Returns:
        bool: True if theme was applied successfully
    """
    try:
        # Lazy import to avoid circular deps
        if get_theme_type is None or load_qss_from_file is None:
            from helpers.theme_helpers import get_theme_type as _gtt, load_qss_from_file as _lqf
            get_theme_type = get_theme_type or _gtt
            load_qss_from_file = load_qss_from_file or _lqf

        theme_type = get_theme_type(theme_name)

        if theme_type == "qss":
            qss = load_qss_from_file(theme_name)
            if qss:
                app.setStyleSheet(qss)
                logging.info(f"Applied QSS theme: {theme_name}")
                return True
        else:
            theme_data = load_theme_from_file(theme_name)
            if theme_data:
                qss = theme_data_to_qss(theme_data)
                app.setStyleSheet(qss)
                logging.info(f"Applied theme: {theme_name}")
                return True

        logging.warning(f"Theme not found: {theme_name}")
        return False
    except Exception as e:
        logging.error(f"Error applying theme {theme_name}: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False
