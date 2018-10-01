import platform

from models.notifications import Notification, SoundConfig


class Notifier:
    @staticmethod
    def can_use_native():
        system = platform.system()
        if system == "Windows":
            try:
                import win10toast
                return True
            except ImportError:
                return False
        elif system == "Linux":
            try:
                import notify2
                return True
            except ImportError:
                return False
        elif system == "Darwin":
            return False  # MacOS is not supported currently
        else:
            return False

    def send_linux(self, notification: Notification, sound_config: SoundConfig):
        notifier_notification = self.notifier.Notification(notification.title, notification.message)
        notifier_notification.set_urgency(1)  # URGENCY_NORMAL
        notifier_notification.show()

    def send_mac_os(self, notification: Notification, sound_config: SoundConfig):
        self.__notify_custom(notification, sound_config)  # no MacOS support

    def send_windows(self, notification: Notification, sound_config: SoundConfig):
        self.notifier().show_toast(notification.title,
                                 notification.message,
                                 duration=4,
                                 threaded=True)

    def send_notification(self, notification: Notification, sound_config: SoundConfig):
        pass

    def __init__(self, app_name: str, use_native: bool = True):
        self.use_native = use_native and self.can_use_native()
        self.app_name = app_name

        if self.use_native:
            system = platform.system()
            if system == "Linux":
                import notify2
                notify2.init(app_name, "glib")
                self.notifier = notify2
                self.send_notification = self.send_linux
            elif system == "Windows":
                from win10toast import ToastNotifier
                self.notifier = ToastNotifier
                self.send_notification = self.send_windows
            elif system == "Darwin":
                self.notifier = None
                self.send_notification = self.send_mac_os

    def notify(self, notification: Notification, sound_config: SoundConfig = SoundConfig(False)):
        if self.use_native:
            self.__notify_native(notification, sound_config)
        else:
            self.__notify_custom(notification, sound_config)

    def __notify_native(self, notification, sound_config):
        self.send_notification(notification, sound_config)

    def __notify_custom(self, notification, sound_config):
        pass


class NotificationService:
    def __init__(self, use_native: bool = True):
        self.notifier = Notifier("Core Messenger", use_native)

    def notify(self, notification: Notification, sound_config: SoundConfig = SoundConfig(False)):
        self.notifier.notify(notification, sound_config)
