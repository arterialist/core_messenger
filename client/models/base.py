import json


class Jsonable:
    @staticmethod
    def from_json(json_string):
        obj = Jsonable()
        obj.__dict__ = json.loads(json_string)
        return obj

    @staticmethod
    def from_json_obj(json_obj):
        obj = Jsonable()
        obj.__dict__ = json_obj
        return obj

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
