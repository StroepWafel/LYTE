# =============================================================================
# MODERATION WINDOWS - Banned/Whitelisted users and videos, Queue history
# =============================================================================

import logging
import threading
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton,
    QHBoxLayout, QLabel
)
from helpers.moderation_helpers import (
    save_banned_users, save_banned_ids, save_whitelisted_users, save_whitelisted_ids
)
from helpers.youtube_helpers import fetch_channel_name, get_video_name_fromID


def _extract_id(s: str) -> str:
    """Extract ID from 'Name (ID)' format."""
    return s.split("(")[-1].strip(")")


def _add_with_async_fetch(item_id: str, item_list: list, save_func, refresh_callback, fetch_name_func):
    """refresh_callback should be thread-safe (e.g. emit a Qt signal)."""
    if not item_id or any(u["id"] == item_id for u in item_list):
        return
    item_list.append({"id": item_id, "name": "Loading..."})
    save_func(item_list)
    refresh_callback()

    def fetch():
        try:
            name = fetch_name_func(item_id)
            for u in item_list:
                if u["id"] == item_id:
                    u["name"] = name
                    break
            save_func(item_list)
            refresh_callback()  # Runs in worker thread - callback must emit signal for GUI update
        except Exception as e:
            logging.error(f"Error fetching name: {e}")

    threading.Thread(target=fetch, daemon=True).start()


