from PyQt5.QtWidgets import QMessageBox, QCheckBox

from widgets.message_boxes.basic import CheckboxMessageBox


class DeleteMsgMessageBox(CheckboxMessageBox):
    def __init__(self, enable_checkbox: bool = False, nickname: str = None):
        super(DeleteMsgMessageBox, self).__init__("Delete for {}?".format(nickname if nickname else "opponent"))
        self.checkbox = QCheckBox()
        self.init_ui(enable_checkbox, "Delete for {}?".format(nickname if nickname else "opponent"))

    def init_ui(self, enable_checkbox, checkbox_text):
        self.setWindowTitle("Are you sure?")
        self.setText("This action can't be undone.")

        if enable_checkbox:
            dialog_layout = self.layout()
            self.checkbox.setChecked(True)
            self.checkbox.setText(checkbox_text)
            dialog_layout.addWidget(self.checkbox)
            self.setLayout(dialog_layout)

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.No)

    def exec_(self, *args, **kwargs):
        return QMessageBox.exec_(self), self.checkbox.isChecked()
