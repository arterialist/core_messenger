from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem

import color_palette


class MessageItemWidget(QListWidgetItem):
    def __init__(self, my, text=None):
        super().__init__()
        self.init_ui(my, text)

    def init_ui(self, my, text):
        self.setText(text)
        self.setBackground(QColor(color_palette.primary if my else color_palette.primary_dark))
        self.setTextAlignment(Qt.AlignRight if my else Qt.AlignLeft)
        self.setForeground(QColor("#ffffff"))
