from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QPushButton, QTextEdit, QFrame, QHBoxLayout, QShortcut

from callback.callbacks import send_button_clicked_callback
from iotools.storage import AppStorage
from models.storage import Category
from theming.styles import button_style
from theming.theme_loader import ThemeLoader


class MessageInputWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.send_button = QPushButton('Send')
        self.message_input = QTextEdit()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        self.message_input.setStyleSheet(ThemeLoader.loaded_theme.get_default_for_widget(self.message_input))
        self.message_input.setAutoFormatting(QTextEdit.AutoAll)

        self.send_button.clicked.connect(lambda: self.send_button_clicked())
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.send_button)
        shortcut.activated.connect(lambda: self.send_button_clicked(True))
        shortcut.setEnabled(True)
        self.send_button.clicked.connect(lambda: self.send_button_clicked(True))
        self.send_button.setStyleSheet(ThemeLoader.loaded_theme.apply_to_stylesheet(button_style))

        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def send_button_clicked(self, with_ctrl=False):
        use_ctrl = bool(int(AppStorage.get_settings().get(Category("messaging", "Messaging"), "use_ctrl_enter").value))

        if use_ctrl and not with_ctrl:
            return

        dialog = self.parentWidget().parentWidget().parentWidget().parentWidget().dialogs_list_frame.dialogs_list.currentItem()
        if dialog:
            current_peer_id = dialog.peer_id
            send_button_clicked_callback(self, current_peer_id)
        self.message_input.setFocus()
