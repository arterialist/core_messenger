import hashlib
import uuid

from client.models.base import Jsonable


class Peer(Jsonable):
    def __init__(self, ip: str, port: int, peer_id: str = None):
        self.ip = ip
        self.port = port
        self.peer_id = peer_id if peer_id else hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()


class Client(Peer):
    def __init__(self, ip: str, port: int, nickname: str = None, peer_id: str = None):
        super().__init__(ip, port, peer_id)
        self.nickname = nickname

    @staticmethod
    def from_peer(peer: Peer, nickname: str = None):
        return Client(peer.ip, peer.port, nickname, peer.peer_id)


class Server(Peer):
    def __init__(self, ip: str, port: int, peer_id: str = None):
        super().__init__(ip, port, peer_id)

    @staticmethod
    def from_peer(peer: Peer):
        return Server(peer.ip, peer.port, peer.peer_id)
