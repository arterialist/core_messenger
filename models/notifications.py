class Notification:
    def __init__(self, title: str, message: str, detailed_message: str = None):
        self.detailed_message = detailed_message if detailed_message else message
        self.message = message
        self.title = title


class SoundConfig:
    def __init__(self, make_sound: bool = True, sound_path: str = None):
        self.make_sound = make_sound
        self.sound_path = sound_path
