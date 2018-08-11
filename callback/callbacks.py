import copy

from PyQt5.QtWidgets import QInputDialog, QMessageBox, QListWidget, QWidget

from client import client_base
from client.models.actions import *
from client.models.messages import Message, Data
from client.models.packets import Packet
from iotools.sql_utils import delete_dialog, save_message, create_dialog, get_messages, delete_message, edit_message, update_dialog_info
from tools import full_strip
from widgets.dialogs.dialogs_list import DialogItemWidget
from widgets.message_boxes.message_delete_box import DeleteMsgMessageBox
from widgets.messages.messages_list import MessageItemWidget


def new_dialog_click_callback(widget):
    while 1:
        host, ok = QInputDialog.getText(widget, "Host", 'Enter Host:')
        if ok:
            if len(full_strip(host)):
                break
        else:
            return

    while 1:
        port, ok = QInputDialog.getText(widget, "Port", 'Enter Port:')
        if ok:
            if len(port) \
                    and port.isdecimal() \
                    and int(port) < 65536 \
                    and int(port) not in (21, 22, 80, 443):
                break
        else:
            return

    client_base.p2p_connect(host, int(port))
    dialog = DialogItemWidget("", client_base.current_connection_address[0], client_base.current_connection_address[1], 0)
    create_dialog(host, port, 0, dialog.peer_id)
    dialogs_list = widget.parentWidget().dialogs_list
    dialogs_list.addItem(dialog)
    dialogs_list.setCurrentItem(dialog)
    client_base.current_peer_id = dialog.peer_id
    messages_list = widget.parentWidget().parentWidget().parentWidget().opened_dialog_frame.messages_list
    messages_list.clear()


def dialog_item_changed_callback(current, window):
    messages_list = window.centralWidget().opened_dialog_frame.messages_list
    messages_list.clear()
    if current:
        messages = get_messages(current.peer_id)

        for message in messages:
            messages_list.addItem(MessageItemWidget(message))


def send_button_clicked_callback(widget):
    if client_base.current_peer_id:
        message_text = full_strip(widget.message_input.toPlainText())
        widget.message_input.clear()
        if not len(message_text):
            return

        messages_list = widget.parentWidget().parentWidget().messages_list
        message = Message(text=message_text, mine=True)
        save_message(client_base.current_peer_id, message)
        messages_list.addItem(MessageItemWidget(message))
        messages_list.scrollToBottom()
        msg_copy = copy.deepcopy(message)
        msg_copy.mine = False
        client_base.send_message(Packet(action=NewMessageAction(), message=msg_copy))


def toggle_listening_callback():
    client_base.socket_listen_off() if client_base.listening else client_base.socket_listen_on()


def handle_incoming_connection_callback(widget):
    widget.incoming_connection.setHidden(False)
    address = client_base.incoming_connection_address
    widget.incoming_connection.connection_info.setText("Connection from {0}:{1}".format(address[0], address[1]))


def accept_incoming_connection():
    client_base.accept_connection()


def decline_incoming_connection():
    client_base.decline_connection()


def new_message_callback(packet, window):
    messages_list: QListWidget = window.centralWidget().opened_dialog_frame.messages_list

    action = packet.action.action  # yes, I know

    if action == "new":
        messages_list.addItem(MessageItemWidget(packet.message))
        messages_list.scrollToBottom()
        save_message(client_base.current_peer_id, packet.message)
    elif action == "delete":
        delete_message(client_base.current_peer_id, packet.message.message_id)
        for index in range(messages_list.count()):
            message_item: MessageItemWidget = messages_list.item(index)
            if message_item.message.message_id == packet.message.message_id:
                messages_list.takeItem(messages_list.row(message_item))
                break
    elif action == "edit":
        edit_message(client_base.current_peer_id, packet.message)
        for index in range(messages_list.count()):
            message_item: MessageItemWidget = messages_list.item(index)
            if message_item.message.message_id == packet.message.message_id:
                row = messages_list.row(message_item)
                messages_list.takeItem(row)
                messages_list.insertItem(row, MessageItemWidget(packet.message))
                break
    elif action == "info":
        nickname = packet.data.content["nickname"]
        port = packet.data.content["port"]
        update_dialog_info(nickname, port, client_base.current_peer_id)
        dialog_widget: DialogItemWidget = window.centralWidget().dialogs_list_frame.dialogs_list.currentItem()
        dialog_widget.nickname = nickname
        dialog_widget.port = port
        dialog_widget.update_ui()
        messages_list.viewport().setFocus()
        if packet.data.content["request"]:
            client_base.send_message(Packet(
                message=Message(text=""),
                action=PeerInfoAction(),
                data=Data(content={
                    "nickname": client_base.nickname,
                    "port": client_base.local_port,
                    "request": False
                })
            ))


def invalid_message_callback(reason, message):
    client_base.invalid_message_callback = None
    alert_box = QMessageBox()
    alert_box.setWindowTitle("Invalid message received")
    alert_box.setText("Reason:\n{}\n\nMessage:\n{}".format(reason, message))
    alert_box.setStandardButtons(QMessageBox.Ok)
    alert_box.exec_()
    client_base.invalid_message_callback = invalid_message_callback


def delete_dialog_callback(peer_id):
    delete_dialog(peer_id)
    client_base.disconnect()


def delete_message_item_selected_callback(messages_list, message):
    # that's ...
    dialogs_list = messages_list \
        .parentWidget() \
        .parentWidget() \
        .parentWidget() \
        .parentWidget() \
        .dialogs_list_frame \
        .dialogs_list
    dialog: DialogItemWidget = dialogs_list.currentItem()

    confirmation_dialog = DeleteMsgMessageBox(message.message.mine, dialog.nickname if len(dialog.nickname) else None)

    result = confirmation_dialog.exec_()

    if result[0] == QMessageBox.Ok:
        delete_message(dialog.peer_id, message.message.message_id)
        messages_list.takeItem(messages_list.row(message))
        if result[1]:
            delete_message_msg = Message(message_id=message.message.message_id, timestamp=0)
            client_base.send_message(Packet(action=DeleteMessageAction(), message=delete_message_msg))


def edit_message_item_selected_callback(opened_dialog: QWidget, message_item: MessageItemWidget):
    old_message: Message = message_item.message
    text_to_edit = old_message.text

    new_text, ok = QInputDialog.getText(opened_dialog, "New Text", 'Edit message text', text=text_to_edit)

    if ok and new_text != text_to_edit:
        message_item.setText(new_text)
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
        client_base.send_message(packet)
        message_item.message = new_message
        message_item.setText(new_text)
        edit_message(client_base.current_peer_id, new_message)
