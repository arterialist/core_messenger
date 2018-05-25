from client.models.base import Jsonable


class Action(Jsonable):
    def __init__(self, action="new"):
        self.action = action


class NewMessageAction(Action):
    def __init__(self):
        super().__init__(action="new")


class EditMessageAction(Action):
    def __init__(self):
        super().__init__(action="edit")


class ReplyMessageAction(Action):
    def __init__(self):
        super().__init__(action="reply")


class ForwardMessageAction(Action):
    def __init__(self):
        super().__init__(action="forward")


class DeleteMessageAction(Action):
    def __init__(self):
        super().__init__(action="delete")
