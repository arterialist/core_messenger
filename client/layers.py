"""
this file is created to make functionality growth fast
"""
import copy


def socket_send_data(to, what, through=list()):
    through_copy = copy.deepcopy(through)
    through_copy.reverse()
    what_copy = copy.deepcopy(what)
    for action in through_copy:
        what_copy = action.process(what_copy)

    if to:
        to.sendall(what_copy)


def socket_handle_received(from_s, what, through=list()):
    through_copy = copy.deepcopy(through)
    what_copy = copy.deepcopy(what)
    for action in through_copy:
        what_copy = action.process_s(what_copy, from_s)

    return what_copy
