from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

import color_palette
from callback.callbacks import new_dialog_click_callback


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
