from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

from callback.callbacks import new_dialog_click_callback, new_chat_click_callback
from theming.theme_loader import ThemeLoader


class DialogsListHeadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.new_dialog_button = QPushButton(self)
        self.new_chat_button = QPushButton(self)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        dialogs_label = QLabel(self)
        dialogs_label.setText("Connect to:")
        dialogs_label.setFixedHeight(30)

        self.new_dialog_button.setText("Client")
        self.new_chat_button.setText("Server")

        self.new_dialog_button.setShortcut('Ctrl+N')
        self.new_chat_button.setShortcut('Ctrl+Shift+N')

        self.new_dialog_button.clicked.connect(lambda: new_dialog_click_callback(self))
        self.new_chat_button.clicked.connect(lambda: new_chat_click_callback(self))

        button_style = ThemeLoader.loaded_theme.get_default_for_widget(self.new_dialog_button)
        self.new_dialog_button.setStyleSheet(button_style)
        self.new_chat_button.setStyleSheet(button_style)

        layout.addWidget(dialogs_label)
        layout.addWidget(self.new_chat_button)
        layout.addWidget(self.new_dialog_button)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(layout)
