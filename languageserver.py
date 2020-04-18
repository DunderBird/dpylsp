from typing import Optional
from enum import Enum
import logging
from .manager import ServerManager
from .response import InitializeResult, SimpleResult
from . import param as p
from . import constant as ct
from .workspace import WorkSpace

logger = logging.getLogger(__name__)


class ServerState(Enum):
    RUN = 0
    SHUTDOWN = 1
    HANG = 2


class BasicLanguageServer:
    def __init__(self,
                 reader,
                 writer,
                 capability: Optional[dict] = None,
                 **kwargs):
        capability = capability if capability else {'textDocumentSync': ct.TextDocumentSyncKind.INCREMENTAL}
        self.state: ServerState = ServerState.HANG
        self.manager = ServerManager(self, reader, writer, server_capability=capability)
        self.workspace = WorkSpace()
        self.user_settings = {}
        self.parent_processId = -1


    def start(self):
        self.state = ServerState.RUN
        self.manager.start()
    
    def close(self):
        self.state = ServerState.HANG
        self.manager.exit()

    def onInitialize(self, param: p.InitializeParams,
                     **kwargs) -> InitializeResult:
        logger.debug(f'initialize: {param}')
        if getattr(param, 'workspaceFolders', None):
            for folder in param.workspaceFolders:
                self.workspace.addFolder(folder)
            logger.debug(f'workspaceFolders: {param.workspaceFolders}')
        else:
            self.workspace.rootUri = param.rootUri if param.rootUri else ''
        logger.debug(f'capability: {param.capabilities.getDict()}')
        self.parent_processId = param.processId
        self.manager.update_client_capability(param.capabilities.getDict())
        return InitializeResult(self.manager.get_server_capability())

    def onInitialized(self, param: p.InitializedParams, **kwargs) -> None:
        self.manager.ask_workspaceConfiguration(p.ConfigurationParams([p.ConfigurationItem(section='workbench')]))

    def onShutdown(self, param: p.NullParams, **kwargs) -> SimpleResult:
        self.state = ServerState.SHUTDOWN
        return SimpleResult()

    def onExit(self, param: p.NullParams, **kwargs) -> None:
        self.close()

    def onDidOpenTextDocument(self, param: p.DidOpenTextDocumentParams,
                              **kwargs) -> None:
        return None

    def onDidChangeTextDocument(self, param: p.DidChangeTextDocumentParams,
                                **kwargs) -> None:
        return None

    def onDidCloseTextDocument(self, param: p.DidCloseTextDocumentParams,
                               **kwargs) -> None:
        return None

    def onDidSaveTextDocument(self, param: p.DidSaveTextDocumentParams,
                              **kwargs) -> None:
        return None

    def onDidChangeConfiguration(self, param: p.DidChangeConfigurationParams,
                                 **kwargs) -> None:
        for item in param.settings:
            if item:
                self.user_settings.update(item)

    def onReceiveWorkspaceConfiguration(self, result: list, **kwargs) -> None:
        for item in result:
            if item:
                self.user_settings.update(item)
        logger.debug(self.user_settings)
    
    def onDidChangeWorkspaceFolders(self, param: p.DidChangeWorkspaceFoldersParams, **kwargs) -> None:
        for added_folder in param.event.added:
            self.workspace.addFolder(added_folder)
        for removed_folder in param.event.removed:
            self.workspace.removeFolder(removed_folder)


class LanguageServer(BasicLanguageServer):
    def __init__(self,
                 reader,
                 writer,
                 capability: Optional[dict]=None,
                 **kwargs):
        super().__init__(reader, writer, capability, **kwargs)

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
