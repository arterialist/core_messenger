import base64
import json

from client.models.packets import Packet
from .module import BaseModule


class SendAsJSONModule(BaseModule):
    def __init__(self):
        super().__init__()

    def process(self, data):
        super().process(data)

        return data.to_json().encode('utf8')

    def process_s(self, data, sock):
        super().process_s(data, sock)

        return Packet.from_json_obj(json.loads(data))

    def disable(self):
        super().disable()
        self.enabled = True


class Base64EncodeModule(BaseModule):
    def __init__(self):
        super().__init__()

    def process_s(self, data, sock):
        super().process_s(data, sock)
        data.message.text = base64.b64decode(data.message.text.encode()).decode()
        return data

    def process(self, data):
        super().process(data)
        data.message.text = base64.b64encode(data.message.text.encode()).decode()
        return data
