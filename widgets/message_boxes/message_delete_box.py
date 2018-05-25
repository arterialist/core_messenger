from PyQt5.QtWidgets import QMessageBox, QCheckBox


class DeleteMsgMessageBox(QMessageBox):
    def __init__(self, enable_checkbox=False):
        super(DeleteMsgMessageBox, self).__init__()
        self.checkbox = QCheckBox()
        self.init_ui(enable_checkbox)

    def init_ui(self, enable_checkbox):
        self.setWindowTitle("Are you sure?")
        self.setText("This action can't be undone.")

        if enable_checkbox:
            dialog_layout = self.layout()
            self.checkbox.setChecked(True)
            self.checkbox.setText("Delete for opponent?")
            dialog_layout.addWidget(self.checkbox)
            self.setLayout(dialog_layout)

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.No)

    def exec_(self, *args, **kwargs):
        return QMessageBox.exec_(self), self.checkbox.isChecked()
