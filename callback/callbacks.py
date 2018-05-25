import re

from PyQt5.QtWidgets import QInputDialog

from client import client_base
from client.models.actions import NewMessageAction
from client.models.messages import Message
from client.models.packets import Packet
from iotools.sql_utils import delete_dialog, save_message, create_dialog, get_messages
from tools import full_strip
from widgets.dialogs.dialogs_list import DialogItemWidget
from widgets.messages.messages_list import MessageItemWidget


def new_dialog_click_callback(widget):
    while 1:
        host, ok = QInputDialog.getText(widget, "Host", 'Enter Host:')
        if ok:
            ip_regexp = r"\b(?:(?:2(?:[0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9])\.){3}(?:(?:2([0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9]))\b"
            if len(full_strip(host)) and re.match(ip_regexp, full_strip(host)):
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
        print(current.peer_id)
        messages = get_messages(current.peer_id)

        for message in messages:
            messages_list.addItem(MessageItemWidget(message.mine, message.text))


def send_button_clicked_callback(widget):
    if client_base.current_peer_id:
        message_text = full_strip(widget.message_input.toPlainText())
        widget.message_input.clear()
        if not len(message_text):
            return

        messages_list = widget.parentWidget().parentWidget().messages_list
        messages_list.addItem(MessageItemWidget(True, message_text))
        messages_list.scrollToBottom()
        message = Message(text=message_text)
        client_base.send_message(Packet(action=NewMessageAction(), message=message))
        message.mine = True
        save_message(client_base.current_peer_id, message)


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
    print(packet)
    messages_list = window.centralWidget().opened_dialog_frame.messages_list
    messages_list.addItem(MessageItemWidget(packet.message.mine, packet.message.text))
    messages_list.scrollToBottom()
    save_message(client_base.current_peer_id, packet.message)


def delete_dialog_callback(peer_id):
    delete_dialog(peer_id)
    client_base.disconnect()
