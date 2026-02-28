# =============================================================================
# CONFIG WINDOW - Initial configuration dialog
# =============================================================================

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QCheckBox,
    QComboBox, QPushButton, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt


def show_config_dialog(invalid_id: bool = False, not_live: bool = False) -> bool:
    """
    Show the initial config dialog. Blocks until user closes.
    
    Returns:
        True if user clicked "Save and Start", False if "Quit"
    """
    from .app import get_app
    from .theme_engine import apply_theme_to_app
    from helpers.theme_helpers import (
        create_default_theme_files, load_all_themes, get_theme_dropdown_items,
        get_theme_name_from_display, set_current_theme, get_current_theme,
        get_available_themes, load_theme_from_file
    )
    from settings import Settings

    app = get_app()

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

    apply_theme_to_app(app, get_current_theme(), load_theme_from_file)

    dialog = ConfigDialog(invalid_id, not_live)
    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted


class ConfigDialog(QDialog):
    def __init__(self, invalid_id: bool = False, not_live: bool = False, parent=None):
        super().__init__(parent)
        from settings import Settings

        self.setWindowTitle("Configure LYTE Settings")
        self.setFixedSize(500, 550)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.id_input = QLineEdit()
        self.id_input.setText(Settings.YOUTUBE_VIDEO_ID)
        self.id_input.setPlaceholderText("11 characters after watch?v=")
        self.id_input.setToolTip("The ID of your livestream")
        form.addRow("YouTube Livestream ID:", self.id_input)

        if invalid_id:
            lbl = QLabel("Invalid or inaccessible livestream ID")
            lbl.setStyleSheet("color: #ff6464")
            form.addRow(lbl)
        if not_live:
            lbl = QLabel("Video is not a livestream")
            lbl.setStyleSheet("color: #ff6464")
            form.addRow(lbl)

        self.prefix_input = QLineEdit()
        self.prefix_input.setText(Settings.PREFIX)
        form.addRow("Command Prefix:", self.prefix_input)

        self.queue_input = QLineEdit()
        self.queue_input.setText(Settings.QUEUE_COMMAND)
        form.addRow("Queue Command:", self.queue_input)

        self.rate_limit_input = QSpinBox()
        self.rate_limit_input.setRange(0, 999999)
        self.rate_limit_input.setValue(Settings.RATE_LIMIT_SECONDS)
        form.addRow("Rate Limit (seconds):", self.rate_limit_input)

        self.toast_checkbox = QCheckBox("Enable Toast Notifications")
        self.toast_checkbox.setChecked(Settings.TOAST_NOTIFICATIONS)
        form.addRow(self.toast_checkbox)

        self.allow_urls_checkbox = QCheckBox("Allow URL Requests")
        self.allow_urls_checkbox.setChecked(Settings.ALLOW_URLS)
        form.addRow(self.allow_urls_checkbox)

        self.require_membership_checkbox = QCheckBox("Require Membership to request")
        self.require_membership_checkbox.setChecked(Settings.REQUIRE_MEMBERSHIP)
        form.addRow(self.require_membership_checkbox)

        self.require_superchat_checkbox = QCheckBox("Require Superchat to request")
        self.require_superchat_checkbox.setChecked(Settings.REQUIRE_SUPERCHAT)
        form.addRow(self.require_superchat_checkbox)

        self.minimum_superchat_input = QSpinBox()
        self.minimum_superchat_input.setRange(0, 9999)
        self.minimum_superchat_input.setValue(Settings.MINIMUM_SUPERCHAT)
        form.addRow("Minimum Superchat (USD):", self.minimum_superchat_input)

        self.enforce_user_whitelist_checkbox = QCheckBox("Enforce User Whitelist")
        self.enforce_user_whitelist_checkbox.setChecked(Settings.ENFORCE_USER_WHITELIST)
        form.addRow(self.enforce_user_whitelist_checkbox)

        self.enforce_id_whitelist_checkbox = QCheckBox("Enforce Song Whitelist")
        self.enforce_id_whitelist_checkbox.setChecked(Settings.ENFORCE_ID_WHITELIST)
        form.addRow(self.enforce_id_whitelist_checkbox)

        self.autoremove_checkbox = QCheckBox("Automatically remove songs")
        self.autoremove_checkbox.setChecked(Settings.AUTOREMOVE_SONGS)
        form.addRow(self.autoremove_checkbox)

        self.song_finish_checkbox = QCheckBox("Notify When New Song Starts")
        self.song_finish_checkbox.setChecked(Settings.SONG_FINISH_NOTIFICATIONS)
        form.addRow(self.song_finish_checkbox)

        self.autoban_checkbox = QCheckBox("Autoban users")
        self.autoban_checkbox.setChecked(Settings.AUTOBAN_USERS)
        form.addRow(self.autoban_checkbox)

        from helpers.theme_helpers import (
            get_theme_dropdown_items, get_available_themes, get_current_theme
        )
        theme_items = get_theme_dropdown_items()
        self.theme_combo = QComboBox()
        if theme_items:
            self.theme_combo.addItems(theme_items)
            themes = get_available_themes()
            current = get_current_theme()
            current_display = themes.get(current, {}).get("display_name", theme_items[0])
            idx = self.theme_combo.findText(current_display)
            if idx >= 0:
                self.theme_combo.setCurrentIndex(idx)
        form.addRow("Theme:", self.theme_combo)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save and Start")
        save_btn.clicked.connect(self._save_and_start)
        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(self._quit)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(quit_btn)
        layout.addLayout(btn_layout)

    def _save_and_start(self):
        from settings import Settings
        from helpers.theme_helpers import get_theme_name_from_display, set_current_theme

        Settings.YOUTUBE_VIDEO_ID = self.id_input.text().strip()
        Settings.PREFIX = self.prefix_input.text().strip()
        Settings.QUEUE_COMMAND = self.queue_input.text().strip()
        Settings.RATE_LIMIT_SECONDS = self.rate_limit_input.value()
        Settings.TOAST_NOTIFICATIONS = self.toast_checkbox.isChecked()
        Settings.ALLOW_URLS = self.allow_urls_checkbox.isChecked()
        Settings.REQUIRE_MEMBERSHIP = self.require_membership_checkbox.isChecked()
        Settings.REQUIRE_SUPERCHAT = self.require_superchat_checkbox.isChecked()
        Settings.MINIMUM_SUPERCHAT = self.minimum_superchat_input.value()
        Settings.ENFORCE_USER_WHITELIST = self.enforce_user_whitelist_checkbox.isChecked()
        Settings.ENFORCE_ID_WHITELIST = self.enforce_id_whitelist_checkbox.isChecked()
        Settings.AUTOREMOVE_SONGS = self.autoremove_checkbox.isChecked()
        Settings.SONG_FINISH_NOTIFICATIONS = self.song_finish_checkbox.isChecked()
        Settings.AUTOBAN_USERS = self.autoban_checkbox.isChecked()

        display = self.theme_combo.currentText()
        if display:
            theme_name = get_theme_name_from_display(display)
            if theme_name:
                Settings.THEME = theme_name
                set_current_theme(theme_name)

        Settings.save()
        self.accept()

    def _quit(self):
        import sys
        main_mod = sys.modules.get('__main__')
        if main_mod and hasattr(main_mod, 'quit_program'):
            main_mod.quit_program()
        self.reject()
