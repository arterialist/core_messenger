import platform
import sys

from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPalette, QCursor, QCloseEvent, QKeySequence
from PyQt5.QtWidgets import QApplication, QAction, qApp, QMainWindow, QHBoxLayout, QFrame, QSplitter, QVBoxLayout, QAbstractItemView, QMenu, \
    QTabWidget, QShortcut

import color_palette
from callback.callbacks import *
from client import client_base
from client.models.messages import Data
from iotools.sql_base import SQLManager, DB_MESSAGING
from iotools.sql_utils import init_databases, save_databases, delete_messages_table_for_dialog, create_messages_table_for_dialog
from iotools.storage import AppStorage
from models.logging import Logger
from models.storage import Category
from tools import full_strip
from widgets.dialogs.dialogs_head import DialogsListHeadWidget
from widgets.message_boxes.basic import ConfirmationMessageBox
from widgets.messages.message_input import MessageInputWidget
from widgets.windows.settings_window import SettingsWindow

main_window = None
settings_window = None
Logger.get_channel("SQL", True).disable()
general_log = Logger.get_channel("GENERAL", True)
init_databases()


# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    new_message_signal = pyqtSignal(Packet, Peer)

    @pyqtSlot(Packet, Peer)
    def new_message_received_slot(self, packet: Packet, peer: Peer):
        new_message_callback(packet, peer, main_window)

    def __init__(self):
        super().__init__()
        self.new_message_signal.connect(self.new_message_received_slot)
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
        self.setWindowIcon(QIcon('images/app-icon.png'))

    def show(self):
        super().show()
        if not bool(int(AppStorage.get_settings().get(Category("general", "General"), "save_startup_data").value)):
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
        else:
            nickname = AppStorage.get_storage().get("nickname")
            port = int(AppStorage.get_storage().get("port"))

        client_base.nickname = nickname
        general_log.log('nickname: {}'.format(nickname))

        client_base.local_port = int(port)
        general_log.log('listening port: {}'.format(port))

        AppStorage.get_storage().set("nickname", nickname)
        AppStorage.get_storage().set("port", port)

        client_base.init_socket()
        client_base.new_message_callback = lambda message, peer: self.new_message_signal.emit(message, peer)
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


