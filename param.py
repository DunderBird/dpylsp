from typing import Optional, List
from .capability import ClientCapabilities
from .constant import DocumentUri
from .dpylsp import LspItem
from .text import (TextDocumentItem, VersionedTextDocumentIdentifier,
                   TextDocumentContentChangeEvent, TextDocumentIdentifier)
from .diagnostic import Diagnostic

import logging

logger = logging.getLogger(__name__)


class InitializeParams(LspItem):
    def __init__(self, processId: Optional[int],
                 rootUri: Optional[DocumentUri],
                 capabilities: ClientCapabilities, **kwargs):
        self.processId = processId
        self.rootUri = rootUri
        self.capabilities = capabilities


class InitializedParams(LspItem):
    def __init__(self, **kwargs):
        pass


class DidOpenTextDocumentParams(LspItem):
    def __init__(self, **kwargs):
        if not hasattr(kwargs, 'textDocument'):
            logger.error('Missing params in DidOpenTextDocument')
            raise ValueError
        self.textDocument = TextDocumentItem(kwargs['textDocument'])


class DidChangeTextDocumentParams(LspItem):
    def __init__(self, **kwargs):
        if not hasattr(kwargs, 'textDocument') or not hasattr(
                kwargs, 'contentChanges'):
            logger.error('Missing params in DidChangeTextDocument')
            raise ValueError
        self.textDocument = VersionedTextDocumentIdentifier(
            kwargs['textDocument'])
        self.contentChange: List[TextDocumentContentChangeEvent]
        for change in kwargs['contentChanges']:
            self.contentChange.append(TextDocumentContentChangeEvent(change))


class DidCloseTextDocumentParams(LspItem):
    def __init__(self, **kwargs):
        if not hasattr(kwargs, 'textDocument'):
            logging.error('Missing params in DidCloseTextDocument')
            raise ValueError
        self.textDocument = TextDocumentIdentifier(kwargs['textDocument'])


class PublishDiagnosticParams(LspItem):
    def __init__(self, uri: DocumentUri, diagnostics: List[Diagnostic],
                 **kwargs):
        self.uri = uri
        self.diagnostics = diagnostics
