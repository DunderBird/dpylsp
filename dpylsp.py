import logging

logger = logging.getLogger(__name__)


def _convert_val(target):
    if target is None:
        return None
    if isinstance(target, (int, float, str)):
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

    def getDict(self):
        dump_dict = {}
        for key, value in vars(self).items():
            if value is not None:
                converted = _convert_val(value)
                if converted:
                    dump_dict[key] = converted
        logger.info(f'dict: {str(dump_dict)}')
        return dump_dict
