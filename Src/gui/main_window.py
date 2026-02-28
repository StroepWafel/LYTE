# =============================================================================
# MAIN WINDOW - Control panel with playback, volume, progress, console
# =============================================================================

import logging
import webbrowser
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QPlainTextEdit, QMenuBar,
    QMessageBox
)
from PySide6.QtCore import Qt


class GuiLogger(logging.Handler):
    """Logging handler that appends to the console via signal (thread-safe)."""

    def __init__(self, bridge):
        super().__init__()
        self.bridge = bridge

    def emit(self, record):
        try:
            msg = self.format(record)
            if self.bridge:
                self.bridge.set_console_text.emit(msg)
        except Exception:
            pass


class MainWindow(QMainWindow):
    def __init__(self, bridge, main_module):
        super().__init__()
        self.bridge = bridge
        self.main = main_module
        self.setWindowTitle("LYTE Control Panel")
        self.setMinimumSize(700, 380)
        self.resize(1330, 750)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Menu bar
        self._create_menu()

        # Update notification (hidden initially)
        self.update_label = QLabel()
        self.update_label.setStyleSheet("color: #ffc864;")
        self.update_label.hide()
        layout.addWidget(self.update_label)

        # Now Playing
        self.now_playing_label = QLabel("Now Playing: Nothing")
        layout.addWidget(self.now_playing_label)

        # Playback controls
        ctrl_layout = QHBoxLayout()
        self.play_btn = QPushButton("Play / Pause")
        self.play_btn.clicked.connect(lambda: self.main.player.pause())
        self.play_btn.setToolTip("Play/Pause the current song")
        ctrl_layout.addWidget(self.play_btn)

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self._on_prev)
        self.prev_btn.setToolTip("Skip to the previous song")
        ctrl_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self._on_next)
        self.next_btn.setToolTip("Skip to the next song")
        ctrl_layout.addWidget(self.next_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.main.update_now_playing)
        self.refresh_btn.setToolTip("Refresh the song info")
        ctrl_layout.addWidget(self.refresh_btn)

        layout.addLayout(ctrl_layout)

        # Volume
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Volume"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.main.Settings.VOLUME)
        self.volume_slider.valueChanged.connect(self._on_volume)
        self.volume_slider.setMinimumWidth(400)
        vol_layout.addWidget(self.volume_slider)
        layout.addLayout(vol_layout)

        # Song progress
        prog_layout = QHBoxLayout()
        prog_layout.addWidget(QLabel("Song Progress"))
        self.song_slider = QSlider(Qt.Orientation.Horizontal)
        self.song_slider.setRange(0, 1000)  # Use 0-1000 for precision
        self.song_slider.setValue(0)
        self.song_slider.sliderMoved.connect(self._on_song_slider)
        self.song_slider.setMinimumWidth(400)
        self._ignore_slider = False
        prog_layout.addWidget(self.song_slider)
        self.song_time_label = QLabel("00:00 / 00:00")
        prog_layout.addWidget(self.song_time_label)
        layout.addLayout(prog_layout)

        # Console
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(200)
        self.console.setToolTip("Log messages and application status")
        layout.addWidget(self.console)

        # Set up GUI logger (uses signal for thread-safe updates)
        gui_handler = GuiLogger(bridge)
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)

        # Connect bridge signals
        bridge.update_now_playing.connect(self._on_update_now_playing)
        bridge.update_slider.connect(self._on_update_slider)
        bridge.update_time_text.connect(self.song_time_label.setText)
        bridge.refresh_list.connect(self._on_refresh_list)
        bridge.show_download_ui.connect(self._on_show_download_ui)
        bridge.hide_update_ui.connect(self._on_hide_update_ui)
        bridge.set_console_text.connect(self._on_append_console)
        bridge.request_theme_reload.connect(self._on_request_theme_reload)

    def _on_prev(self):
        self.main.set_user_initiated_skip()
        self.main.player.previous()
        self.main.update_now_playing()

    def _on_next(self):
        self.main.set_user_initiated_skip()
        self.main.player.next()
        self.main.update_now_playing()

    def _on_volume(self, value):
        self.main.Settings.VOLUME = value
        if self.main.player.get_media_player():
            self.main.player.get_media_player().audio_set_volume(value)
        self.main.save_config_to_file()

    def _on_song_slider(self, value):
        length = self.main.get_song_length()
        if length:
            pos_ms = int((value / 1000.0) * length * 1000)
            self.main.player.get_media_player().set_time(pos_ms)
            self.main.last_user_seek_time = self.main.current_time()

    def _on_update_slider(self, progress: float):
        if not self._ignore_slider:
            self._ignore_slider = True
            self.song_slider.setValue(int(progress * 1000))
            self._ignore_slider = False

    def _on_update_now_playing(self, text: str):
        self.now_playing_label.setText(text)

    def _on_refresh_list(self, list_id: str, items: list):
        # Handled by modal windows - they connect to refresh_list with their list_id
        pass

    def _on_show_download_ui(self, version: str):
        self.update_label.setText(f"Update Available: v{version} (Current: v{self.main.CURRENT_VERSION})")
        self.update_label.show()
        if hasattr(self, 'update_details_action'):
            self.update_details_action.setEnabled(True)

    def _on_hide_update_ui(self):
        self.update_label.hide()

    def _on_append_console(self, msg: str):
        """Thread-safe: append log line to console (slot runs on GUI thread)."""
        cur = self.console.toPlainText()
        lines = cur.splitlines()
        lines.append(msg)
        if len(lines) > 100:
            lines = lines[-100:]
        self.console.setPlainText("\n".join(lines))

    def _on_request_theme_reload(self):
        """Theme file changed; reload themes on GUI thread."""
        logging.info("Theme file change detected, reloading...")
        self.main.reload_themes()
        logging.info("Themes reloaded automatically")

    def _create_menu(self):
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Reload Config", self._reload_config).setToolTip("Reload configuration from file")
        file_menu.addAction("Settings", self._show_settings).setToolTip("Manage general settings")
        file_menu.addAction("Quit", self.main.quit_program).setToolTip("Exit the application")

        # View
        view_menu = menubar.addMenu("View")
        self.theme_menu = view_menu.addMenu("Theme")
        for display_name in self.main.get_theme_dropdown_items():
            action = self.theme_menu.addAction(display_name, lambda dn=display_name: self._select_theme(dn))
            action.setCheckable(True)
            if display_name == self.main.get_available_themes().get(self.main.get_current_theme(), {}).get("display_name", ""):
                action.setChecked(True)
        view_menu.addAction("Open Themes Folder", lambda: self.main.show_folder(self.main.THEMES_FOLDER))
        view_menu.addAction("Reload themes", self.main.reload_themes)

        # Moderation
        mod_menu = menubar.addMenu("Moderation")
        mod_menu.addAction("View Queue History", self._show_queue_history)
        mod_menu.addAction("Manage Banned Users", self._show_banned_users)
        mod_menu.addAction("Manage Banned Videos", self._show_banned_videos)
        mod_menu.addAction("Manage Whitelisted Users", self._show_whitelisted_users)
        mod_menu.addAction("Manage Whitelisted Videos", self._show_whitelisted_videos)

        # Help
        help_menu = menubar.addMenu("Help")
        help_menu.addAction(f"Version: {self.main.CURRENT_VERSION}").setEnabled(False)
        help_menu.addSeparator()
        help_menu.addAction("Check for Updates", self.main.check_for_updates_wrapper)
        self.update_details_action = help_menu.addAction("View Update Details...", self._show_update_details)
        self.update_details_action.setEnabled(False)
        help_menu.addAction("Open GitHub Issues", lambda: webbrowser.open("https://github.com/StroepWafel/LYTE/issues"))
        help_menu.addAction("Open General Documentation", lambda: webbrowser.open("https://www.stroepwafel.au/LYTE/documentation"))
        help_menu.addAction("Open Theme Documentation", lambda: webbrowser.open("https://www.stroepwafel.au/LYTE/documentation/theme-documentation"))

    def _select_theme(self, display_name: str):
        theme_name = self.main.get_theme_name_from_display(display_name)
        self.main.select_theme_by_name(theme_name)
        for a in self.theme_menu.actions():
            if a.isCheckable():
                a.setChecked(a.text() == display_name)

    def _reload_config(self):
        self.main.load_config()

    def _show_settings(self):
        from .settings_window import SettingsWindow
        self.main.load_config()
        dlg = SettingsWindow(self.main)
        dlg.exec()

    def _show_queue_history(self):
        from .moderation_windows import QueueHistoryWindow
        self.main.refresh_queue_history_list()
        dlg = QueueHistoryWindow(self.main)
        dlg.exec()

    def _show_banned_users(self):
        from .moderation_windows import BannedUsersWindow
        self.main.load_banned_users_wrapper()
        self.main.refresh_banned_users_list()
        dlg = BannedUsersWindow(self.main)
        dlg.exec()

    def _show_banned_videos(self):
        from .moderation_windows import BannedVideosWindow
        self.main.load_banned_ids_wrapper()
        self.main.refresh_banned_ids_list()
        dlg = BannedVideosWindow(self.main)
        dlg.exec()

    def _show_whitelisted_users(self):
        from .moderation_windows import WhitelistedUsersWindow
        self.main.load_whitelisted_users_wrapper()
        self.main.refresh_whitelisted_users_list()
        dlg = WhitelistedUsersWindow(self.main)
        dlg.exec()

    def _show_whitelisted_videos(self):
        from .moderation_windows import WhitelistedVideosWindow
        self.main.load_whitelisted_ids_wrapper()
        self.main.refresh_whitelisted_ids_list()
        dlg = WhitelistedVideosWindow(self.main)
        dlg.exec()

    def _show_update_details(self):
        from .update_window import UpdateDetailsWindow
        dlg = UpdateDetailsWindow(self.main)
        dlg.exec()
