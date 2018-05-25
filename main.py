import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QPalette, QCursor, QCloseEvent
from PyQt5.QtWidgets import QApplication, QAction, qApp, QMainWindow, QHBoxLayout, QFrame, QSplitter, QWidget, \
    QVBoxLayout, QListWidget, QAbstractItemView, QMenu

import color_palette
from callback.callbacks import *
from client import client_base
from iotools.sql_base import SQLManager, ColumnTypes
from tools import full_strip
from widgets.dialogs.dialogs_head import DialogsListHeadWidget, DialogsIncomingConnectionWidget
from widgets.messages.message_input import MessageInputWidget

window = None
sql_storage_manager = SQLManager.get_instance("files/storage.db")

sql_storage_manager.create_table("dialogs",
                                 ["host", "port", "chat_type", "peer_id"],
                                 [ColumnTypes.TEXT, ColumnTypes.NUMERIC, ColumnTypes.NUMERIC, ColumnTypes.TEXT])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        toggle_listening_action = QAction('Toggle &listening', self, checkable=True)
        toggle_listening_action.setChecked(False)
        toggle_listening_action.setShortcut('Ctrl+L')
        toggle_listening_action.triggered.connect(toggle_listening_callback)

        exit_action = QAction(QIcon('images/exit.png'), '&Quit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(exit_action)
        file_menu.addAction(toggle_listening_action)

        p = self.palette()
        p.setColor(QPalette.Background, QColor(color_palette.primary))
        self.setPalette(p)

        self.setCentralWidget(RootWidget())

        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle('Core Messenger')
        self.setWindowIcon(QIcon('images/telegram_icon.png'))

        self.show()

        while 1:
            text, ok = QInputDialog.getText(self, 'Nickname', 'Enter nickname:')
            if ok and len(full_strip(text)):
                break

        client_base.nickname = text
        print('nickname: {}'.format(text))

        while 1:
            text, ok = QInputDialog.getText(self, 'Port', 'Enter listening port:')
            text = full_strip(text)

            '''
            port must me
            decimal
            less than 655536 (2^16)
            not reserved (ftp, ssh, http, https)
            '''
            if ok \
                    and len(text) \
                    and text.isdecimal() \
                    and int(text) < 65536 \
                    and int(text) not in (21, 22, 80, 443):
                break

        client_base.local_port = int(text)
        print('listening port: {}'.format(text))

        client_base.init_socket()
        client_base.new_message_callback = lambda message: new_message_callback(message, window)
        client_base.invalid_message_callback = lambda reason, message: invalid_message_callback(reason, message, window)

    def closeEvent(self, a0: QCloseEvent):
        client_base.finish()


# noinspection PyAttributeOutsideInit
class RootWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.dialogs_list_frame = DialogsListRootWidget()
        self.dialogs_list_frame.setFrameShape(QFrame.StyledPanel)
        self.dialogs_list_frame.setMinimumWidth(200)

        self.opened_dialog_frame = OpenedDialogWidget()
        self.opened_dialog_frame.setFrameShape(QFrame.StyledPanel)
        self.opened_dialog_frame.setMinimumWidth(300)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.dialogs_list_frame)
        self.splitter.addWidget(self.opened_dialog_frame)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        layout.addWidget(self.splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# noinspection PyAttributeOutsideInit
class DialogsListRootWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        client_base.incoming_connection_callback = lambda: handle_incoming_connection_callback(self)

        self.head = DialogsListHeadWidget()
        self.incoming_connection = DialogsIncomingConnectionWidget(window)
        self.incoming_connection.setHidden(True)
        self.dialogs_list = QListWidget()
        p = self.dialogs_list.palette()
        p.setColor(QPalette.Base, QColor(color_palette.primary))
        self.dialogs_list.setPalette(p)
        self.dialogs_list.setIconSize(QSize(40, 40))
        # noinspection PyTypeChecker
        self.dialogs_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.dialogs_list.currentItemChanged.connect(lambda current, previous: dialog_item_changed_callback(current, window))
        self.dialogs_list.setSpacing(5)

        self.dialogs_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dialogs_list.customContextMenuRequested.connect(self.dialog_context_menu_event)

        dialogs = sql_storage_manager.select_all("dialogs")
        for item in dialogs:
            self.dialogs_list.addItem(DialogItemWidget("", item[0], item[1], item[2], peer_id=item[3]))

        layout.addWidget(self.head)
        layout.addWidget(self.incoming_connection)
        layout.addWidget(self.dialogs_list)
        layout.setContentsMargins(0, 5, 0, 0)

        self.setLayout(layout)

    def dialog_context_menu_event(self, event):
        self.menu = QMenu(self)
        close_action = QAction('Disconnect', self)
        close_action.triggered.connect(lambda: self.remove_dialog(self.dialogs_list.currentItem()))
        self.menu.addAction(close_action)
        # add other required actions
        self.menu.popup(QCursor.pos())

    def remove_dialog(self, dialog):
        if dialog:
            delete_dialog_callback(dialog.peer_id)
            self.dialogs_list.takeItem(self.dialogs_list.row(dialog))


# noinspection PyAttributeOutsideInit
class OpenedDialogWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.messages_list = QListWidget()
        p = self.messages_list.palette()
        p.setColor(QPalette.Base, QColor(color_palette.primary_dark))
        self.messages_list.setPalette(p)
        self.messages_list.setSpacing(5)
        self.messages_list.showMinimized()

        self.messages_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.messages_list.customContextMenuRequested.connect(self.message_context_menu_event)

        self.message_input = MessageInputWidget()

        self.message_input.setMinimumHeight(50)
        self.message_input.setMaximumHeight(100)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.messages_list)
        self.splitter.addWidget(self.message_input)

        layout.addWidget(self.splitter)

        layout.setContentsMargins(0, 0, 0, 0)
        self.splitter.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def message_context_menu_event(self, event):
        self.menu = QMenu(self)
        reply_action = QAction('Reply', self)
        forward_action = QAction('Forward', self)
        edit_action = QAction('Edit', self)
        delete_action = QAction('Delete', self)
        reply_action.triggered.connect(lambda: print(self.messages_list.currentItem()))
        self.menu.addAction(reply_action)
        self.menu.addAction(forward_action)
        self.menu.addAction(edit_action)
        self.menu.addAction(delete_action)
        # add other required actions
        self.menu.popup(QCursor.pos())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    # noinspection PyBroadException
    try:
        sys.exit(app.exec_())
    except Exception:
        client_base.finish()
