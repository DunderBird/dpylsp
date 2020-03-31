from typing import Optional
from .dpylsp import LspItem
from .struct import DocumentUri


class ConfigurationItem(LspItem):
    def __init__(self,
                 scopeUri: Optional[DocumentUri] = None,
                 section: Optional[str] = None,
                 **kwargs):
        self.scopeUri = scopeUri
        self.section = section

    @classmethod
    def fromDict(cls, param: dict):
        return cls(param.get('scopeUri'), param.get('section'))
