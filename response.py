from typing import Optional
from capability import ServerCapabilities
from dpylsp import LspItem


class SimpleResult(LspItem):
    def getDict(self):
        return {'result': None}


class InitializeResult(LspItem):
    def __init__(self,
                 capabilities: ServerCapabilities,
                 serverInfo: Optional[str] = None,
                 version: Optional[str] = None):
        self.capabilities = capabilities
        self.serverInfo = serverInfo
        self.version = version
