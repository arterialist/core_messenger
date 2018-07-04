import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QPalette, QCursor, QCloseEvent
from PyQt5.QtWidgets import QApplication, QAction, qApp, QMainWindow, QHBoxLayout, QFrame, QSplitter, QWidget, \
    QVBoxLayout, QListWidget, QAbstractItemView, QMenu

import color_palette
from callback.callbacks import *
from client import client_base
from iotools.sql_base import SQLManager, DB_MESSAGING
from iotools.sql_utils import init_databases, save_databases
from iotools.storage import AppStorage
from tools import full_strip
from widgets.dialogs.dialogs_head import DialogsListHeadWidget, DialogsIncomingConnectionWidget
from widgets.messages.message_input import MessageInputWidget
from widgets.windows.settings_window import SettingsWindow

main_window = None
settings_window = None
init_databases()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        toggle_listening_action = QAction("Toggle &listening", parent=self)
        toggle_listening_action.setCheckable(True)
        toggle_listening_action.setChecked(False)
        toggle_listening_action.setShortcut('Ctrl+L')
        toggle_listening_action.triggered.connect(toggle_listening_callback)

        settings_action = QAction("&Settings", parent=self)
        settings_action.setShortcut("Ctrl+Shift+S")
        settings_action.triggered.connect(self.open_settings)

        exit_action = QAction(QIcon('images/exit.png'), '&Quit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(toggle_listening_action)
        file_menu.addAction(settings_action)
        file_menu.addAction(exit_action)

        p = self.palette()
        p.setColor(QPalette.Background, QColor(color_palette.primary))
        self.setPalette(p)

        self.setCentralWidget(RootWidget())

        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle('Core Messenger')
        self.setWindowIcon(QIcon('images/telegram_icon.png'))

    def show(self):
        super().show()
        while 1:
            nickname, ok = QInputDialog.getText(self, 'Nickname', 'Enter nickname:')
            if ok:
                if len(full_strip(nickname)):
                    break
            else:
                self.close()

        while 1:
            port, ok = QInputDialog.getText(self, 'Port', 'Enter listening port:')
            port = full_strip(port)

            '''
            port must me
            decimal
            less than 655536 (2^16)
            not reserved (ftp, ssh, http, https)
            
            needs further improvement (port checking)
            '''
            if ok:
                if len(port) \
                        and port.isdecimal() \
                        and int(port) < 65536 \
                        and int(port) not in (21, 22, 80, 443):
                    break
            else:
                self.close()

        client_base.nickname = nickname
        print('nickname: {}'.format(nickname))

        client_base.local_port = int(port)
        print('listening port: {}'.format(port))

        AppStorage.get_storage().set("nickname", nickname)
        AppStorage.get_storage().set("port", port)

        client_base.init_socket()
        client_base.new_message_callback = lambda message: new_message_callback(message, main_window)
        client_base.invalid_message_callback = invalid_message_callback

    @staticmethod
    def open_settings():
        settings_window.show()

    def closeEvent(self, a0: QCloseEvent):
        client_base.finish()


class RootWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.splitter = QSplitter(Qt.Horizontal)
        self.opened_dialog_frame = OpenedDialogWidget()
        self.dialogs_list_frame = DialogsListRootWidget()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.dialogs_list_frame.setFrameShape(QFrame.StyledPanel)
        self.dialogs_list_frame.setMinimumWidth(200)

        self.opened_dialog_frame.setFrameShape(QFrame.StyledPanel)
        self.opened_dialog_frame.setMinimumWidth(300)

        self.splitter.addWidget(self.dialogs_list_frame)
        self.splitter.addWidget(self.opened_dialog_frame)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        layout.addWidget(self.splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class DialogsListRootWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.dialogs_list = QListWidget()
        self.incoming_connection = DialogsIncomingConnectionWidget(main_window)
        self.head = DialogsListHeadWidget()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        client_base.incoming_connection_callback = lambda: handle_incoming_connection_callback(self)

        self.incoming_connection.setHidden(True)
        p = self.dialogs_list.palette()
        p.setColor(QPalette.Base, QColor(color_palette.primary))
        self.dialogs_list.setPalette(p)
        self.dialogs_list.setIconSize(QSize(40, 40))
        self.dialogs_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.dialogs_list.currentItemChanged.connect(lambda current, previous: dialog_item_changed_callback(current, main_window))
        self.dialogs_list.setSpacing(5)

        self.dialogs_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dialogs_list.customContextMenuRequested.connect(self.dialog_context_menu_event)

        dialogs = SQLManager.get_instance(DB_MESSAGING).select_all("dialogs")
        for item in dialogs:
            self.dialogs_list.addItem(DialogItemWidget("", item[0], item[1], item[2], peer_id=item[3]))

        layout.addWidget(self.head)
        layout.addWidget(self.incoming_connection)
        layout.addWidget(self.dialogs_list)
        layout.setContentsMargins(0, 5, 0, 0)

        self.setLayout(layout)

    def dialog_context_menu_event(self, event):
        # this is necessary!
        # noinspection PyAttributeOutsideInit
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


class OpenedDialogWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.splitter = QSplitter(Qt.Vertical)
        self.message_input = MessageInputWidget()
        self.messages_list = QListWidget()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        p = self.messages_list.palette()
        p.setColor(QPalette.Base, QColor(color_palette.primary_dark))
        self.messages_list.setPalette(p)
        self.messages_list.setSpacing(5)
        self.messages_list.showMinimized()
        self.messages_list.setWordWrap(True)

        self.messages_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.messages_list.customContextMenuRequested.connect(self.message_context_menu_event)

        self.message_input.setMinimumHeight(50)
        self.message_input.setMaximumHeight(100)

        self.splitter.addWidget(self.messages_list)
        self.splitter.addWidget(self.message_input)

        layout.addWidget(self.splitter)

        layout.setContentsMargins(0, 0, 0, 0)
        self.splitter.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def message_context_menu_event(self, event):
        # same thing
        # noinspection PyAttributeOutsideInit
        self.menu = QMenu(self)
        reply_action = QAction('Reply', self)
        forward_action = QAction('Forward', self)
        edit_action = QAction('Edit', self)
        delete_action = QAction('Delete', self)
        message_item = self.messages_list.currentItem()
        delete_action.triggered.connect(lambda: delete_message_item_selected_callback(self.messages_list, message_item))
        self.menu.addAction(reply_action)
        self.menu.addAction(forward_action)
        self.menu.addAction(edit_action)
        self.menu.addAction(delete_action)
        # add other required actions
        self.menu.popup(QCursor.pos())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    settings_window = SettingsWindow()
    main_window.show()
    # noinspection PyBroadException
    try:
        sys.exit(app.exec_())
    finally:
        save_databases(AppStorage.get_settings(), AppStorage.get_storage())
        client_base.finish()
