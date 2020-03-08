from typing import Optional, List
from dpylsp import LspItem
from constant import DocumentUri


class Position(LspItem):
    def __init__(self, line, character, **kwargs):
        self.line: int = line
        self.character: int = character


class Range(LspItem):
    def __init__(self, start: dict, end: dict, **kwargs):
        self.start = Position(**start)
        self.end = Position(**end)


class Location(LspItem):
    def __init__(self, uri: DocumentUri, range: dict, **kwargs):
        self.uri = uri
        self.range = Range(**range)


class TextDocumentIdentifier(LspItem):
    def __init__(self, uri: DocumentUri, **kwargs):
        self.uri = uri


class VersionedTextDocumentIdentifier(TextDocumentIdentifier):
    def __init__(self, uri: DocumentUri, **kwargs):
        super().__init__(uri)
        self.version: Optional[int] = kwargs.get('version')


class TextEdit:
    '''
        A textual edit applicable to a text document.
    '''
    def __init__(self, range: dict, newText: str, **kwargs):
        self.range = Range(**range)
        self.newText = newText


class TextDocumentEdit:
    '''
        Describes textual changes on a single text
        document. A TextDocumentEdit describes all changes
        on a version Si and after they are applied move the
        document to version Si+1.
    '''
    def __init__(self, textDocument: dict, edits: List[dict], **kwargs):
        self.textDocument = VersionedTextDocumentIdentifier(**textDocument)
        self.edits = []
        for edit in edits:
            self.edits.append(TextEdit(**edit))


class TextDocumentItem:
    '''
        An Item to transfer a text document from the client to
        the server.
    '''
    def __init__(self, uri: DocumentUri, languageId: str, version: int,
                 text: str, **kwargs):
        self.uri = uri
        self.languageId = languageId
        self.version = version
        self.text = text


class TextDocumentContentChangeEvent:
    '''
        An event describing a change to a text document. If range and
        rangeLength are ommitted. the new text is considered to be the full
        content of the document.
    '''
    def __init__(self,
                 text: str,
                 range: Optional[Range] = None,
                 **kwargs):
        self.text = text
        self.range = range
