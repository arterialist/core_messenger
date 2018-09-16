import re

from PyQt5.QtWidgets import QWidget, QPushButton, QTextEdit, QTabWidget

from theming import styles


class Theme:
    def __init__(self, parsed_file: dict):
        self.colors = parsed_file

    def apply_to_stylesheet(self, stylesheet: str, custom_placeholders: dict = {}):
        placeholder_regexp = re.compile(r"@([a-z]+[a-zA-Z]*)@")
        placeholders = placeholder_regexp.findall(stylesheet)
        new_stylesheet = stylesheet
        for placeholder in placeholders:
            value = self.colors.get(placeholder, custom_placeholders.get(placeholder, "#FF0000"))
            new_stylesheet = new_stylesheet.replace(f"@{placeholder}@", value)  # red for theme creator to detect errors in theme
        return new_stylesheet

    def get_default_for_widget(self, widget: QWidget):
        if isinstance(widget, QPushButton):
            return self.apply_to_stylesheet(styles.button_style)
        if isinstance(widget, QTextEdit):
            return self.apply_to_stylesheet(styles.multiline_input_style)
        if isinstance(widget, QTabWidget):
            return self.apply_to_stylesheet(styles.tabs_style)
