from .module import BaseModule
import json


class SendAsJSONModule(BaseModule):
    def __init__(self):
        super().__init__()

    def process(self, data):
        super().process(data)

        return data.to_json().encode('utf8')

    def process_s(self, data, sock):
        super().process_s(data, sock)

        return json.loads(data)
