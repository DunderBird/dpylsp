from typing import Optional, List, Union
from .capability import ClientCapabilities
from .dpylsp import LspItem
from .struct import (TextDocumentItem, VersionedTextDocumentIdentifier,
                   TextDocumentContentChangeEvent, TextDocumentIdentifier, DocumentUri, Diagnostic,
                   WorkspaceFolder, WorkspaceFoldersChangeEvent, Registration)
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
                 capabilities: ClientCapabilities, workspaceFolders: Optional[List[WorkspaceFolder]] = None, **kwargs):
        self.processId = processId
        self.capabilities: ClientCapabilities = capabilities
        self.rootUri = rootUri
        if workspaceFolders:
            self.workspaceFolders: List[WorkspaceFolder] = workspaceFolders

    @classmethod
    def fromDict(cls, param: dict):
        workspaceFolders = None
        if 'workspaceFolders' in param:
            workspaceFolders = []
            for folder in param['workspaceFolders']:
                workspaceFolders.append(WorkspaceFolder.fromDict(folder))
        return cls(processId=param['processId'],
                   rootUri=param['rootUri'],
                   capabilities=ClientCapabilities.fromDict(
                       param['capabilities']),
                   workspaceFolders=workspaceFolders)


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


# capability
class RegistrationParams(LspItem):
    def __init__(self, registrations: list[Registration], **kwargs):
        self.registrations = registrations
    
    @classmethod
    def fromDict(cls, param: dict):
        registrations = []
        for regis in param['registrations']:
            registrations.append(Registration.fromDict(regis))
        return cls(registrations)