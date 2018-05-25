"""
this file is created to make functionality growth fast
"""


def socket_send_data(to, what, through=list()):
    for action in through:
        what = action.process(what)

    if to:
        to.sendall(what)


def socket_handle_received(from_s, what, through=list()):
    for action in through:
        what = action.process_s(what, from_s)

    return what