# noinspection PyAttributeOutsideInit,PyUnresolvedReferences
class DialogsListRootWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.dialogs_list = QListWidget()
        self.incoming_list = QListWidget()
        self.head = DialogsListHeadWidget()
        self.tabs = QTabWidget()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # shortcuts setup
        close_dialog_shortcut = QShortcut(QKeySequence("Esc"), self)
        close_dialog_shortcut.activated.connect(lambda: self.close_dialog_event())
        close_dialog_shortcut.setEnabled(True)

        dialog_up_shortcut = QShortcut(QKeySequence("Alt+Up"), self)
        dialog_up_shortcut.activated.connect(lambda: self.open_dialog_above())
        dialog_up_shortcut.setEnabled(True)

        dialog_down_shortcut = QShortcut(QKeySequence("Alt+Down"), self)
        dialog_down_shortcut.activated.connect(lambda: self.open_dialog_below())
        dialog_down_shortcut.setEnabled(True)

        open_dialogs_shortcut = QShortcut(QKeySequence("Ctrl+Alt+D"), self)
        open_dialogs_shortcut.activated.connect(lambda: self.tabs.setCurrentIndex(0))
        open_dialogs_shortcut.setEnabled(True)

        open_incoming_shortcut = QShortcut(QKeySequence("Ctrl+Alt+I"), self)
        open_incoming_shortcut.activated.connect(lambda: self.tabs.setCurrentIndex(1))
        open_incoming_shortcut.setEnabled(True)

        accept_connection_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        accept_connection_shortcut.activated.connect(lambda: self.accept_connection_event(self.incoming_list.currentItem()))
        accept_connection_shortcut.setEnabled(True)

        decline_connection_shortcut = QShortcut(QKeySequence("Ctrl+Shift+D"), self)
        decline_connection_shortcut.activated.connect(lambda: self.decline_connection_event(self.incoming_list.currentItem()))
        decline_connection_shortcut.setEnabled(True)

        # dialogs list setup
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
            self.dialogs_list.addItem(DialogItemWidget(item[4], item[0], item[1], item[2], peer_id=item[3]))

        # incoming list setup
        p = self.incoming_list.palette()
        p.setColor(QPalette.Base, QColor(color_palette.primary))
        self.incoming_list.setPalette(p)

        self.incoming_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.incoming_list.customContextMenuRequested.connect(self.incoming_context_menu_event)

        # tabs setup
        if platform.system() != "Linux":
            self.tabs.setStyleSheet(
                'QTabBar::tab:selected {background-color: ' + color_palette.primary + ';} ' +
                'QTabBar::tab:!selected {background-color: ' + color_palette.primary_light + ';} ' +
                'QTabWidget::pane { background-color: ' + color_palette.primary + ';} ' +
                'QTabWidget::pane { border: none;} '
            )
        p = self.tabs.palette()
        p.setColor(QPalette.Button, QColor(color_palette.primary))
        self.tabs.setPalette(p)
        self.tabs.addTab(self.dialogs_list, "Dialogs")
        self.tabs.addTab(self.incoming_list, "Incoming Connections")

        layout.addWidget(self.head)
        layout.addWidget(self.tabs)
        layout.setContentsMargins(0, 5, 0, 0)

        client_base.incoming_connection_callback = lambda address, connection: handle_incoming_connection_callback(self.incoming_list, address)

        self.setLayout(layout)

    def close_dialog_event(self):
        dialog_item_changed_callback(None, main_window)
        if self.dialogs_list.currentItem():
            self.dialogs_list.currentItem().setSelected(False)

    def open_dialog_above(self):
        current = self.dialogs_list.currentRow()
        if current:
            self.dialogs_list.setCurrentRow(current - 1)

    def open_dialog_below(self):
        current = self.dialogs_list.currentRow()
        if current < self.dialogs_list.count() - 1:
            self.dialogs_list.setCurrentRow(current + 1)

    def dialog_context_menu_event(self, _):
        # this is necessary!
        # noinspection PyAttributeOutsideInit
        self.menu = QMenu(self)
        item: DialogItemWidget = self.dialogs_list.currentItem()
        if item:
            peer_id = item.peer_id

            share_info_action = QAction('Share Your Info', self)
            share_info_action.triggered.connect(lambda: self.share_info(peer_id))

            request_info_action = QAction('Request Peer Info', self)
            request_info_action.triggered.connect(lambda: self.request_info(peer_id))

            clear_history_action = QAction('Clear History', self)
            clear_history_action.triggered.connect(lambda: self.clear_history(peer_id))

            delete_dialog_action = QAction('Delete Dialog', self)
            delete_dialog_action.triggered.connect(lambda: self.delete_dialog(item))

            self.menu.addAction(share_info_action)
            self.menu.addAction(request_info_action)
            self.menu.addAction(clear_history_action)
            self.menu.addAction(delete_dialog_action)

            if peer_id in client_base.peers.keys():
                disconnect_action = QAction('Disconnect', self)
                disconnect_action.triggered.connect(lambda: self.disconnect_from_peer(item))
                self.menu.addAction(disconnect_action)
            else:
                reconnect_action = QAction('Reconnect', self)
                reconnect_action.triggered.connect(lambda: self.reconnect_to_peer(item))
                self.menu.addAction(reconnect_action)
            # add other required actions
            self.menu.popup(QCursor.pos())

    def incoming_context_menu_event(self, _):
        item = self.incoming_list.currentItem()
        if item:
            # noinspection PyAttributeOutsideInit
            self.menu = QMenu(self)

            accept_action = QAction("Accept", self)
            accept_action.triggered.connect(lambda: self.accept_connection_event(item))

            decline_action = QAction("Decline", self)
            decline_action.triggered.connect(lambda: self.decline_connection_event(item))

            self.menu.addAction(accept_action)
            self.menu.addAction(decline_action)
            self.menu.popup(QCursor.pos())

    def accept_connection_event(self, item):
        address = (item.text().split(":")[0], int(item.text().split(":")[1]))
        accept_incoming_connection(self, address)

    def decline_connection_event(self, item):
        address = (item.text().split(":")[0], int(item.text().split(":")[1]))
        decline_incoming_connection(self, address)

    @staticmethod
    def disconnect_from_peer(dialog):
        client_base.send_message(
            dialog.peer_id,
            Packet(
                action=DisconnectAction(),
                message=Message()
            )
        )
        client_base.disconnect(Peer(dialog.host, dialog.port, dialog.peer_id))

    @staticmethod
    def reconnect_to_peer(dialog):
        if dialog.chat_type == 0:
            client_base.p2p_connect(dialog.host, dialog.port, peer_id_override=dialog.peer_id)
            client_base.send_message(
                dialog.peer_id,
                Packet(
                    action=ConnectAction(),
                    message=Message(),
                    data=Data()
                )
            )
        else:
            client_base.server_connect(dialog.host, dialog.port, peer_id_override=dialog.peer_id)

    def delete_dialog(self, dialog):
        result = ConfirmationMessageBox("Delete dialog? This cannot be undone.").exec_()
        if result == QMessageBox.Yes:
            delete_dialog_callback(dialog.peer_id, dialog.host, dialog.port)
            self.dialogs_list.takeItem(self.dialogs_list.row(dialog))

    def clear_history(self, peer_id):
        result = ConfirmationMessageBox("Clear history? This cannot be undone.").exec_()
        if result == QMessageBox.Yes:
            self.parentWidget().parentWidget().opened_dialog_frame.messages_list.clear()
            delete_messages_table_for_dialog(peer_id)
            create_messages_table_for_dialog(peer_id)

    @staticmethod
    def send_info(peer_id: str, request: bool = False):
        client_base.send_message(peer_id, Packet(
            message=Message(text=""),
            action=PeerInfoAction(),
            data=Data(content={
                "nickname": client_base.nickname,
                "port": client_base.local_port,
                "request": request
            })
        ))

    def share_info(self, peer_id):
        self.send_info(peer_id)

    def request_info(self, peer_id):
        self.send_info(peer_id, True)


# noinspection PyUnresolvedReferences
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
        self.messages_list.setSpacing(1)
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

    def message_context_menu_event(self, _):
        message_item: QListWidgetItem = self.messages_list.currentItem()
        if message_item:
            message_widget: MessageItemWidget = self.messages_list.itemWidget(message_item)
            # same thing
            # noinspection PyAttributeOutsideInit
            self.menu = QMenu(self)
            reply_action = QAction('Reply', self)
            forward_action = QAction('Forward', self)
            delete_action = QAction('Delete', self)
            delete_action.triggered.connect(lambda: delete_message_item_selected_callback(self.messages_list, message_item))

            self.menu.addAction(reply_action)
            self.menu.addAction(forward_action)
            if message_widget.message.mine:
                edit_action = QAction('Edit', self)
                edit_action.triggered.connect(lambda: edit_message_item_selected_callback(self, message_widget))
                self.menu.addAction(edit_action)
            self.menu.addAction(delete_action)
            # add other required actions
            self.menu.popup(QCursor.pos())


if __name__ == '__main__':
    if platform.system() == "Windows":
        import ctypes

        win_app_id = 'arterialist.core_messenger'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(win_app_id)

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
