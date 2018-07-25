from client.models.actions import Action
from client.models.base import Jsonable
from client.models.messages import Message, Data


class Packet(Jsonable):
    def __init__(self, action: Action = None, message: Message = None, data: Data = None):
        self.action = action
        self.message = message
        self.data = data

    @staticmethod
    def from_json_obj(json_obj):
        packet = Packet(
            action=Action.from_json_obj(
                json_obj=json_obj["action"]),
            message=Message.from_json_obj(
                json_obj=json_obj["message"])
        )
        if json_obj["data"]:
            packet.data = Data.from_json_obj(json_obj=json_obj["data"])
        return packet
