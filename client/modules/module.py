class BaseModule:
    def __init__(self, enabled=True):
        print("Module {} loaded".format(self.__class__.__name__))
        self.enabled = enabled

    # method for modifications of data before sending
    def process(self, data):
        if self.enabled:
            # do action
            pass

    # method for modifications of data after receiving
    def process_s(self, data, sock):
        if self.enabled:
            # do action
            pass

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

