# =============================================================================
# GUI LAUNCHER - Starts PySide6 GUI in dedicated thread
# =============================================================================

import logging
import threading


def launch_gui_thread() -> None:
    """
    Launch the PySide6 GUI in a dedicated daemon thread.
    The GUI runs independently; workers communicate via ThreadBridge signals.
    """
    def _run_gui():
        try:
            from .app import run_gui
            run_gui()
        except Exception as e:
            logging.error(f"GUI error: {e}")
            import traceback
            logging.error(traceback.format_exc())

    thread = threading.Thread(target=_run_gui, daemon=True)
    thread.start()
    logging.info("GUI thread started")
