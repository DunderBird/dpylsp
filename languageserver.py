from typing import Optional
from enum import Enum
from .manager import ServerManager
from .response import InitializeResult, SimpleResult
from . import param as p
from . import constant as ct
from .workspace import WorkSpace
from .capability import ServerCapabilities


class ServerState(Enum):
    RUN = 0
    SHUTDOWN = 1
    HANG = 2


class LanguageServer:
    def __init__(self,
                 reader,
                 writer,
                 capability: Optional[ServerCapabilities] = None,
                 **kwargs):
        self.state: ServerState = ServerState.HANG
        self.manager = ServerManager(self, reader, writer)
        self.workspace = WorkSpace()
        self.capability = capability if capability else ServerCapabilities(
            ct.textSync_Incremental)

    def start(self):
        self.state = ServerState.RUN
        self.manager.start()

    def close(self):
        self.state = ServerState.HANG
        self.manager.exit()

    def onInitialize(self, param: p.InitializeParams,
                     **kwargs) -> InitializeResult:
        return InitializeResult(self.capability)

    def onInitialized(self, param: p.InitializedParams, **kwargs) -> None:
        return None

    def onShutdown(self, param: p.NullParams, **kwargs) -> SimpleResult:
        self.state = ServerState.SHUTDOWN
        return SimpleResult()

    def onExit(self, param: p.NullParams, **kwargs) -> None:
        self.close()

    def onDidOpenTextDocument(self, param: p.DidOpenTextDocumentParams,
                              **kwargs) -> None:
        textDocument = param.textDocument
        self.workspace.addDocument(textDocument.uri, textDocument.text)

    def onDidChangeTextDocument(self, param: p.DidChangeTextDocumentParams,
                                **kwargs) -> None:
        self.workspace.updateDocument(param.textDocument.uri,
                                      param.contentChanges)

    def onDidCloseTextDocument(self, param: p.DidCloseTextDocumentParams,
                               **kwargs) -> None:
        textDocument = param.textDocument
        self.workspace.removeDocument(textDocument.uri)

    def onDidSaveTextDocument(self, param: p.DidSaveTextDocumentParams,
                              **kwargs) -> None:
        return None