class BannedUsersWindow(QDialog):
    def __init__(self, main):
        super().__init__(main.GUI_MAIN_WINDOW_REF[0] if main.GUI_MAIN_WINDOW_REF else None)
        self.main = main
        self.setWindowTitle("Banned Users")
        self.setMinimumSize(400, 400)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Manage Banned Users"))

        self.list_widget = QListWidget()
        self._refresh_list()
        layout.addWidget(self.list_widget)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Add User ID")
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Ban User")
        add_btn.clicked.connect(self._ban)
        un_btn = QPushButton("Unban Selected")
        un_btn.clicked.connect(self._unban)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(un_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        if hasattr(self.main, 'GUI_BRIDGE') and self.main.GUI_BRIDGE:
            self.main.GUI_BRIDGE.refresh_list.connect(self._on_refresh_signal)

    def _on_refresh_signal(self, list_id: str, items: list):
        if list_id == "banned_users_list":
            self.list_widget.clear()
            self.list_widget.addItems(items)

    def _refresh_list(self):
        items = [f"{u['name']} ({u['id']})" for u in self.main.BANNED_USERS]
        self.list_widget.clear()
        self.list_widget.addItems(items)

    def _emit_refresh(self):
        """Thread-safe refresh - emits signal for GUI update."""
        if hasattr(self.main, 'GUI_BRIDGE') and self.main.GUI_BRIDGE:
            self.main.GUI_BRIDGE.refresh_list.emit("banned_users_list", [f"{u['name']} ({u['id']})" for u in self.main.BANNED_USERS])

    def _ban(self):
        uid = self.input.text().strip()
        _add_with_async_fetch(
            uid, self.main.BANNED_USERS,
            lambda lst: save_banned_users(lst, self.main.BANNED_USERS_PATH),
            self._emit_refresh,
            fetch_channel_name
        )
        self.input.clear()

    def _unban(self):
        item = self.list_widget.currentItem()
        if item:
            uid = _extract_id(item.text())
            self.main.BANNED_USERS[:] = [u for u in self.main.BANNED_USERS if u["id"] != uid]
            save_banned_users(self.main.BANNED_USERS, self.main.BANNED_USERS_PATH)
            self._refresh_list()


class BannedVideosWindow(QDialog):
    def __init__(self, main):
        super().__init__(main.GUI_MAIN_WINDOW_REF[0] if main.GUI_MAIN_WINDOW_REF else None)
        self.main = main
        self.setWindowTitle("Banned Videos")
        self.setMinimumSize(400, 400)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Manage Banned Videos"))

        self.list_widget = QListWidget()
        self._refresh_list()
        layout.addWidget(self.list_widget)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Add Video ID")
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Ban Video")
        add_btn.clicked.connect(self._ban)
        un_btn = QPushButton("Unban Selected")
        un_btn.clicked.connect(self._unban)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(un_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        if hasattr(self.main, 'GUI_BRIDGE') and self.main.GUI_BRIDGE:
            self.main.GUI_BRIDGE.refresh_list.connect(self._on_refresh_signal)

    def _on_refresh_signal(self, list_id: str, items: list):
        if list_id == "banned_ids_list":
            self.list_widget.clear()
            self.list_widget.addItems(items)

    def _refresh_list(self):
        self.list_widget.clear()
        self.list_widget.addItems([f"{u['name']} ({u['id']})" for u in self.main.BANNED_IDS])

    def _emit_refresh(self):
        if hasattr(self.main, 'GUI_BRIDGE') and self.main.GUI_BRIDGE:
            self.main.GUI_BRIDGE.refresh_list.emit("banned_ids_list", [f"{u['name']} ({u['id']})" for u in self.main.BANNED_IDS])

    def _ban(self):
        vid = self.input.text().strip()
        _add_with_async_fetch(
            vid, self.main.BANNED_IDS,
            lambda lst: save_banned_ids(lst, self.main.BANNED_IDS_PATH),
            self._emit_refresh,
            get_video_name_fromID
        )
        self.input.clear()

    def _unban(self):
        item = self.list_widget.currentItem()
        if item:
            vid = _extract_id(item.text())
            self.main.BANNED_IDS[:] = [u for u in self.main.BANNED_IDS if u["id"] != vid]
            save_banned_ids(self.main.BANNED_IDS, self.main.BANNED_IDS_PATH)
            self._refresh_list()


class WhitelistedUsersWindow(QDialog):
    def __init__(self, main):
        super().__init__(main.GUI_MAIN_WINDOW_REF[0] if main.GUI_MAIN_WINDOW_REF else None)
        self.main = main
        self.setWindowTitle("Whitelisted Users")
        self.setMinimumSize(400, 400)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Manage Whitelisted Users"))

        self.list_widget = QListWidget()
        self._refresh_list()
        layout.addWidget(self.list_widget)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Add User ID")
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Whitelist User")
        add_btn.clicked.connect(self._add)
        un_btn = QPushButton("Un-Whitelist Selected")
        un_btn.clicked.connect(self._remove)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(un_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        if hasattr(self.main, 'GUI_BRIDGE') and self.main.GUI_BRIDGE:
            self.main.GUI_BRIDGE.refresh_list.connect(self._on_refresh_signal)

    def _on_refresh_signal(self, list_id: str, items: list):
        if list_id == "whitelisted_users_list":
            self.list_widget.clear()
            self.list_widget.addItems(items)

    def _refresh_list(self):
        self.list_widget.clear()
        self.list_widget.addItems([f"{u['name']} ({u['id']})" for u in self.main.WHITELISTED_USERS])

    def _emit_refresh(self):
        if hasattr(self.main, 'GUI_BRIDGE') and self.main.GUI_BRIDGE:
            self.main.GUI_BRIDGE.refresh_list.emit("whitelisted_users_list", [f"{u['name']} ({u['id']})" for u in self.main.WHITELISTED_USERS])

    def _add(self):
        uid = self.input.text().strip()
        _add_with_async_fetch(
            uid, self.main.WHITELISTED_USERS,
            lambda lst: save_whitelisted_users(lst, self.main.WHITELISTED_USERS_PATH),
            self._emit_refresh,
            fetch_channel_name
        )
        self.input.clear()

    def _remove(self):
        item = self.list_widget.currentItem()
        if item:
            uid = _extract_id(item.text())
            self.main.WHITELISTED_USERS[:] = [u for u in self.main.WHITELISTED_USERS if u["id"] != uid]
            save_whitelisted_users(self.main.WHITELISTED_USERS, self.main.WHITELISTED_USERS_PATH)
            self._refresh_list()


class WhitelistedVideosWindow(QDialog):
    def __init__(self, main):
        super().__init__(main.GUI_MAIN_WINDOW_REF[0] if main.GUI_MAIN_WINDOW_REF else None)
        self.main = main
        self.setWindowTitle("Whitelisted Videos")
        self.setMinimumSize(400, 400)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Manage Whitelisted Videos"))

        self.list_widget = QListWidget()
        self._refresh_list()
        layout.addWidget(self.list_widget)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Add Video ID")
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Whitelist Video")
        add_btn.clicked.connect(self._add)
        un_btn = QPushButton("Un-Whitelist Selected")
        un_btn.clicked.connect(self._remove)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(un_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        if hasattr(self.main, 'GUI_BRIDGE') and self.main.GUI_BRIDGE:
            self.main.GUI_BRIDGE.refresh_list.connect(self._on_refresh_signal)

    def _on_refresh_signal(self, list_id: str, items: list):
        if list_id == "whitelisted_ids_list":
            self.list_widget.clear()
            self.list_widget.addItems(items)

    def _refresh_list(self):
        self.list_widget.clear()
        self.list_widget.addItems([f"{u['name']} ({u['id']})" for u in self.main.WHITELISTED_IDS])

    def _emit_refresh(self):
        if hasattr(self.main, 'GUI_BRIDGE') and self.main.GUI_BRIDGE:
            self.main.GUI_BRIDGE.refresh_list.emit("whitelisted_ids_list", [f"{u['name']} ({u['id']})" for u in self.main.WHITELISTED_IDS])

    def _add(self):
        vid = self.input.text().strip()
        _add_with_async_fetch(
            vid, self.main.WHITELISTED_IDS,
            lambda lst: save_whitelisted_ids(lst, self.main.WHITELISTED_IDS_PATH),
            self._emit_refresh,
            get_video_name_fromID
        )
        self.input.clear()

    def _remove(self):
        item = self.list_widget.currentItem()
        if item:
            vid = _extract_id(item.text())
            self.main.WHITELISTED_IDS[:] = [u for u in self.main.WHITELISTED_IDS if u["id"] != vid]
            save_whitelisted_ids(self.main.WHITELISTED_IDS, self.main.WHITELISTED_IDS_PATH)
            self._refresh_list()


class QueueHistoryWindow(QDialog):
    def __init__(self, main):
        super().__init__(main.GUI_MAIN_WINDOW_REF[0] if main.GUI_MAIN_WINDOW_REF else None)
        self.main = main
        self.setWindowTitle("Queue History")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Queue History"))
        layout.addWidget(QLabel("Past queued songs (resets on app restart)"))

        self.list_widget = QListWidget()
        self._refresh_list()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        ban_song_btn = QPushButton("Ban Selected Song")
        ban_song_btn.clicked.connect(self._ban_song)
        ban_user_btn = QPushButton("Ban Selected User")
        ban_user_btn.clicked.connect(self._ban_user)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ban_song_btn)
        btn_layout.addWidget(ban_user_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        if hasattr(self.main, 'GUI_BRIDGE') and self.main.GUI_BRIDGE:
            self.main.GUI_BRIDGE.refresh_list.connect(self._on_refresh_signal)

    def _on_refresh_signal(self, list_id: str, items: list):
        if list_id == "queue_history_list":
            self.list_widget.clear()
            self.list_widget.addItems(items)

    def _refresh_list(self):
        self.list_widget.clear()
        items = [
            f"{e['song_title']} - Requested by {e['username']} ({e['user_id']}) [{e['song_id']}]"
            for e in self.main.QUEUE_HISTORY
        ]
        self.list_widget.addItems(items)

    def _extract_info(self):
        item = self.list_widget.currentItem()
        if not item:
            return None
        return self.main.extract_queue_item_info(item.text())

    def _ban_song(self):
        info = self._extract_info()
        if info and info.get("song_id"):
            song_id = info["song_id"]
            song_title = info["song_title"]
            if not any(song_id == x["id"] for x in self.main.BANNED_IDS):
                self.main.BANNED_IDS.append({"id": song_id, "name": song_title})
                save_banned_ids(self.main.BANNED_IDS, self.main.BANNED_IDS_PATH)
                logging.info(f"Banned song '{song_title}' ({song_id})")
            self._refresh_list()

    def _ban_user(self):
        info = self._extract_info()
        if info and info.get("user_id"):
            user_id = info["user_id"]
            username = info["username"]
            if not any(user_id == x["id"] for x in self.main.BANNED_USERS):
                self.main.BANNED_USERS.append({"id": user_id, "name": username})
                save_banned_users(self.main.BANNED_USERS, self.main.BANNED_USERS_PATH)
                logging.info(f"Banned user '{username}' ({user_id})")
            self._refresh_list()
