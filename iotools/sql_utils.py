from client.models.messages import Message
from iotools.sql_base import SQLManager, ColumnTypes, DB_MESSAGING, DB_SETTINGS, DB_STORAGE, Query
from models.storage import Settings, Storage, Category, Setting


def init_databases():
    create_dialogs_table()
    create_settings_table()
    create_storage_table()
    create_drafts_table()


def save_databases(settings: Settings, storage: Storage):
    save_settings_to_db(settings)
    save_storage_to_db(storage)


def create_dialogs_table():
    SQLManager.get_instance(DB_MESSAGING) \
        .create_table("dialogs",
                      ["host", "port", "chat_type", "peer_id", "nickname", "listening_port"],
                      [ColumnTypes.TEXT, ColumnTypes.NUMERIC, ColumnTypes.NUMERIC, ColumnTypes.TEXT, ColumnTypes.TEXT, ColumnTypes.NUMERIC])


def create_category_table(category: Category):
    sql_manager = SQLManager.get_instance(DB_SETTINGS)
    if not sql_manager.has_table(category.name):
        sql_manager.add_record("_categories", ["name", "display_name"], [category.name, category.display_name])

    sql_manager.create_table(category.name,
                             ["name", "value", "type", "display_name"],
                             [ColumnTypes.TEXT, ColumnTypes.TEXT, ColumnTypes.NUMERIC, ColumnTypes.TEXT])


def create_settings_table():
    sql_manager = SQLManager.get_instance(DB_SETTINGS)
    sql_manager.create_table("_categories",
                             ["name", "display_name"],
                             [ColumnTypes.TEXT, ColumnTypes.TEXT])

    create_category_table(Category("general", "General"))


def create_storage_table():
    SQLManager.get_instance(DB_STORAGE) \
        .create_table("storage",
                      ["name", "value"],
                      [ColumnTypes.TEXT, ColumnTypes.TEXT])


def create_drafts_table():
    manager = SQLManager.get_instance(DB_MESSAGING)
    manager.create_table("drafts",
                         ["peer_id", "draft"],
                         [ColumnTypes.TEXT, ColumnTypes.TEXT])

    for _, _, _, peer_id, _, _ in manager.select_all("dialogs"):
        manager.add_record("drafts", ["peer_id", "draft"], [peer_id, ""])


def create_draft(peer_id: str):
    SQLManager.get_instance(DB_MESSAGING) \
        .add_record("drafts",
                    ["peer_id", "draft"],
                    [peer_id, ""])


def save_draft(peer_id: str, draft: str):
    SQLManager.get_instance(DB_MESSAGING) \
        .edit_record(Query(["peer_id"], [peer_id]),
                     "drafts",
                     ["draft"], [draft])


def get_draft(peer_id: str):
    return SQLManager.get_instance(DB_MESSAGING).select_single("peer_id", peer_id, "drafts")[1]


def get_settings_from_db() -> Settings:
    settings = Settings()
    for category in SQLManager.get_instance(DB_SETTINGS).select_all("_categories"):
        for setting in SQLManager.get_instance(DB_SETTINGS).select_all(category[0]):
            settings.set(
                Category(category[0], category[1]),
                Setting(setting[0], setting[1], setting[2], setting[3]),
                init=True)

    return settings


def get_storage_from_db() -> Storage:
    storage = Storage()
    for pref in SQLManager.get_instance(DB_STORAGE).select_all("storage"):
        storage.set(pref[0], pref[1], init=True)

    return storage


def save_settings_to_db(settings: Settings):
    sql_manager = SQLManager.get_instance(DB_SETTINGS)

    for category, setting in settings.iterate():
        if settings.is_new_category(category):
            create_category_table(category)

        if settings.is_new(category, setting):
            sql_manager.add_record(
                category.name,
                ["name", "value", "type", "display_name"],
                [setting.key, setting.value, setting.setting_type, setting.display_name])
        else:
            sql_manager.edit_record(
                Query(["name"], [setting.key]),
                category.name,
                ["name", "value"],
                [setting.key, setting.value])


def save_storage_to_db(storage: Storage):
    sql_manager = SQLManager.get_instance(DB_STORAGE)

    for key, value in storage.iterate():
        if storage.is_new(key):
            sql_manager.add_record(
                "storage",
                ["name", "value"],
                [key, value])
        else:
            sql_manager.edit_record(
                Query(["name"], [key]),
                "storage",
                ["name", "value"],
                [key, value])


def create_dialog(host: str, port: str, chat_type: int, peer_id: str):
    sql_manager = SQLManager.get_instance(DB_MESSAGING)
    sql_manager.add_record(
        "dialogs",
        ["host", "port", "chat_type", "peer_id", "nickname", "listening_port"],
        [host, port, chat_type, peer_id, "", ""])
    create_messages_table_for_dialog(peer_id)
    create_draft(peer_id)


def update_dialog(host: str, port: int, chat_type: int, peer_id: str):
    SQLManager.get_instance(DB_MESSAGING).edit_record(
        Query(["peer_id"], [peer_id]),
        "dialogs",
        ["host", "port", "chat_type"],
        [host, port, chat_type]
    )


def update_dialog_info(nickname: str, port: int, peer_id: str):
    SQLManager.get_instance(DB_MESSAGING).edit_record(
        Query(["peer_id"], [peer_id]),
        "dialogs",
        ["nickname", "listening_port"],
        [nickname, port]
    )


def delete_dialog(peer_id: str):
    SQLManager.get_instance(DB_MESSAGING).delete_record(
        "dialogs", f"peer_id='{peer_id}'")
    delete_messages_table_for_dialog(peer_id)


def create_messages_table_for_dialog(peer_id: str):
    SQLManager.get_instance(DB_MESSAGING).create_table(
        f"messages_{peer_id}",
        ["message_id", "timestamp", "text", "mine", "service", "from_peer_id", "from_nickname"],
        [ColumnTypes.TEXT, ColumnTypes.NUMERIC, ColumnTypes.TEXT, ColumnTypes.INTEGER, ColumnTypes.INTEGER, ColumnTypes.TEXT, ColumnTypes.TEXT])


def delete_messages_table_for_dialog(peer_id: str):
    SQLManager.get_instance(DB_MESSAGING).delete_table(f"messages_{peer_id}")


def save_message(peer_id: str, message: Message, from_peer_id: str, service: bool = False, from_nickname: str = ""):
    SQLManager.get_instance(DB_MESSAGING).add_record(
        f"messages_{peer_id}",
        ["message_id", "timestamp", "text", "mine", "service", "from_peer_id", "from_nickname"],
        [message.message_id, message.timestamp, message.text.replace("'", "''"), 1 if message.mine else 0, 1 if service else 0, from_peer_id,
         from_nickname])


def delete_message(peer_id: str, message_id: str):
    SQLManager.get_instance(DB_MESSAGING).delete_record(
        f"messages_{peer_id}",
        f"message_id='{message_id}'")


def edit_message(peer_id: str, message: Message):
    SQLManager.get_instance(DB_MESSAGING).edit_record(
        Query(["message_id"], [message.message_id]),
        f"messages_{peer_id}",
        ["text"],
        [message.text]
    )


def get_messages(peer_id):
    messages = SQLManager.get_instance(DB_MESSAGING).select_all(f"messages_{peer_id}")
    res = list()
    for msg in messages:
        res.append((Message(message_id=msg[0], timestamp=msg[1], text=msg[2], mine=msg[3] == 1), bool(msg[4]), msg[5], msg[6]))

    return res
