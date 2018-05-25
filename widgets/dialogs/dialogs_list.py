import hashlib
import uuid

from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtWidgets import QListWidgetItem

import color_palette

chat_type_icons = {
    0: "images/p2p_icon.png",
    1: "images/psp_icon.png",
    2: "images/chat_icon.png"
}


class DialogItemWidget(QListWidgetItem):
    def __init__(self, nickname, host, port, chat_type, peer_id=None):
        super().__init__()
        self.nickname = nickname
        self.host = host
        self.port = port
        self.chat_type = chat_type
        self.peer_id = peer_id if peer_id else hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()
        self.init_ui()

    def init_ui(self):
        self.setText('Dialog with {0}\n{1}:{2}'.format(self.nickname, self.host, self.port))
        self.setFont(QFont('sans-serif', 10))
        self.setIcon(QIcon(chat_type_icons[self.chat_type]))
        self.setBackground(QColor(color_palette.primary))
