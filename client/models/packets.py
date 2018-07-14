from client.models.actions import Action
from client.models.base import Jsonable
from client.models.messages import Message


class Packet(Jsonable):
    def __init__(self, action: Action = None, message: Message = None):
        self.action = action
        self.message = message

    @staticmethod
    def from_json_obj(json_obj: dict) -> Jsonable:
        return Packet(
            action=Action.from_json_obj(
                json_obj=json_obj["action"]),
            message=Message.from_json_obj(
                json_obj=json_obj["message"]))
