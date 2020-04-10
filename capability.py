from typing import Optional, Union
from .dpylsp import LspItem


class ClientCapabilities(LspItem):
    def __init__(self, **kwargs):
        pass


'''
    Server capabilities
'''
class ServerCapabilities(LspItem):
    def __init__(self,
                 textDocumentSync: Optional[int], **kwargs):
        self.textDocumentSync = textDocumentSync

class WorkspaceFolderServerCapabilities(LspItem):
    def __init__(self, supported: Optional[bool]=None, changeNotifications: Optional[Union[str, bool]]=None):
        self.supported = supported
        self.changeNotifications = changeNotifications
