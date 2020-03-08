import json
from enum import Enum


class LspItem(object):
    def getDict(self):
        dump_dict = {}
        for key, value in vars(self).items():
            if value is not None:
                if isinstance(value, LspItem):
                    dump_dict[key] = value.getDict()
                elif isinstance(value, (int, float, str, list, dict)):
                    dump_dict[key] = value
                elif hasattr(value,
                             '__dict__') and not isinstance(value, Enum):
                    dump_dict[key] = vars(value)
        return dump_dict

    def serialize(self):
        return json.dumps(self.getDict())
