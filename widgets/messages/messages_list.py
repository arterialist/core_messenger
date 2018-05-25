from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem

import color_palette


class MessageItemWidget(QListWidgetItem):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.init_ui(message)

    def init_ui(self, message):
        self.setText(message.text)
        self.setBackground(QColor(color_palette.primary if message.mine else color_palette.primary_dark))
        self.setTextAlignment(Qt.AlignRight if message.mine else Qt.AlignLeft)
        self.setForeground(QColor("#ffffff"))
