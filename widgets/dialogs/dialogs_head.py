from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

import color_palette
from callback.callbacks import new_dialog_click_callback, accept_incoming_connection, decline_incoming_connection
from client import client_base
from iotools import sql_utils
from widgets.dialogs.dialogs_list import DialogItemWidget


class DialogsListHeadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.new_dialog_button = QPushButton(self)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        dialogs_label = QLabel(self)
        dialogs_label.setText("Dialogs")
        dialogs_label.setFixedHeight(30)

        self.new_dialog_button.setFixedHeight(30)
        self.new_dialog_button.setFixedWidth(60)
        self.new_dialog_button.setText("NEW")
        self.new_dialog_button.setShortcut('Ctrl+N')
        self.new_dialog_button.clicked.connect(lambda: new_dialog_click_callback(self))
        palette = self.new_dialog_button.palette()
        palette.setColor(QPalette.Button, QColor(color_palette.primary_light))
        self.new_dialog_button.setPalette(palette)

        layout.addWidget(dialogs_label)
        layout.addWidget(self.new_dialog_button)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(layout)


class DialogsIncomingConnectionWidget(QWidget):
    def __init__(self, window):
        super().__init__()
        self.connection_info = QLabel(self)
        self.accept_button = QPushButton(self)
        self.decline_button = QPushButton(self)
        self.window = window
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.setFixedHeight(40)

        self.accept_button.setFixedHeight(30)
        self.accept_button.setFixedWidth(60)
        self.accept_button.setText("✓")
        self.accept_button.setShortcut("Ctrl+Shift+A")
        self.accept_button.clicked.connect(lambda: self.accept())
        palette = self.accept_button.palette()
        palette.setColor(QPalette.Button, QColor(color_palette.primary_light))
        self.accept_button.setPalette(palette)

        self.decline_button.setFixedHeight(30)
        self.decline_button.setFixedWidth(60)
        self.decline_button.setText("✗")
        self.decline_button.setShortcut("Ctrl+Shift+D")
        self.decline_button.clicked.connect(lambda: self.decline())
        palette = self.accept_button.palette()
        palette.setColor(QPalette.Button, QColor(color_palette.primary_light))
        self.decline_button.setPalette(palette)

        self.connection_info.setFixedHeight(40)
        self.connection_info.maximumWidth()

        layout.addWidget(self.connection_info)
        layout.addWidget(self.decline_button)
        layout.addWidget(self.accept_button)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

    def accept(self):
        accept_incoming_connection()
        self.setHidden(True)
        address = client_base.current_connection_address
        dialog = DialogItemWidget("", address[0], address[1], 0)
        sql_utils.create_dialog(address[0], address[1], 0, dialog.peer_id)
        dialogs_list = self.parentWidget().dialogs_list
        dialogs_list.addItem(dialog)
        dialogs_list.setCurrentItem(dialog)
        client_base.current_peer_id = dialog.peer_id

    def decline(self):
        decline_incoming_connection()
        self.setHidden(True)
