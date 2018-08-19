import hashlib
import uuid

from client.models.base import Jsonable


class Peer(Jsonable):
    def __init__(self, host: str, port: int, peer_id: str = None):
        self.host = host
        self.port = port
        self.peer_id = peer_id if peer_id else hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()


class Client(Peer):
    def __init__(self, host: str, port: int, nickname: str = None, peer_id: str = None):
        super().__init__(host, port, peer_id)
        self.nickname = nickname

    @staticmethod
    def from_peer(peer: Peer, nickname: str = None):
        return Client(peer.host, peer.port, nickname, peer.peer_id)


class Server(Peer):
    def __init__(self, host: str, port: int, peer_id: str = None):
        super().__init__(host, port, peer_id)

    @staticmethod
    def from_peer(peer: Peer):
        return Server(peer.host, peer.port, peer.peer_id)
