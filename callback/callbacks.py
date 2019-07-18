import copy
from time import sleep
from typing import Optional

from PyQt5.QtWidgets import QInputDialog, QMessageBox, QListWidget, QWidget, QListWidgetItem, QAbstractItemView, QTextEdit

from client import client_base
from client.models.actions import *
from client.models.messages import Message, Data
from client.models.packets import Packet
from client.models.peers import Peer, Client
from iotools.sql_utils import delete_dialog, save_message, create_dialog, get_messages, delete_message, edit_message, update_dialog_info, save_draft, \
    get_draft, create_drafts_table
from iotools.storage import AppStorage
from models.storage import Category
from tools import full_strip
from widgets.dialogs.dialogs_list import DialogItemWidget
from widgets.message_boxes.message_delete_box import DeleteMsgMessageBox
from widgets.messages.messages_list import MessageItemWidget


def get_address(widget) -> Optional[tuple]:
    while 1:
        host, ok = QInputDialog.getText(widget, "Host", 'Enter Host:')
        if ok:
            if len(full_strip(host)):
                break
        else:
            return None

    while 1:
        port, ok = QInputDialog.getText(widget, "Port", 'Enter Port:')
        if ok:
            if len(port) \
                    and port.isdecimal() \
                    and int(port) < 65536 \
                    and int(port) not in (21, 22, 80, 443):
                break
        else:
            return None

    return host, int(port)


def new_dialog_click_callback(widget):
    address = get_address(widget)

    if not address:
        return

    error, peer = client_base.p2p_connect(address[0], address[1])

    if peer:
        dialog = DialogItemWidget("", peer.host, peer.port, 0, peer_id=peer.peer_id)
        create_dialog(address[0], address[1], 0, peer.peer_id)
        dialogs_list = widget.parentWidget().dialogs_list
        dialogs_list.addItem(dialog)
        dialogs_list.setCurrentItem(dialog)
        messages_list = widget.parentWidget().parentWidget().parentWidget().opened_dialog_frame.messages_list
        messages_list.clear()
    else:
        alert_box = QMessageBox()
        alert_box.setWindowTitle("Error")
        alert_box.setText(error)
        alert_box.setStandardButtons(QMessageBox.Ok)
        alert_box.exec_()


def new_chat_click_callback(widget):
    address = get_address(widget)

    if not address:
        return

    error, peer = client_base.server_connect(address[0], address[1])

    if peer:
        dialog = DialogItemWidget("", peer.host, peer.port, 2, peer_id=peer.peer_id)
        create_dialog(address[0], address[1], 2, peer.peer_id)
        dialogs_list = widget.parentWidget().dialogs_list
        dialogs_list.addItem(dialog)
        dialogs_list.setCurrentItem(dialog)
        messages_list = widget.parentWidget().parentWidget().parentWidget().opened_dialog_frame.messages_list
        messages_list.clear()
    else:
        alert_box = QMessageBox()
        alert_box.setWindowTitle("Error")
        alert_box.setText(error)
        alert_box.setStandardButtons(QMessageBox.Ok)
        alert_box.exec_()


def dialog_item_changed_callback(current: DialogItemWidget, previous: DialogItemWidget, window):
    messages_list: QListWidget = window.centralWidget().opened_dialog_frame.messages_list
    message_input: QTextEdit = window.centralWidget().opened_dialog_frame.message_input.message_input
    scroll_type = QAbstractItemView.ScrollPerItem
    if bool(int(AppStorage.get_settings().get(Category("ui", "User Interface"), "enable_smooth_scroll").value)):
        scroll_type = QAbstractItemView.ScrollPerPixel
    messages_list.setVerticalScrollMode(scroll_type)
    messages_list.clear()

    if previous:
        save_draft(previous.peer_id, full_strip(message_input.toPlainText()))
    message_input.clear()

    if current:
        messages = get_messages(current.peer_id)
        draft = get_draft(current.peer_id)
        message_input.setText(draft)

        for message in messages:
            message_item_widget = MessageItemWidget(message[0], message[2], message[3], service=message[1],
                                                    previous_peer_id=messages[messages.index(message) - 1][2] if messages[0] != message else None)
            item = QListWidgetItem()
            item.setSizeHint(message_item_widget.sizeHint())
            messages_list.addItem(item)
            messages_list.setItemWidget(item, message_item_widget)
    messages_list.scrollToBottom()


