from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QMainWindow, QListWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QCheckBox, QLineEdit, \
    QAbstractItemView, QScrollArea, QListWidgetItem, QFileDialog

from iotools.storage import AppStorage
from models.storage import Setting, SETTING_CHECKBOX, SETTING_TEXT, SETTING_FILE
from theming import styles
from theming.theme_loader import ThemeLoader


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setGeometry(150, 150, 600, 600)
        self.setFixedWidth(600)

        self.setStyleSheet(ThemeLoader.loaded_theme.apply_to_stylesheet(styles.main_window_style))

        self.setCentralWidget(SettingsRootWidget())


# noinspection PyAttributeOutsideInit
class SettingsRootWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.categories_list = QListWidget()
        self.current_category = ""
        self.init_ui()

    def init_ui(self):
        theme = ThemeLoader.loaded_theme
        self.setStyleSheet(theme.apply_to_stylesheet(styles.main_window_style))

        self.categories_list.setFixedWidth(200)
        self.categories_list.setStyleSheet(theme.apply_to_stylesheet(styles.settings_categories_list_style))
        self.categories_list.currentItemChanged.connect(self.category_changed)
        self.categories_list.setSelectionMode(QAbstractItemView.SingleSelection)

        settings = AppStorage.get_settings()

        first_settings = settings.get_settings(settings.get_categories()[0])
        self.current_category = settings.get_categories()[0]
        for category in settings.get_categories():
            item = QListWidgetItem(category.display_name)
            self.categories_list.addItem(item)

        self.settings_container = SettingsContainerWidget(first_settings)
        self.settings_container.setFixedWidth(400)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.categories_list)
        layout.addWidget(self.settings_container)

        self.setLayout(layout)

    def category_changed(self, _, previous):
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
        self.setFixedHeight(50)
        self.title.setText(self.setting.display_name)
        font = QFont()
        font.setBold(True)
        self.title.setFont(font)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.setContentsMargins(0, 0, 0, 0)
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
        self.button = QPushButton()
        self.init_ui()

    def init_ui(self):
        layout = self.get_layout()
        self.setLayout(layout)

    def get_layout(self):
        layout = QHBoxLayout()
        self.button.setStyleSheet(ThemeLoader.loaded_theme.get_default_for_widget(self.button))
        if self.setting_type == SETTING_CHECKBOX:
            self.checkbox.setChecked(bool(int(self.value)))
            layout.addWidget(self.checkbox)
        elif self.setting_type == SETTING_TEXT:
            self.editable.setText(self.value)
            layout.addWidget(self.editable)
        elif self.setting_type == SETTING_FILE:
            self.editable.setText(self.value)
            self.button.setText("Choose")
            self.button.clicked.connect(self.choose_file_callback)
            layout.addWidget(self.editable)
            layout.addWidget(self.button)

        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def choose_file_callback(self):
        file_path: QUrl = (QFileDialog.getOpenFileUrl(caption="Choose file"))[0]
        file_path: str = file_path.toString()
        if file_path:
            self.editable.setText(file_path)

    def get_value(self):
        value = None
        if self.setting_type == SETTING_CHECKBOX:
            value = self.checkbox.isChecked()
        elif self.setting_type in [SETTING_TEXT, SETTING_FILE]:
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
        self.setStyleSheet(ThemeLoader.loaded_theme.apply_to_stylesheet(styles.settings_category_opened_style))

        settings_layout = QVBoxLayout()
        settings_layout.setAlignment(Qt.AlignTop)
        self.settings_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        button_style = ThemeLoader.loaded_theme.get_default_for_widget(self.ok_button)
        self.cancel_button.clicked.connect(self.cancel_settings)
        self.cancel_button.setStyleSheet(button_style)
        self.apply_button.clicked.connect(self.apply_settings)
        self.apply_button.setStyleSheet(button_style)
        self.ok_button.clicked.connect(self.save_and_exit)
        self.ok_button.setStyleSheet(button_style)

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
