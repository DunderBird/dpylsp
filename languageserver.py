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
    def __init__(self, reader, writer):
        self.state: ServerState = ServerState.HANG
        self.manager = ServerManager(self, reader, writer)
        self.workspace = WorkSpace()

    def start(self):
        self.state = ServerState.RUN
        self.manager.start()

    def close(self):
        self.state = ServerState.HANG
        self.manager.exit()

    def onInitialize(self, param: p.InitializeParams,
                     **kwargs) -> InitializeResult:
        capability = {"textDocumentSync": ct.textSync_Incremental}
        return InitializeResult(capabilities=ServerCapabilities(**capability))

    def onInitialized(self, param: p.InitializedParams, **kwargs) -> None:
        return None

    def onShutdown(self, **kwargs) -> SimpleResult:
        self.state = ServerState.SHUTDOWN
        return SimpleResult()

    def onExit(self, **kwargs) -> None:
        self.close()

    def onDidOpenTextDocument(self, param: p.DidOpenTextDocumentParams,
                              **kwargs) -> None:
        textDocument = param.textDocument
        self.workspace.addDocument(textDocument.uri, textDocument.text)

    def onDidChangeTextDocument(self, param: p.DidChangeTextDocumentParams,
                                **kwargs) -> None:
        self.workspace.updateDocument(param.textDocument.uri,
                                      param.contentChange)

    def onDidCloseTextDocument(self, param: p.DidCloseTextDocumentParams,
                               **kwargs) -> None:
        textDocument = param.textDocument
        self.workspace.removeDocument(textDocument.uri)
