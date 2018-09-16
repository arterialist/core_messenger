from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget, QSizePolicy, QLayout

from client.models.messages import Message
from theming import styles
from theming.theme_loader import ThemeLoader


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
        theme = ThemeLoader.loaded_theme

        if not self.service:
            self.message_text.setWordWrap(True)
        self.message_text.setText(self.message.text)

        bl_radius = "10px" if self.message.mine else "10px" if self.service else "0px"
        br_radius = "0px" if self.message.mine else "10px" if self.service else "10px"

        if self.message.mine:
            stylesheet = styles.my_message_balloon
        elif self.service:
            stylesheet = styles.service_message_balloon
        else:
            stylesheet = styles.their_message_balloon

        self.message_text.setStyleSheet(theme.apply_to_stylesheet(
            stylesheet,
            {
                "blRadius": bl_radius,
                "brRadius": br_radius
            }
        ))

        if self.from_peer_id and self.from_peer_id != self.previous_peer_id and not self.service:
            text = self.from_peer_id
            text += f"({self.from_nickname})" if self.from_nickname else ""
            self.name_text.setStyleSheet(theme.apply_to_stylesheet(styles.nickname_label))
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
