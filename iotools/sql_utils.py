from client import client_base
from client.models.messages import Message
from iotools.sql_base import SQLManager, ColumnTypes


def create_dialog(host, port, chat_type, peer_id):
    SQLManager.get_instance("files/storage.db").add_record(
        "dialogs",
        ["host", "port", "chat_type", "peer_id"],
        [host, port, chat_type, peer_id])
    create_messages_table_for_dialog(peer_id)
    client_base.current_peer_id = peer_id


def delete_dialog(peer_id):
    SQLManager.get_instance("files/storage.db").delete_record(
        "dialogs", "peer_id='{}'".format(peer_id))
    delete_messages_table_for_dialog(peer_id)


def create_messages_table_for_dialog(peer_id):
    SQLManager.get_instance("files/storage.db").create_table(
        "messages_{}".format(peer_id),
        ["message_id", "timestamp", "text", "mine"],
        [ColumnTypes.TEXT, ColumnTypes.NUMERIC, ColumnTypes.TEXT, ColumnTypes.INTEGER])


def delete_messages_table_for_dialog(peer_id):
    SQLManager.get_instance("files/storage.db").delete_table("messages_{}".format(peer_id))


def save_message(peer_id, message):
    SQLManager.get_instance("files/storage.db").add_record(
        "messages_{}".format(peer_id),
        ["message_id", "timestamp", "text", "mine"],
        [message.message_id, message.timestamp, message.text.replace("'", "''"), 1 if message.mine else 0])


def delete_message(peer_id, message_id):
    SQLManager.get_instance("files/storage.db").delete_record(
        "messages_{}".format(peer_id),
        "message_id='{}'".format(message_id))


def get_messages(peer_id):
    messages = SQLManager.get_instance("files/storage.db").select_all("messages_{}".format(peer_id))
    res = list()
    for msg in messages:
        res.append(Message(message_id=msg[0], timestamp=msg[1], text=msg[2], mine=msg[3] == 1))
        
    return res
