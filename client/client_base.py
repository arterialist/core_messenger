import socket
import threading
from json import JSONDecodeError

from client import layers
from client.models.packets import Packet
from client.modules.default_modules import SendAsJSONModule

# load modules
loaded_modules = [SendAsJSONModule()]

nickname = None
local_port = None

sock = None
server_host = None
server_port = None

connected = False
listening = False

has_incoming_connection = False
incoming_connection = None
incoming_connection_address = None

current_connection = None
current_connection_address = None
current_peer_id = None
current_peer_nickname = None

incoming_message_thread = None
incoming_connection_thread = None
message_sending_thread = None

incoming_connection_callback = None
new_message_callback = None
invalid_message_callback = None


def init_socket():
    global sock, connected
    connected = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def incoming_connections_listener():
    global has_incoming_connection, incoming_connection, incoming_connection_address
    while 1:
        try:
            connection, address = sock.accept()
            incoming_connection = connection
            incoming_connection_address = address
            has_incoming_connection = True
            if incoming_connection_callback:
                incoming_connection_callback()
        except OSError:
            continue


def p2p_new_message_listener():
    global current_connection, connected
    while connected:
        data = current_connection.recv(4096)
        reason = None
        if data == b'':
            print('Connection closed')
            connected = False
            break
        try:
            recv_msg = Packet.from_json_obj(layers.socket_handle_received(current_connection, data.decode('utf8'), loaded_modules))
            recv_msg.message.mine = False
            if new_message_callback:
                new_message_callback(recv_msg)
            print(recv_msg.__dict__)
        except UnicodeDecodeError:
            reason = "Corrupted message"
        except JSONDecodeError:
            reason = "Received non-JSON message (raw connection?)"
        except KeyError:
            reason = "Invalid JSON schema"
        finally:
            if reason and invalid_message_callback:
                invalid_message_callback(reason, data.decode("utf8"))


def server_new_message_listener():
    global current_connection
    while connected:
        data = current_connection.recv(4096)
        try:
            if new_message_callback:
                new_message_callback('\n' + data.decode('utf8'))
            print('\n' + data.decode('utf8'))
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
    except socket.error as e:
        print('Bind failed.')
        print(e)
        return

    sock.listen(256)

    incoming_connection_thread = threading.Thread(target=incoming_connections_listener)
    incoming_connection_thread.setDaemon(True)
    incoming_connection_thread.start()
    listening = True


def p2p_connect(remote_host, remote_port):
    global current_connection, current_connection_address, incoming_message_thread, connected
    socket_listen_off()

    current_connection_address = (remote_host, remote_port)
    current_connection = sock
    try:
        sock.connect(current_connection_address)
    except ConnectionRefusedError:
        print('Client is offline')
        return

    connected = True
    incoming_message_thread = threading.Thread(target=p2p_new_message_listener)
    incoming_message_thread.setDaemon(True)
    incoming_message_thread.start()
    print('Connected to client')


def server_connect():
    global current_connection_address, current_connection, incoming_message_thread, connected
    socket_listen_off()

    current_connection_address = (server_host, server_port)
    current_connection = sock
    sock.connect(current_connection_address)

    connected = True
    incoming_message_thread = threading.Thread(target=server_new_message_listener)
    incoming_message_thread.setDaemon(True)
    incoming_message_thread.start()
    print('Connected to server')


def accept_connection():
    global current_connection, current_connection_address, connected, incoming_message_thread
    current_connection = incoming_connection
    current_connection_address = incoming_connection_address
    connected = True
    incoming_message_thread = threading.Thread(target=p2p_new_message_listener)
    incoming_message_thread.setDaemon(True)
    incoming_message_thread.start()


def decline_connection():
    global incoming_connection, incoming_connection_address
    incoming_connection.close()
    incoming_connection = None
    incoming_connection_address = None


def send_message(message):
    # pass your modules here
    layers.socket_send_data(current_connection, message, loaded_modules)


def disconnect():
    global current_connection, incoming_message_thread, incoming_connection_thread, connected, current_peer_id
    connected = False

    current_peer_id = None

    if current_connection:
        current_connection.detach()
        current_connection.close()

    if incoming_message_thread:
        incoming_message_thread.join(0)
    if incoming_connection_thread:
        incoming_connection_thread.join(0)


def finish():
    global sock, current_connection, incoming_message_thread, incoming_connection_thread, connected

    connected = False
    if sock:
        sock.detach()
        sock.close()

    if current_connection:
        current_connection.detach()
        current_connection.close()

    if incoming_message_thread:
        incoming_message_thread.join(0)
    if incoming_connection_thread:
        incoming_connection_thread.join(0)

    exit(0)
