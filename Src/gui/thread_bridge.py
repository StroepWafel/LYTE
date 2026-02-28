# =============================================================================
# THREAD BRIDGE - Qt signals for cross-thread GUI updates
# =============================================================================

from PySide6.QtCore import QObject, Signal


class ThreadBridge(QObject):
    """Signals for worker threads to update the GUI (slots run on GUI thread)."""

    update_slider = Signal(float)           # 0.0-1.0 progress
    update_time_text = Signal(str)          # "MM:SS / MM:SS"
    update_now_playing = Signal(str)        # "Now Playing: Title"
    refresh_list = Signal(str, list)         # list_id, items
    show_window = Signal(str, bool)         # window_tag, show
    enable_menu_item = Signal(str, bool)    # item_tag, enabled
    show_download_ui = Signal(str)           # latest_version
    set_console_text = Signal(str)           # append log line (thread-safe)
    hide_update_ui = Signal()                # hide update notification
    request_theme_reload = Signal()          # theme file changed, reload on GUI thread
