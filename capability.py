from typing import Optional
from .dpylsp import LspItem


class ClientCapabilities(LspItem):
    def __init__(self, **kwargs):
        pass


class ServerCapabilities(LspItem):
    def __init__(self,
                 textDocumentSync: Optional[int], **kwargs):
        self.textDocumentSync = textDocumentSync
