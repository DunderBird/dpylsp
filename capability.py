from typing import Optional, Union
from .dpylsp import LspItem


class ClientCapabilities(LspItem):
    def __init__(self, params):
        pass


class ServerCapabilities(LspItem):
    def __init__(self,
                 textDocumentSync: Optional[Union[int,
                                                  int]], **kwargs):
        self.textDocumentSync = textDocumentSync