def send_button_clicked_callback(widget, peer_id):
    if peer_id not in client_base.peers.keys():
        return

    message_text = full_strip(widget.message_input.toPlainText())
    widget.message_input.clear()
    if not len(message_text):
        return

    messages_list = widget.parentWidget().parentWidget().messages_list
    message = Message(text=message_text, mine=True)
    save_message(peer_id, message, "", from_nickname=client_base.nickname)
    message_item_widget = MessageItemWidget(message, "", client_base.nickname)
    item = QListWidgetItem()
    item.setSizeHint(message_item_widget.sizeHint())
    messages_list.addItem(item)
    messages_list.setItemWidget(item, message_item_widget)
    messages_list.scrollToBottom()
    msg_copy = copy.deepcopy(message)
    msg_copy.mine = False
    client_base.send_message(peer_id, Packet(action=NewMessageAction(), message=msg_copy))


def toggle_listening_callback():
    client_base.socket_listen_off() if client_base.listening else client_base.socket_listen_on()


def handle_incoming_connection_callback(incoming_list_widget: QListWidget, address):
    item = QListWidgetItem("{}:{}".format(address[0], address[1]))
    incoming_list_widget.addItem(item)


def accept_incoming_connection(widget, address):
    info = client_base.accept_connection(address)

    if info[1]:
        peer_id = info[1].peer_id
        dialog = DialogItemWidget("", address[0], address[1], 0, peer_id=peer_id)
        create_dialog(address[0], address[1], 0, peer_id)
        create_drafts_table()
        dialogs_list = widget.dialogs_list
        dialogs_list.addItem(dialog)
        dialogs_list.setCurrentItem(dialog)

        connection_item = widget.incoming_list.currentItem()
        widget.incoming_list.takeItem(widget.incoming_list.row(connection_item))
        widget.tabs.setCurrentIndex(0)


def decline_incoming_connection(widget, address):
    client_base.decline_connection(address)
    connection_item = widget.incoming_list.currentItem()
    widget.incoming_list.takeItem(widget.incoming_list.row(connection_item))


def new_message_callback(packet: Packet, peer: Peer, window):
    messages_list: QListWidget = window.centralWidget().opened_dialog_frame.messages_list

    action = packet.action.action  # yes, I know
    peer_id = packet.data.content.get("from_peer") if packet.data and packet.data.content.get("from_peer", None) else peer.peer_id
    previous_peer_id = messages_list.itemWidget(messages_list.item(messages_list.count() - 1)).from_peer_id if messages_list.count() > 0 else None

    if action == NewMessageAction().action:
        message_item_widget = MessageItemWidget(packet.message, peer_id, peer.nickname if type(peer) is Client else "",
                                                previous_peer_id=previous_peer_id)
        item = QListWidgetItem()
        item.setSizeHint(message_item_widget.sizeHint())
        messages_list.addItem(item)
        messages_list.setItemWidget(item, message_item_widget)
        messages_list.scrollToBottom()
        save_message(peer.peer_id, packet.message, peer_id, peer.nickname if type(peer) is Client else "")

    elif action == DeleteMessageAction().action:
        delete_message(peer.peer_id, packet.message.message_id)
        for index in range(messages_list.count()):
            message_item = messages_list.item(index)
            message_item_widget: MessageItemWidget = messages_list.itemWidget(message_item)
            if message_item_widget.message.message_id == packet.message.message_id:
                messages_list.takeItem(messages_list.row(message_item))
                break

    elif action == EditMessageAction().action:
        edit_message(peer.peer_id, packet.message)
        for index in range(messages_list.count()):
            message_item = messages_list.item(index)
            message_item_widget: MessageItemWidget = messages_list.itemWidget(message_item)
            if message_item_widget.message.message_id == packet.message.message_id:
                message_item_widget.init_ui()
                break

    elif action == PeerInfoAction().action:
        nickname = packet.data.content["nickname"]
        port = packet.data.content["port"]
        update_dialog_info(nickname, port, peer_id)
        dialog_widget: DialogItemWidget = window.centralWidget().dialogs_list_frame.dialogs_list.currentItem()
        dialog_widget.nickname = nickname
        dialog_widget.port = port
        dialog_widget.update_ui()
        messages_list.viewport().setFocus()
        if packet.data.content["request"]:
            client_base.send_message(dialog_widget.peer_id, Packet(
                message=Message(text=""),
                action=PeerInfoAction(),
                data=Data(content={
                    "nickname": client_base.nickname,
                    "port": client_base.local_port,
                    "request": False
                })
            ))

    elif action == ServiceAction().action:
        message_item_widget = MessageItemWidget(packet.message, peer.peer_id, "", True)
        item = QListWidgetItem()
        item.setSizeHint(message_item_widget.sizeHint())
        messages_list.addItem(item)
        messages_list.setItemWidget(item, message_item_widget)
        messages_list.scrollToBottom()
        save_message(peer.peer_id, packet.message, peer.peer_id, True)

    elif action == DisconnectAction().action:
        pass
        # TODO peer has disconnected

    elif action == ConnectAction().action:
        if packet.data:  # indicates that it's just reconnect
            return
        # pretend that we are server
        client_base.send_message(
            peer_id,
            Packet(
                action=ServiceAction(),
                message=Message(text="Wrong button, buddy :)")
            )
        )
        client_base.peers[peer_id]["socket"].close()
        client_base.peers.pop(peer_id)
        sleep(0.5)
        dialogs_list = window.centralWidget().dialogs_list_frame.dialogs_list
        dialogs_list.takeItem(dialogs_list.row(dialogs_list.currentItem()))
        delete_dialog(peer.peer_id)


