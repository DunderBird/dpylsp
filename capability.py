from typing import Optional, Union
from .dpylsp import LspItem, DictLspItem


class ClientCapabilities(DictLspItem):
    def __init__(self, **kwargs):
        super().__init__(kwargs)


'''
    Server capabilities
'''
class ServerCapabilities(DictLspItem):
    def __init__(self, **kwargs):
        super().__init__(kwargs)


class WorkspaceFolderServerCapabilities(LspItem):
    def __init__(self, supported: Optional[bool]=None, changeNotifications: Optional[Union[str, bool]]=None):
        self.supported = supported
        self.changeNotifications = changeNotifications
