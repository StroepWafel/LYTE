# =============================================================================
# CUSTOM WIDGETS - Styled PySide6 widgets for modern look
# =============================================================================

from PySide6.QtWidgets import QFrame, QPushButton


class Card(QFrame):
    """Rounded container for logical sections."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            Card {
                background-color: #2d2d2d;
                border: 1px solid #464646;
                border-radius: 8px;
                padding: 12px;
            }
        """)


class StyledButton(QPushButton):
    """Button with consistent modern styling (theme applied via QSS)."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
