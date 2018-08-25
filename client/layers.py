"""
this file is created to make functionality growth fast
"""
import copy

from client.models.base import Jsonable
from client.modules.module import STATUS_ERROR, STATUS_DROP, BaseModule, STATUS_OK


def socket_send_data(to, what: Jsonable, modules: dict, error_callback=None):
    modules_copy = copy.deepcopy(modules)
    pre_send: list = modules_copy.get("model")
    post_send: list = modules_copy.get("binary")
    transformer: BaseModule = modules_copy.get("transformer")

    what_copy = copy.deepcopy(what)
    for action in pre_send:
        if not action.enabled:
            continue
        status_code, what_copy = action.on_send(what_copy)
        if status_code == STATUS_ERROR and error_callback:
            error_callback(action, what_copy)
            return what, status_code

        if status_code == STATUS_DROP:
            return what, status_code

    what_copy = transformer.on_send(what_copy)

    for action in post_send:
        if not action.enabled:
            continue
        status_code, what_copy = action.on_send(what_copy)
        if status_code == STATUS_ERROR and error_callback:
            error_callback(action, what_copy)
            return what, status_code

        if status_code == STATUS_DROP:
            return what, status_code

    if to:
        data_length = len(what_copy)
        if data_length > pow(2, 16):
            return what, STATUS_DROP
        to.sendall(bytes(f"{chr(64)}{str(data_length).zfill(6)}{chr(64)}", "utf8"))  # data length packet
        to.sendall(what_copy)


def socket_handle_received(from_s, what, modules: dict, error_callback=None):
    modules_copy = copy.deepcopy(modules)
    pre_send: list = modules_copy.get("model")
    pre_send = reversed(pre_send)
    post_send: list = modules_copy.get("binary")
    post_send = reversed(post_send)
    transformer: BaseModule = modules_copy.get("transformer")

    what_copy = copy.deepcopy(what)
    for action in post_send:
        if not action.enabled:
            continue
        status_code, what_copy = action.on_receive(what_copy, from_s)
        if status_code == STATUS_ERROR and error_callback:
            error_callback(action, what_copy)
            return what, status_code

        if status_code == STATUS_DROP:
            return what, status_code

    what_copy = transformer.on_receive(what_copy, from_s)

    for action in pre_send:
        if not action.enabled:
            continue
        status_code, what_copy = action.on_receive(what_copy, from_s)
        if status_code == STATUS_ERROR and error_callback:
            error_callback(action, what_copy)
            return what, status_code

        if status_code == STATUS_DROP:
            return what, status_code

    return what_copy, STATUS_OK
