from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget, QSizePolicy, QLayout

import color_palette
from client.models.messages import Message


class MessageItemWidget(QWidget):
    def __init__(self, message: Message, from_peer_id: str, from_nickname: str, service: bool = False, previous_peer_id: str = None):
        super().__init__()
        self.message = message
        self.service = service
        self.from_peer_id = from_peer_id
        self.from_nickname = from_nickname
        self.previous_peer_id = previous_peer_id

        self.name_text = QLabel()
        self.message_text = QLabel()

        self.attachments_box = QHBoxLayout()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        background_color = color_palette.palette["blue_grey"][800]
        if self.message.mine:
            background_color = color_palette.primary
        elif self.service:
            background_color = "#80546E7A"

        if not self.service:
            self.message_text.setWordWrap(True)
        self.message_text.setText(self.message.text)
        p = self.message_text.palette()
        p.setColor(QPalette.Text, QColor("#DDDDDD") if self.service else QColor("#FFFFFF"))
        self.message_text.setPalette(p)
        bl_radius = "10px" if self.message.mine else "10px" if self.service else "0px"
        br_radius = "0px" if self.message.mine else "10px" if self.service else "10px"
        self.message_text.setStyleSheet(
            """
            QWidget {
                background-color: """ + background_color + """;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-left-radius: """ + bl_radius + """;
                border-bottom-right-radius: """ + br_radius + """;
                padding: 5px;
            }
            """
        )

        if self.from_peer_id and self.from_peer_id != self.previous_peer_id and not self.service:
            text = self.from_peer_id
            text += f"({self.from_nickname})" if self.from_nickname else ""
            p = self.message_text.palette()
            p.setColor(QPalette.Text, QColor("#DDDDFF"))
            font = self.name_text.font()
            font.setBold(True)
            self.name_text.setPalette(p)
            self.name_text.setFont(font)
            self.name_text.setText(text)
            self.name_text.setContentsMargins(5, 2, 2, 2)
            layout.addWidget(self.name_text)

        layout.addWidget(self.message_text)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSizeConstraint(QLayout.SetMaximumSize)
        alignment = Qt.AlignCenter
        if not self.service:
            alignment = Qt.AlignRight if self.message.mine else Qt.AlignLeft
        layout.setAlignment(alignment)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setLayout(layout)

    def refresh(self):
        self.message_text.setText(self.message.text)
        if self.from_peer_id and self.from_peer_id != self.previous_peer_id and not self.service:
            text = self.from_peer_id
            text += f"({self.from_nickname})" if self.from_nickname else ""
            self.name_text.setText(text)
