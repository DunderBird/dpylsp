from typing import Optional, List, Union
from .capability import ClientCapabilities
from .dpylsp import LspItem
from .struct import (TextDocumentItem, VersionedTextDocumentIdentifier,
                   TextDocumentContentChangeEvent, TextDocumentIdentifier, DocumentUri, Diagnostic,
                   WorkspaceFolder, WorkspaceFoldersChangeEvent)
from .config import ConfigurationItem

import logging

logger = logging.getLogger(__name__)


class NullParams(LspItem):
    '''
        Nullparams means the parameter is void
    '''
    def __init__(self, **kwargs):
        pass


class CancelParams(LspItem):
    def __init__(self, id: Union[int, str], **kwargs):
        self.id = id


class InitializeParams(LspItem):
    def __init__(self, processId: Optional[int],
                 rootUri: Optional[DocumentUri],
                 capabilities: ClientCapabilities, **kwargs):
        self.processId = processId
        self.rootUri = rootUri
        self.capabilities: ClientCapabilities = capabilities

    @classmethod
    def fromDict(cls, param: dict):
        return cls(processId=param['processId'],
                   rootUri=param['rootUri'],
                   capabilities=ClientCapabilities.fromDict(
                       param['capabilities']))


class InitializedParams(LspItem):
    def __init__(self, **kwargs):
        pass


# window
class ShowMessageParams(LspItem):
    def __init__(self, messageType: int, message: str, **kwargs):
        self.type = messageType
        self.message = message

class LogMessageParams(LspItem):
    def __init__(self, messageType: int, message: str, **kwargs):
        self.type = messageType
        self.message = message


# workspace
class DidChangeWorkspaceFoldersParams(LspItem):
    def __init__(self, event: WorkspaceFoldersChangeEvent, **kwargs):
        self.event = event
    
    @classmethod
    def fromDict(cls, param):
        return cls(WorkspaceFoldersChangeEvent.fromDict(param['event']))


class DidChangeConfigurationParams(LspItem):
    def __init__(self, settings, **kwargs):
        self.settings = settings

    @classmethod
    def fromDict(cls, param: dict):
        return cls(param['settings'])


class ConfigurationParams(LspItem):
    def __init__(self, items: List[ConfigurationItem], **kwargs):
        self.items = items

    @classmethod
    def fromDict(cls, param: dict):
        items = []
        for item in param['items']:
            items.append(ConfigurationItem.fromDict(item))
        return cls(items)


class DidOpenTextDocumentParams(LspItem):
    def __init__(self, textDocument: TextDocumentItem, **kwargs):
        self.textDocument = textDocument

    @classmethod
    def fromDict(cls, param: dict):
        return cls(
            textDocument=TextDocumentItem.fromDict(param['textDocument']))


class DidChangeTextDocumentParams(LspItem):
    def __init__(self, textDocument: VersionedTextDocumentIdentifier,
                 contentChanges: List[TextDocumentContentChangeEvent],
                 **kwargs):
        self.textDocument = textDocument
        self.contentChanges: List[
            TextDocumentContentChangeEvent] = contentChanges

    @classmethod
    def fromDict(cls, param: dict):
        contentChanges = []
        for change_event in param['contentChanges']:
            contentChanges.append(
                TextDocumentContentChangeEvent.fromDict(change_event))
        return cls(textDocument=VersionedTextDocumentIdentifier.fromDict(
            param['textDocument']),
                   contentChanges=contentChanges)


class DidCloseTextDocumentParams(LspItem):
    def __init__(self, textDocument: TextDocumentIdentifier, **kwargs):
        self.textDocument = textDocument

    @classmethod
    def fromDict(cls, param: dict):
        return cls(textDocument=TextDocumentIdentifier.fromDict(
            param['textDocument']))


class DidSaveTextDocumentParams(LspItem):
    def __init__(self, textDocument: TextDocumentIdentifier, **kwargs):
        self.textDocument = textDocument

    @classmethod
    def fromDict(cls, param: dict):
        return cls(textDocument=TextDocumentIdentifier.fromDict(
            param['textDocument']))


class PublishDiagnosticParams(LspItem):
    def __init__(self, uri: DocumentUri, diagnostics: List[Diagnostic],
                 **kwargs):
        self.uri = uri
        self.diagnostics = diagnostics

    @classmethod
    def fromDict(cls, param: dict):
        diags = []
        for diag_dict in param['diagnostics']:
            diags.append(Diagnostic.fromDict(diag_dict))
        return cls(uri=param['uri'], diagnostics=diags)
