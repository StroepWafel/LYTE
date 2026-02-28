# =============================================================================
# SETTINGS WINDOW - General settings modal
# =============================================================================

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QCheckBox,
    QPushButton
)
from settings import Settings


class SettingsWindow(QDialog):
    def __init__(self, main_module):
        super().__init__(main_module.GUI_MAIN_WINDOW_REF[0] if main_module.GUI_MAIN_WINDOW_REF else None)
        self.main = main_module
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 400)

        layout = QVBoxLayout(self)
        form = QFormLayout()

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

        self.song_finish_checkbox = QCheckBox("Notify When New Song Starts")
        self.song_finish_checkbox.setChecked(Settings.SONG_FINISH_NOTIFICATIONS)
        form.addRow(self.song_finish_checkbox)

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

        self.autoban_checkbox = QCheckBox("Autoban users")
        self.autoban_checkbox.setChecked(Settings.AUTOBAN_USERS)
        form.addRow(self.autoban_checkbox)

        self.autoremove_checkbox = QCheckBox("Automatically remove songs")
        self.autoremove_checkbox.setChecked(Settings.AUTOREMOVE_SONGS)
        form.addRow(self.autoremove_checkbox)

        layout.addLayout(form)

        btn = QPushButton("Update Settings")
        btn.clicked.connect(self._save)
        layout.addWidget(btn)

    def _save(self):
        Settings.RATE_LIMIT_SECONDS = self.rate_limit_input.value()
        Settings.TOAST_NOTIFICATIONS = self.toast_checkbox.isChecked()
        Settings.PREFIX = self.prefix_input.text().strip()
        Settings.QUEUE_COMMAND = self.queue_input.text().strip()
        Settings.ALLOW_URLS = self.allow_urls_checkbox.isChecked()
        Settings.REQUIRE_MEMBERSHIP = self.require_membership_checkbox.isChecked()
        Settings.REQUIRE_SUPERCHAT = self.require_superchat_checkbox.isChecked()
        Settings.MINIMUM_SUPERCHAT = self.minimum_superchat_input.value()
        Settings.ENFORCE_USER_WHITELIST = self.enforce_user_whitelist_checkbox.isChecked()
        Settings.ENFORCE_ID_WHITELIST = self.enforce_id_whitelist_checkbox.isChecked()
        Settings.AUTOREMOVE_SONGS = self.autoremove_checkbox.isChecked()
        Settings.AUTOBAN_USERS = self.autoban_checkbox.isChecked()
        Settings.SONG_FINISH_NOTIFICATIONS = self.song_finish_checkbox.isChecked()
        Settings.save()
        self.accept()
