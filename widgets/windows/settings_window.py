from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QWidget, QMainWindow, QListWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QCheckBox, QLineEdit, \
    QAbstractItemView, QScrollArea

import color_palette
from iotools.storage import AppStorage
from models.storage import Setting


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setGeometry(150, 150, 600, 600)

        p = self.palette()
        p.setColor(QPalette.Background, QColor(color_palette.primary))
        self.setPalette(p)

        self.setCentralWidget(SettingsRootWidget())


# noinspection PyAttributeOutsideInit
class SettingsRootWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.categories_list = QListWidget()
        self.current_category = ""
        self.init_ui()

    def init_ui(self):
        self.categories_list.setFixedWidth(200)
        p = self.categories_list.palette()
        p.setColor(QPalette.Base, QColor(color_palette.primary_dark))
        self.categories_list.setPalette(p)
        self.categories_list.currentItemChanged.connect(self.category_changed)
        self.categories_list.setSelectionMode(QAbstractItemView.SingleSelection)

        settings = AppStorage.get_settings()

        first_settings = settings.get_settings(settings.get_categories()[0])
        self.current_category = settings.get_categories()[0]
        for category in settings.get_categories():
            self.categories_list.addItem(category.display_name)

        self.settings_container = SettingsContainerWidget(first_settings)
        self.settings_container.setFixedWidth(400)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.categories_list)
        layout.addWidget(self.settings_container)

        self.setLayout(layout)

    def category_changed(self, current, previous):
        if previous:
            layout = self.layout()
            layout.removeWidget(self.settings_container)
            self.settings_container.deleteLater()
            self.settings_container = None
            settings = AppStorage.get_settings()
            self.current_category = settings.get_categories()[self.categories_list.currentIndex().row()]
            self.settings_container = SettingsContainerWidget(settings.get_settings(self.current_category))
            layout.addWidget(self.settings_container)


class SettingItemWidget(QWidget):
    def __init__(self, setting: Setting):
        super().__init__()

        self.setting = setting
        self.title = QLabel()
        self.value = SettingsItemValueWidget(setting.value, setting.setting_type)

        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(90)
        self.title.setText(self.setting.display_name)
        self.title.setFont(QFont("Times", weight=QFont.Bold))

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        self.setLayout(layout)

    def get_setting(self):
        self.setting.value = self.value.get_value()
        return self.setting


class SettingsItemValueWidget(QWidget):
    def __init__(self, value, setting_type):
        super().__init__()
        self.value = value
        self.setting_type = setting_type

        self.checkbox = QCheckBox()
        self.editable = QLineEdit()
        self.init_ui()

    def init_ui(self):
        layout = self.get_layout()
        self.setLayout(layout)

    def get_layout(self):
        layout = QHBoxLayout()
        if self.setting_type == 0:
            self.checkbox.setChecked(bool(int(self.value)))
            layout.addWidget(self.checkbox)
        elif self.setting_type == 1:
            self.editable.setText(self.value)
            layout.addWidget(self.editable)

        return layout

    def get_value(self):
        value = None
        if self.setting_type == 0:
            value = self.checkbox.isChecked()
        elif self.setting_type == 1:
            value = str(self.editable.text())

        return value


class SettingsContainerWidget(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

        self.settings_list = QScrollArea()
        self.settings_list_content = QWidget()
        self.action_buttons = QWidget()
        self.ok_button = QPushButton("OK")
        self.apply_button = QPushButton("Apply")
        self.cancel_button = QPushButton("Cancel")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        p = self.palette()
        p.setColor(QPalette.Base, QColor(color_palette.primary))
        self.setPalette(p)

        settings_layout = QVBoxLayout()
        settings_layout.setAlignment(Qt.AlignTop)
        self.settings_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.cancel_button.clicked.connect(self.cancel_settings)
        self.apply_button.clicked.connect(self.apply_settings)
        self.ok_button.clicked.connect(self.save_and_exit)

        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setAlignment(Qt.AlignRight)
        action_buttons_layout.addWidget(self.ok_button)
        action_buttons_layout.addWidget(self.apply_button)
        action_buttons_layout.addWidget(self.cancel_button)
        self.action_buttons.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.action_buttons.setLayout(action_buttons_layout)

        for setting in self.settings:
            settings_layout.addWidget(SettingItemWidget(setting))

        self.settings_list_content.setLayout(settings_layout)
        self.settings_list.setWidget(self.settings_list_content)

        layout.addWidget(self.settings_list)
        layout.addWidget(self.action_buttons)
        self.setLayout(layout)

    def cancel_settings(self):
        self.parentWidget().parentWidget().close()

    def apply_settings(self):
        category = self.parentWidget().current_category
        settings_list_layout = self.settings_list.widget().layout()

        for index in range(settings_list_layout.count()):
            AppStorage.get_settings().set(category, settings_list_layout.itemAt(index).widget().get_setting())

    def save_and_exit(self):
        self.apply_settings()
        self.cancel_settings()
