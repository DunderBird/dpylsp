from typing import Optional, Union
from .dpylsp import LspItem
from .config import TextDocumentSyncOptions


class ClientCapabilities(LspItem):
    def __init__(self, params):
        pass


class ServerCapabilities(LspItem):
    def __init__(self,
                 textDocumentSync: Optional[Union[int,
                                                  TextDocumentSyncOptions]]):
        self.textDocumentSync = textDocumentSync
