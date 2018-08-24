import base64
import json

from Crypto import Random
from Crypto.Cipher import AES

from client.models.packets import Packet
from .module import BaseModule, BasePreModule, processing_method, BasePostModule


class SendAsJSONModule(BaseModule):
    def __init__(self):
        super().__init__()

    def on_send(self, data):
        super().on_send(data)
        return data.to_json().encode('utf8')

    def on_receive(self, data, sock):
        super().on_receive(data, sock)
        return Packet.from_json_obj(json.loads(data))

    def disable(self):
        super().disable()
        self.enabled = True


class Base64EncodeModule(BasePreModule):
    def __init__(self):
        super().__init__()

    @processing_method
    def on_receive(self, data, sock):
        super().on_receive(data, sock)
        if data.message and data.message.text:
            data.message.text = base64.b64decode(data.message.text.encode()).decode()
        return data

    @processing_method
    def on_send(self, data):
        super().on_send(data)
        if data.message and data.message.text:
            data.message.text = base64.b64encode(data.message.text.encode()).decode()
        return data


class Base64SendModule(BasePostModule):
    def __init__(self):
        super().__init__()

    @processing_method
    def on_receive(self, data, sock):
        super().on_receive(data, sock)
        data = base64.b64decode(data)
        return data

    @processing_method
    def on_send(self, data):
        super().on_send(data)
        data = base64.b64encode(data)
        return data


class AES256SendModule(BasePostModule):
    def __init__(self, secret: str, enabled=True):
        super().__init__()
        self.secret = secret
        self.enabled = enabled

    BLOCK_SIZE = 16

    def _pad(self, data):
        return data + bytes((self.BLOCK_SIZE - len(data) % self.BLOCK_SIZE) * chr(self.BLOCK_SIZE - len(data) % self.BLOCK_SIZE), 'utf8')

    @staticmethod
    def _unpad(data):
        return data[:-ord(data[len(data) - 1:])]

    def encrypt(self, data):
        data = self._pad(data)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.secret, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(data))

    def decrypt(self, data):
        data = base64.b64decode(data)
        iv = data[:AES.block_size]
        cipher = AES.new(self.secret, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(data[AES.block_size:]))

    @processing_method
    def on_send(self, data):
        super().on_send(data)
        if len(self.secret) != self.BLOCK_SIZE:
            raise ValueError('Key length is invalid, must be 16 chars.')
        return self.encrypt(data)

    @processing_method
    def on_receive(self, data, sock):
        super().on_receive(data, sock)
        if len(self.secret) != self.BLOCK_SIZE:
            raise ValueError('Key length is invalid, must be 16 chars.')
        return self.decrypt(data)
