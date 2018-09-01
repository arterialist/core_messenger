class LogChannel:
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    def log(self, message: str):
        if self.enabled:
            print(f"Channel {self.name}: {message}")

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class FileLogChannel(LogChannel):
    def __init__(self, name: str, file_path: str, enabled: bool = True):
        super().__init__(name, enabled)
        self.file_path = file_path

    def log(self, message: str):
        with open(self.file_path, "a") as f:
            f.write(message)
            f.write("\n")


class Logger:
    __channels = dict()

    @staticmethod
    def get_channel(name: str, force: bool = False) -> LogChannel:
        if force and name not in Logger.__channels.keys():
            Logger.__channels[name] = LogChannel(name)

        return Logger.__channels.get(name, LogChannel("stub", enabled=False))

    @staticmethod
    def set_channel(channel: LogChannel):
        Logger.__channels[channel.name] = channel

    @staticmethod
    def remove_channel(name):
        if name in Logger.__channels.keys():
            Logger.__channels.pop(name)

    @staticmethod
    def mute():
        for channel in Logger.__channels.values():
            channel.disable()

    @staticmethod
    def unmute():
        for channel in Logger.__channels.values():
            channel.enable()
