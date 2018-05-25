import hashlib
import uuid

from client.models.base import Jsonable
from tools import current_time


class Message(Jsonable):
    def __init__(self, message_id=None, timestamp=None, text=None, attachments=None, mine=False):
        self.message_id = message_id if message_id else hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()
        self.timestamp = timestamp if timestamp else current_time()
        self.text = text
        self.attachments = attachments
        self.mine = mine


class Attachment(Jsonable):
    def __init__(self, link=None):
        self.link = link


class Photo(Attachment):
    def __init__(self, link=None, image_format=None):
        super().__init__(link)
        self.image_format = image_format


class Audio(Attachment):
    def __init__(self, link, duration=None):
        super().__init__(link)
        self.duration = duration
