import copy
import socket
import threading
from json import JSONDecodeError

from client import layers
from client.models.peers import Client, Server, Peer
from client.modules.default_modules import SendAsJSONModule, Base64EncodeModule

loaded_modules = [SendAsJSONModule(), Base64EncodeModule()]

nickname = None
local_port = None
sock = None
listening = False

has_incoming_connection = False
incoming_connection = None
incoming_connection_address = None

incoming_connection_thread = None
message_sending_thread = None

incoming_connection_callback = None
new_message_callback = None
invalid_message_callback = None
peer_disconnected_callback = None

peers = dict()

incoming_connections = dict()


class DummySocket:
    def close(self):
        pass


def init_socket():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# noinspection PyCallingNonCallable
def incoming_connections_listener():
    global has_incoming_connection, incoming_connection, incoming_connection_address
    while listening:
        try:
            connection, address = sock.accept()
            incoming_connections[address] = connection
            has_incoming_connection = True
            if incoming_connection_callback:
                incoming_connection_callback(address, connection)
        except OSError:
            continue


# noinspection PyCallingNonCallable
def p2p_new_message_listener(peer: Client, connection: socket):
    while peer.peer_id in peers.keys():
        try:
            data = connection.recv(4096)
        except OSError:
            continue
        reason = None
        if data == b'':
            print('Connection closed')
            if peer_disconnected_callback:
                peer_disconnected_callback()
            if peer.peer_id in peers.keys():
                peers.pop(peer.peer_id)
            break
        try:
            recv_msg = layers.socket_handle_received(connection, data.decode('utf8'), loaded_modules)
            if new_message_callback:
                new_message_callback(recv_msg, peer)
        except UnicodeDecodeError:
            reason = "Corrupted message"
        except JSONDecodeError:
            reason = "Received non-JSON message (raw connection?)"
        except KeyError:
            reason = "Invalid JSON schema"
        finally:
            if reason and invalid_message_callback:
                invalid_message_callback(reason, data.decode("utf8"), peer)


# noinspection PyCallingNonCallable
def server_new_message_listener(peer: Server):
    while peer.peer_id in peers.keys():
        data = sock.recv(4096)
        try:
            if new_message_callback:
                new_message_callback('\n' + data.decode('utf8'), peer)
        except UnicodeDecodeError:
            print('Corrupted message')


def socket_listen_off():
    global listening
    sock.close()
    if incoming_connection_thread:
        incoming_connection_thread.join(0)
    init_socket()
    listening = False


def socket_listen_on():
    global sock, incoming_connection_thread, listening
    socket_listen_off()

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', local_port))
    except socket.error:
        print('Bind failed.')
        return

    sock.listen(1024)

    listening = True
    incoming_connection_thread = threading.Thread(target=incoming_connections_listener)
    incoming_connection_thread.setDaemon(True)
    incoming_connection_thread.start()


def p2p_connect(remote_host: str, remote_port: int) -> tuple:
    if len(peers.keys()) == 1024:
        return "Reached maximum connections limit", None

    try:
        sock.connect((remote_host, remote_port))
    except ConnectionRefusedError:
        return "Client is offline", None
    except socket.gaierror as e:
        return str(e), None

    sock.setblocking(False)
    peer = Client(remote_host, remote_port)
    incoming_message_thread = threading.Thread(target=p2p_new_message_listener, args=[peer, sock])
    incoming_message_thread.setDaemon(True)

    peers[peer.peer_id] = {
        "peer": peer,
        "thread": incoming_message_thread,
        "socket": sock
    }

    incoming_message_thread.start()
    print('Connected to client')
    return None, peer


def server_connect(remote_host: str, remote_port: int) -> tuple:
    if len(peers.keys()) == 1024:
        return "Reached maximum connections limit", None

    try:
        sock.connect((remote_host, remote_port))
    except ConnectionRefusedError:
        return "Server is offline", None
    except socket.gaierror as e:
        return str(e), None

    sock.setblocking(False)
    peer = Server(remote_host, remote_port)
    incoming_message_thread = threading.Thread(target=server_new_message_listener, args=[peer, sock])
    incoming_message_thread.setDaemon(True)

    peers[peer.peer_id] = {
        "peer": peer,
        "thread": incoming_message_thread,
        "socket": sock
    }

    incoming_message_thread.start()
    print('Connected to server')
    return None, peer


def accept_connection(address) -> tuple:
    connection = incoming_connections.get(address, None)

    if not connection:
        return "Invalid address", None

    incoming_connections.pop(address)
    connection.setblocking(False)
    peer = Peer(address[0], address[1])
    incoming_message_thread = threading.Thread(target=p2p_new_message_listener, args=[peer, connection])

    peers[peer.peer_id] = {
        "peer": peer,
        "thread": incoming_message_thread,
        "socket": connection
    }

    incoming_message_thread.setDaemon(True)
    incoming_message_thread.start()

    return None, peer


def decline_connection(address):
    if address in incoming_connections.keys():
        incoming_connections.get(address, DummySocket()).close()
        incoming_connections.pop(address)


def send_message(peer_id, message):
    if peer_id in peers.keys():
        # pass your modules here
        layers.socket_send_data(peers.get(peer_id).get("socket"), message, loaded_modules)


def disconnect(peer: Peer):
    if peer.peer_id in peers.keys():
        peers[peer.peer_id]["thread"].join(0)
        peers[peer.peer_id]["socket"].shutdown(socket.SHUT_RDWR)
        peers[peer.peer_id]["socket"].close()
        peers.pop(peer.peer_id)


def finish():
    global sock, incoming_connection_thread

    peer_ids = copy.deepcopy(list(peers.keys()))

    for peer_id in peer_ids:
        peers[peer_id]["thread"].join(0)
        peers.pop(peer_id)

    if sock:
        sock.detach()
        sock.close()

    if incoming_connection_thread:
        incoming_connection_thread.join(0)

    exit(0)
