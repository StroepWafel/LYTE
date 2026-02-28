# =============================================================================
# UPDATE DETAILS WINDOW - Changelog and download options
# =============================================================================

import webbrowser
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPlainTextEdit, QHBoxLayout, QPushButton
)


class UpdateDetailsWindow(QDialog):
    def __init__(self, main):
        super().__init__(main.GUI_MAIN_WINDOW_REF[0] if main.GUI_MAIN_WINDOW_REF else None)
        self.main = main
        self.setWindowTitle("Update Details")
        self.setMinimumSize(600, 550)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Update Details"))

        self.title_label = QLabel()
        self.version_label = QLabel()
        layout.addWidget(self.title_label)
        layout.addWidget(self.version_label)

        layout.addWidget(QLabel("Changelog:"))
        self.body = QPlainTextEdit()
        self.body.setReadOnly(True)
        self.body.setMinimumHeight(330)
        layout.addWidget(self.body)

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open Release Page")
        open_btn.clicked.connect(self._open_release)
        dl_btn = QPushButton("Download Installer")
        dl_btn.clicked.connect(self.main.download_installer)
        run_btn = QPushButton("Run Installer")
        run_btn.clicked.connect(self._run_installer)
        ignore_btn = QPushButton("Ignore This Update")
        ignore_btn.clicked.connect(self._ignore)
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(dl_btn)
        btn_layout.addWidget(run_btn)
        btn_layout.addWidget(ignore_btn)
        layout.addLayout(btn_layout)

        self._populate()

    def _populate(self):
        details = self.main.LATEST_RELEASE_DETAILS
        self.title_label.setText(f"Release: {details.get('name', 'Latest Release')}")
        self.version_label.setText(f"Version: v{details.get('version', self.main.LATEST_VERSION)}")
        self.body.setPlainText(details.get('body', ''))

    def _open_release(self):
        url = self.main.LATEST_RELEASE_DETAILS.get("html_url", "https://github.com/StroepWafel/LYTE/releases/latest")
        webbrowser.open(url)

    def _run_installer(self):
        self.main.run_installer_wrapper()

    def _ignore(self):
        self.main.ignore_update_action()
