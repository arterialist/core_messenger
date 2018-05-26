from PyQt5.QtWidgets import QMessageBox, QCheckBox


class CheckboxMessageBox(QMessageBox):
    def __init__(self, checkbox_text, parent=None, enable_checkbox=False):
        super(CheckboxMessageBox, self).__init__()
        self.checkbox = QCheckBox(parent=parent)
        self.init_ui(enable_checkbox, checkbox_text)

    def init_ui(self, enable_checkbox, checkbox_text):
        if enable_checkbox:
            dialog_layout = self.layout()
            self.checkbox.setChecked(True)
            self.checkbox.setText(checkbox_text)
            dialog_layout.addWidget(self.checkbox)
            self.setLayout(dialog_layout)

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.No)

    def exec_(self, *args, **kwargs):
        return QMessageBox.exec_(self), self.checkbox.isChecked()
