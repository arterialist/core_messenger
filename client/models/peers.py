import hashlib
import uuid

from client.models.base import Jsonable


class Peer(Jsonable):
    def __init__(self, ip: str, port: int, peer_id: str = None):
        self.ip = ip
        self.port = port
        self.peer_id = peer_id if peer_id else hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()


class Client(Peer):
    def __init__(self, ip: str, port: int, nickname: str, peer_id: str = None):
        super().__init__(ip, port, peer_id)
        self.nickname = nickname


class Server(Peer):
    def __init__(self, ip: str, port: int, peer_id: str = None):
        super().__init__(ip, port, peer_id)
