from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem

import color_palette
from client.models.messages import Message


class MessageItemWidget(QListWidgetItem):
    def __init__(self, message: Message, from_peer_id: str, from_nickname: str, service: bool = False, previous_peer_id: str = None):
        super().__init__()
        self.message = message
        self.service = service
        self.from_peer_id = from_peer_id
        self.from_nickname = from_nickname
        self.previous_peer_id = previous_peer_id
        self.init_ui()

    def init_ui(self):
        self.setText(self.get_text())
        self.setBackground(QColor(color_palette.primary if self.message.mine else color_palette.primary_dark))
        alignment = Qt.AlignCenter
        if not self.service:
            alignment = Qt.AlignRight if self.message.mine else Qt.AlignLeft
        self.setTextAlignment(alignment)
        self.setForeground(QColor("#DDD") if self.service else QColor("#FFF"))

    def get_text(self):
        text = ""
        if self.from_peer_id != self.previous_peer_id:
            text += self.from_peer_id
            text += f"({self.from_nickname})\n" if self.from_nickname else "\n"

        text += self.message.text
        return text
