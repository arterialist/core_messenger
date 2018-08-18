import platform

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

import color_palette
from callback.callbacks import new_dialog_click_callback, new_chat_click_callback


class DialogsListHeadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.new_dialog_button = QPushButton(self)
        self.new_chat_button = QPushButton(self)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        dialogs_label = QLabel(self)
        dialogs_label.setText("Create dialog")
        dialogs_label.setFixedHeight(30)

        self.new_dialog_button.setFixedHeight(30)
        self.new_chat_button.setFixedHeight(30)

        self.new_dialog_button.setFixedWidth(60)
        self.new_chat_button.setFixedWidth(60)

        self.new_dialog_button.setText("Client")
        self.new_chat_button.setText("Server")

        self.new_dialog_button.setShortcut('Ctrl+N')
        self.new_chat_button.setShortcut('Ctrl+Shift+N')

        self.new_dialog_button.clicked.connect(lambda: new_dialog_click_callback(self))
        self.new_chat_button.clicked.connect(lambda: new_chat_click_callback(self))

        if platform.system() != "Linux":
            button_style = """
                QPushButton {
                    border: 2px solid """ + color_palette.primary + """;
                    border-radius: 3px;
                    background-color: """ + color_palette.primary_light + """;
                    color: #DDD;
                }

                QPushButton:pressed {
                    background-color: """ + color_palette.primary_dark + """;
                }
            """
            self.new_dialog_button.setStyleSheet(button_style)
            self.new_chat_button.setStyleSheet(button_style)

        palette = self.new_dialog_button.palette()
        palette.setColor(QPalette.Button, QColor(color_palette.primary_light))
        self.new_dialog_button.setPalette(palette)
        self.new_chat_button.setPalette(palette)

        layout.addWidget(dialogs_label)
        layout.addWidget(self.new_chat_button)
        layout.addWidget(self.new_dialog_button)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(layout)
