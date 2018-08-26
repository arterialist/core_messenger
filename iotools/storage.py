from iotools.sql_utils import get_settings_from_db, get_storage_from_db
from models.storage import Settings


class AppStorage:
    __settings = None
    __storage = None

    @staticmethod
    def get_settings() -> Settings:
        if AppStorage.__settings:
            return AppStorage.__settings
        AppStorage.__settings = get_settings_from_db()
        return AppStorage.__settings

    @staticmethod
    def get_storage():
        if AppStorage.__storage:
            return AppStorage.__storage
        AppStorage.__storage = get_storage_from_db()
        return AppStorage.__storage