def invalid_message_callback(reason, message, peer):
    client_base.invalid_message_callback = None
    alert_box = QMessageBox()
    alert_box.setWindowTitle("Invalid message received")
    alert_box.setText("Reason:\n{}\nFrom:{}:{}\n\nMessage:\n{}".format(reason, peer.host, peer.port, message))
    alert_box.setStandardButtons(QMessageBox.Ok)
    alert_box.exec_()
    client_base.invalid_message_callback = invalid_message_callback


def delete_dialog_callback(peer_id: str, host: str, port: int):
    client_base.send_message(
        peer_id,
        Packet(
            action=DisconnectAction(),
            message=Message()
        )
    )
    delete_dialog(peer_id)
    client_base.disconnect(Peer(host, port, peer_id))


def delete_message_item_selected_callback(messages_list: QListWidget, message_item):
    # that's ...
    dialogs_list = messages_list \
        .parentWidget() \
        .parentWidget() \
        .parentWidget() \
        .parentWidget() \
        .dialogs_list_frame \
        .dialogs_list
    dialog: DialogItemWidget = dialogs_list.currentItem()

    message_item_widget = messages_list.itemWidget(message_item)
    confirmation_dialog = DeleteMsgMessageBox(message_item_widget.message.mine, dialog.nickname if len(dialog.nickname) else None)

    result = confirmation_dialog.exec_()

    if result[0] == QMessageBox.Ok:
        delete_message(dialog.peer_id, message_item_widget.message.message_id)
        messages_list.takeItem(messages_list.row(message_item))
        if result[1]:
            delete_message_msg = Message(message_id=message_item_widget.message.message_id, timestamp=0)
            client_base.send_message(dialog.peer_id, Packet(action=DeleteMessageAction(), message=delete_message_msg))


def edit_message_item_selected_callback(opened_dialog: QWidget, message_item: MessageItemWidget):
    old_message: Message = message_item.message
    text_to_edit = old_message.text

    new_text, ok = QInputDialog.getText(opened_dialog, "New Text", 'Edit message text', text=text_to_edit)

    if ok and new_text != text_to_edit:
        dialog = opened_dialog.parentWidget().parentWidget().dialogs_list_frame.dialogs_list.currentItem()
        current_peer_id = dialog.peer_id
        message_item.message.text = new_text
        message_item.refresh()
        new_message = Message(
            old_message.message_id,
            old_message.timestamp,
            new_text,
            old_message.attachments,
            True
        )
        msg_copy = copy.deepcopy(new_message)
        msg_copy.mine = False
        packet = Packet(
            action=EditMessageAction(),
            message=msg_copy
        )
        client_base.send_message(current_peer_id, packet)
        message_item.message = new_message
        edit_message(current_peer_id, new_message)
