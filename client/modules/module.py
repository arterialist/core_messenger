import functools

STATUS_OK = pow(2, 0)
STATUS_ERROR = pow(2, 1)
STATUS_DROP = pow(2, 2)


class PacketDropException(Exception):
    pass


def processing_method(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> tuple:
        try:
            result = func(*args, **kwargs)
            return STATUS_OK, result
        except PacketDropException:
            return STATUS_DROP, None
        except Exception as e:
            return STATUS_ERROR, e

    return wrapper


class BaseModule:
    def __init__(self, enabled=True):
        print("Module {} loaded".format(self.__class__.__name__))
        self.enabled = enabled

    # method for modifications of data before sending
    def on_send(self, data):
        if self.enabled:
            # do action
            pass

    # method for modifications of data after receiving
    def on_receive(self, data, sock):
        if self.enabled:
            # do action
            pass

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class BasePreModule(BaseModule):
    def on_receive(self, data, sock):
        super().on_receive(data, sock)
        if type(data) is bytes:
            raise Exception("Invalid module usage. Got <bytes> data")

    def on_send(self, data):
        super().on_send(data)
        if type(data) is bytes:
            raise Exception("Invalid module usage. Got <bytes> data")


class BasePostModule(BaseModule):
    def on_receive(self, data, sock):
        super().on_receive(data, sock)
        if type(data) is not bytes:
            raise Exception(f"Invalid module usage. Got {type(data)} data instead of <bytes>")

    def on_send(self, data):
        super().on_send(data)
        if type(data) is not bytes:
            raise Exception(f"Invalid module usage. Got {type(data)} data instead of <bytes>")
