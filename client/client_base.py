import copy
import socket
import threading
from json import JSONDecodeError

from client import layers
from client.models.actions import ConnectAction
from client.models.messages import Message
from client.models.packets import Packet
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
sockets = dict()


def init_socket():
    global sock
    sock = socket.socket()


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
            if (peer.host, peer.port) in sockets.keys():
                sockets.pop((peer.host, peer.port))
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
def server_new_message_listener(peer: Server, connection: socket):
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
            if (peer.host, peer.port) in sockets.keys():
                sockets.pop((peer.host, peer.port))
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


def p2p_connect(remote_host: str, remote_port: int, peer_id_override: str = None) -> tuple:
    if len(peers.keys()) == 1024:
        return "Reached maximum connections limit", None

    address = (remote_host, remote_port)

    if address in sockets.keys():
        connection, connected = sockets[address]["connection"], sockets[address]["used"]
        if connected:
            return "Already connected to {}:{}".format(address[0], address[1]), None
        sockets[address]["used"] = True
    else:
        connection = socket.socket()
        try:
            connection.connect(address)
        except ConnectionRefusedError:
            return "Client is offline", None
        except socket.gaierror as e:
            return str(e), None
        connection.settimeout(30)
        sockets[address] = {
            "connection": connection,
            "used": True
        }

    peer = Client(remote_host, remote_port)

    if peer_id_override:
        peer.peer_id = peer_id_override

    incoming_message_thread = threading.Thread(target=p2p_new_message_listener, args=[peer, connection])
    incoming_message_thread.setDaemon(True)

    peers[peer.peer_id] = {
        "peer": peer,
        "thread": incoming_message_thread,
        "socket": connection
    }

    incoming_message_thread.start()
    print('Connected to client')
    return None, peer


def server_connect(remote_host: str, remote_port: int, peer_id_override: str = None) -> tuple:
    if len(peers.keys()) == 1024:
        return "Reached maximum connections limit", None

    address = (remote_host, remote_port)

    if address in sockets.keys():
        connection, connected = sockets[address]["connection"], sockets[address]["used"]
        if connected:
            return "Already connected to {}:{}".format(address[0], address[1]), None
        sockets[address]["used"] = True
    else:
        connection = socket.socket()
        try:
            connection.connect(address)
        except ConnectionRefusedError:
            return "Server is offline", None
        except socket.gaierror as e:
            return str(e), None
        connection.settimeout(30)
        sockets[address] = {
            "connection": connection,
            "used": True
        }

    peer = Server(remote_host, remote_port)

    if peer_id_override:
        peer.peer_id = peer_id_override

    incoming_message_thread = threading.Thread(target=server_new_message_listener, args=[peer, connection])
    incoming_message_thread.setDaemon(True)

    peers[peer.peer_id] = {
        "peer": peer,
        "thread": incoming_message_thread,
        "socket": connection
    }

    incoming_message_thread.start()

    send_message(
        peer.peer_id,
        Packet(
            action=ConnectAction(),
            message=Message()
        )
    )
    print('Connected to server')
    return None, peer


def accept_connection(address) -> tuple:
    connection = incoming_connections.get(address, None)

    if not connection:
        return "Invalid address", None

    incoming_connections.pop(address)
    connection.settimeout(30)
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
        incoming_connections[address].close()
        incoming_connections.pop(address)


def send_message(peer_id, message):
    if peer_id in peers.keys():
        # pass your modules here
        layers.socket_send_data(peers.get(peer_id).get("socket"), message, loaded_modules)


def disconnect(peer: Peer):
    if peer.peer_id in peers.keys():
        peers[peer.peer_id]["thread"].join(0)
        try:
            peers.pop(peer.peer_id)
        except KeyError:
            pass
    if (peer.host, peer.port) in sockets.keys():
        sockets[(peer.host, peer.port)]["used"] = False


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
