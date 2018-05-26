from client import client_base
from client.models.messages import Message
from iotools.sql_base import SQLManager, ColumnTypes, DB_MESSAGING, DB_SETTINGS, DB_STORAGE
from models.storage import Settings, Storage


def init_databases():
    create_dialogs_table()
    create_settings_table()
    create_storage_table()


def save_databases(settings, storage):
    save_settings_to_db(settings)
    save_storage_to_db(storage)


def create_dialogs_table():
    SQLManager.get_instance(DB_MESSAGING) \
        .create_table("dialogs",
                      ["host", "port", "chat_type", "peer_id"],
                      [ColumnTypes.TEXT, ColumnTypes.NUMERIC, ColumnTypes.NUMERIC, ColumnTypes.TEXT])


def create_settings_table():
    SQLManager.get_instance(DB_SETTINGS) \
        .create_table("settings",
                      ["key", "value"],
                      [ColumnTypes.TEXT, ColumnTypes.TEXT])


def create_storage_table():
    SQLManager.get_instance(DB_STORAGE) \
        .create_table("storage",
                      ["key", "value"],
                      [ColumnTypes.TEXT, ColumnTypes.TEXT])


def get_settings_from_db():
    settings = Settings()
    for setting in SQLManager.get_instance(DB_SETTINGS).select_all("settings"):
        settings.set(setting[0], setting[1])

    return settings


def get_storage_from_db():
    storage = Storage()
    for pref in SQLManager.get_instance(DB_STORAGE).select_all("storage"):
        storage.set(pref[0], pref[1])

    return storage


def save_settings_to_db(settings):
    sql_manager = SQLManager.get_instance(DB_SETTINGS)

    for key, value in settings.iterate():
        if settings.is_new(key):
            sql_manager.add_record(
                "settings",
                ["key", "value"],
                [key, value])
        else:
            sql_manager.edit_record(
                "key='{}'".format(key),
                "settings",
                ["key", "value"],
                [key, value])


def save_storage_to_db(storage):
    sql_manager = SQLManager.get_instance(DB_STORAGE)

    for key, value in storage.iterate():
        if storage.is_new(key):
            sql_manager.add_record(
                "storage",
                ["key", "value"],
                [key, value])
        else:
            sql_manager.edit_record(
                "key='{}'".format(key),
                "storage",
                ["key", "value"],
                [key, value])


def create_dialog(host, port, chat_type, peer_id):
    SQLManager.get_instance(DB_MESSAGING).add_record(
        "dialogs",
        ["host", "port", "chat_type", "peer_id"],
        [host, port, chat_type, peer_id])
    create_messages_table_for_dialog(peer_id)
    client_base.current_peer_id = peer_id


def delete_dialog(peer_id):
    SQLManager.get_instance(DB_MESSAGING).delete_record(
        "dialogs", "peer_id='{}'".format(peer_id))
    delete_messages_table_for_dialog(peer_id)


def create_messages_table_for_dialog(peer_id):
    SQLManager.get_instance(DB_MESSAGING).create_table(
        "messages_{}".format(peer_id),
        ["message_id", "timestamp", "text", "mine"],
        [ColumnTypes.TEXT, ColumnTypes.NUMERIC, ColumnTypes.TEXT, ColumnTypes.INTEGER])


def delete_messages_table_for_dialog(peer_id):
    SQLManager.get_instance(DB_MESSAGING).delete_table("messages_{}".format(peer_id))


def save_message(peer_id, message):
    SQLManager.get_instance(DB_MESSAGING).add_record(
        "messages_{}".format(peer_id),
        ["message_id", "timestamp", "text", "mine"],
        [message.message_id, message.timestamp, message.text.replace("'", "''"), 1 if message.mine else 0])


def delete_message(peer_id, message_id):
    SQLManager.get_instance(DB_MESSAGING).delete_record(
        "messages_{}".format(peer_id),
        "message_id='{}'".format(message_id))


def get_messages(peer_id):
    messages = SQLManager.get_instance(DB_MESSAGING).select_all("messages_{}".format(peer_id))
    res = list()
    for msg in messages:
        res.append(Message(message_id=msg[0], timestamp=msg[1], text=msg[2], mine=msg[3] == 1))

    return res
