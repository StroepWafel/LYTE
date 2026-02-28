# =============================================================================
# APPLICATION - QApplication singleton and run entry point
# =============================================================================

from PySide6.QtWidgets import QApplication
from typing import Optional

_app: Optional[QApplication] = None


def get_app() -> QApplication:
    """Get or create the QApplication instance."""
    global _app
    if _app is None:
        _app = QApplication([])
    return _app


def run_gui(main_module=None):
    """Run the main GUI (called from main.py). Creates app, shows main window, runs exec."""
    import sys
    main_module = main_module or sys.modules.get('__main__')
    if not main_module:
        raise RuntimeError("run_gui requires main module")

    from .main_window import MainWindow
    from .thread_bridge import ThreadBridge
    from helpers.theme_helpers import (
        load_theme_from_file, get_current_theme, apply_theme,
        register_theme_applier, load_all_themes, create_default_theme_files,
        get_available_themes, set_current_theme
    )
    from gui.theme_engine import apply_theme_to_app

    app = get_app()

    # Theme applier: apply to QApplication
    def _apply(theme_name: str):
        apply_theme_to_app(app, theme_name, load_theme_from_file)

    register_theme_applier(_apply)

    try:
        create_default_theme_files()
        load_all_themes()
    except Exception as e:
        import logging
        logging.error(f"Error loading themes: {e}")

    themes = get_available_themes()
    current = get_current_theme()
    if not themes or current not in themes:
        if themes:
            set_current_theme(list(themes.keys())[0])
        else:
            set_current_theme("dark_theme")

    _apply(get_current_theme())

    # Create thread bridge and main window
    bridge = ThreadBridge()
    main_module.GUI_BRIDGE = bridge  # Allow main.py workers to access it
    main_module.GUI_MAIN_WINDOW_REF = []  # Will hold ref to MainWindow

    mw = MainWindow(bridge, main_module)
    main_module.GUI_MAIN_WINDOW_REF.append(mw)

    mw.show()

    # Run theme file watcher (needs main window to exist)
    main_module.start_theme_file_watcher()

    app.exec()
