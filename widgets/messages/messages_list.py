from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem

import color_palette
from client.models.messages import Message


class MessageItemWidget(QListWidgetItem):
    def __init__(self, message: Message, service: bool = False):
        super().__init__()
        self.message = message
        self.service = service
        self.init_ui()

    def init_ui(self):
        self.setText(self.message.text)
        self.setBackground(QColor(color_palette.primary if self.message.mine else color_palette.primary_dark))
        alignment = Qt.AlignCenter
        if not self.service:
            alignment = Qt.AlignRight if self.message.mine else Qt.AlignLeft
        self.setTextAlignment(alignment)
        self.setForeground(QColor("#DDD") if self.service else QColor("#FFF"))
