from time import time

from client.common import get_id_hash
from client.models.base import Jsonable


class Message(Jsonable):
    def __init__(self, message_id: str = None, timestamp: int = None, text: str = None, attachments: list = None, mine: bool = False):
        self.message_id = message_id if message_id else get_id_hash()
        self.timestamp = timestamp if timestamp else int(round(time() * 1000))
        self.text = text
        self.attachments = attachments
        self.mine = mine


class Attachment(Jsonable):
    def __init__(self, link: str = None, content_length: int = 0, name: str = None):
        self.link = link
        self.content_length = content_length
        self.name = name


class Photo(Attachment):
    def __init__(self, link: str = None, image_format: str = None):
        super().__init__(link)
        self.image_format = image_format


class Audio(Attachment):
    def __init__(self, link: str, duration: int = None):
        super().__init__(link)
        self.duration = duration


class Data(Jsonable):
    def __init__(self, content: dict = None):
        if content is None:
            content = {}
        self.content = content
