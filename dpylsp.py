import logging

logger = logging.getLogger(__name__)


def _convert_val(target):
    if target is None:
        return None
    if isinstance(target, int):
        return int(target)  # note that we use int() to get value from a IntEnum
    if isinstance(target, (float, str)):
        return target
    elif isinstance(target, list):
        result = []
        for item in target:
            result.append(_convert_val(item))
        return result
    elif isinstance(target, dict):
        result = {}
        for key, value in target.items():
            result[key] = _convert_val(value)
    elif isinstance(target, LspItem):
        return target.getDict()
    else:
        return None


class LspItem(object):
    def __init__(self, **kwargs):
        pass

    @classmethod
    def fromDict(cls, param: dict):
        return cls(**param)

    def __repr__(self):
        return str(self.getDict())
    
    def __str__(self):
        return str(self.getDict())

    def getDict(self):
        dump_dict = {}
        for key, value in vars(self).items():
            if value is not None:
                converted = _convert_val(value)
                if converted is not None:
                    dump_dict[key] = converted
        return dump_dict
