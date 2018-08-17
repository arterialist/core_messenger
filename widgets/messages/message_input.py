import platform

from PyQt5.QtGui import QPalette, QColor, QKeySequence
from PyQt5.QtWidgets import QPushButton, QTextEdit, QFrame, QHBoxLayout, QShortcut

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
        self.message_input.setStyleSheet("color: #DDD;")
        self.message_input.setAutoFormatting(QTextEdit.AutoAll)

        self.send_button.setFixedWidth(60)
        self.send_button.setFixedHeight(30)
        p = self.send_button.palette()
        p.setColor(QPalette.Button, QColor(color_palette.primary_light))
        self.send_button.setPalette(p)
        self.send_button.clicked.connect(lambda: self.send_button_clicked())
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.send_button)
        shortcut.activated.connect(lambda: self.send_button_clicked())
        shortcut.setEnabled(True)
        if platform.system() != "Linux":
            self.send_button.setStyleSheet("""
                    QPushButton {
                        border: 2px solid """ + color_palette.primary + """;
                        border-radius: 3px;
                        background-color: """ + color_palette.primary_light + """;
                        color: #DDD;
                    }
    
                    QPushButton:pressed {
                        background-color: """ + color_palette.primary_dark + """;
                    }
                """)

        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def send_button_clicked(self):
        dialog = self.parentWidget().parentWidget().parentWidget().parentWidget().dialogs_list_frame.dialogs_list.currentItem()
        if dialog:
            current_peer_id = dialog.peer_id
            send_button_clicked_callback(self, current_peer_id)
        self.message_input.setFocus()
