from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QPushButton, QTextEdit, QFrame, QHBoxLayout

import color_palette
from callback.callbacks import send_button_clicked_callback


class MessageInputWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.send_button = QPushButton('Send')
        self.message_input = QTextEdit()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        palette = self.message_input.palette()
        palette.setColor(QPalette.Base, QColor(color_palette.primary_light))
        self.message_input.setPalette(palette)
        self.message_input.setTextColor(QColor('#ffffff'))
        self.message_input.setAutoFormatting(QTextEdit.AutoAll)

        self.send_button.setFixedWidth(50)
        p = self.send_button.palette()
        p.setColor(QPalette.Button, QColor(color_palette.primary_light))
        self.send_button.setPalette(p)
        self.send_button.clicked.connect(lambda: send_button_clicked_callback(self))
        self.send_button.setShortcut('Ctrl+Return')

        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
