from typing import Optional, List
from .dpylsp import LspItem
from . import constant as ct


'''
    Text Related
'''

EOL: List[str] = ['\n', '\r\n', '\r']
DocumentUri = str


class Position(LspItem):
    def __init__(self, line: int, character: int, **kwargs):
        self.line: int = line
        self.character: int = character


class Range(LspItem):
    def __init__(self, start: Position, end: Position, **kwargs):
        self.start = start
        self.end = end

    @classmethod
    def fromDict(cls, param: dict):
        return cls(start=Position.fromDict(param['start']),
                   end=Position.fromDict(param['end']))


class Location(LspItem):
    def __init__(self, uri: DocumentUri, range: Range, **kwargs):
        self.uri = uri
        self.range = range

    @classmethod
    def fromDict(cls, param: dict):
        return cls(uri=param['uri'], range=Range.fromDict(param['range']))


class TextDocumentIdentifier(LspItem):
    def __init__(self, uri: DocumentUri, **kwargs):
        self.uri = uri


class VersionedTextDocumentIdentifier(TextDocumentIdentifier):
    def __init__(self,
                 uri: DocumentUri,
                 version: Optional[int] = None,
                 **kwargs):
        super().__init__(uri)
        self.version: Optional[int] = version


class TextEdit(LspItem):
    '''
        A textual edit applicable to a text document.
    '''
    def __init__(self, range: Range, newText: str, **kwargs):
        self.range = range
        self.newText = newText

    @classmethod
    def fromDict(cls, param: dict):
        return cls(range=Range.fromDict(param['range']),
                   newText=param['newText'])


class TextDocumentEdit(LspItem):
    '''
        Describes textual changes on a single text
        document. A TextDocumentEdit describes all changes
        on a version Si and after they are applied move the
        document to version Si+1.
    '''
    def __init__(self, textDocument: VersionedTextDocumentIdentifier,
                 edits: List[TextEdit], **kwargs):
        self.textDocument = textDocument
        self.edits = edits

    @classmethod
    def fromDict(cls, param: dict):
        edits = []
        for edit in param['edits']:
            edits.append(TextEdit.fromDict(edit))
        return cls(
            textDocument=VersionedTextDocumentIdentifier.fromDict(
                param['textDocument']),
            edits=edits,
        )


class TextDocumentItem(LspItem):
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


class TextDocumentContentChangeEvent(LspItem):
    '''
        An event describing a change to a text document. If range and
        rangeLength are ommitted. the new text is considered to be the full
        content of the document.
    '''
    def __init__(self, text: str, range: Range, **kwargs):
        self.text = text
        self.range = range

    @classmethod
    def fromDict(cls, param: dict):
        return cls(param['text'], Range.fromDict(param['range']))




'''
    Diagnostic Related
'''
class Diagnostic(LspItem):
    def __init__(self,
                 range: Range,
                 message: str,
                 severity: Optional[ct.DiagnosticSeverity] = None,
                 **kwargs):
        self.range = range
        self.message = message
        self.severity = severity

    @classmethod
    def fromDict(cls, param: dict):
        return Diagnostic(Range.fromDict(param['range']), param['message'],
                          param['severity'])




'''
    Response Related
'''
class ResponseError(LspItem):
    def __init__(self, code: ct.ErrorCodes, message=''):
        self.code = code
        self.message = message




'''
    Workspace Related
'''
class WorkspaceFolder(LspItem):
    def __init__(self, uri: DocumentUri, name: str):
        self.uri = uri
        self.name = name


class WorkspaceFoldersChangeEvent(LspItem):
    def __init__(self, added: List[WorkspaceFolder], removed: List[WorkspaceFolder]):
        self.added = added
        self.removed = removed
    
    @classmethod
    def fromDict(cls, param):
        added_list = [WorkspaceFolder.fromDict(add) for add in param['added']]
        removed_list = [WorkspaceFolder.fromDict(remove) for remove in param['removed']]
        return cls(added_list, removed_list)


'''
    Capability Related
'''
class RegisterOptions(LspItem):
    pass


class Registration(LspItem):
    def __init__(self, id: str, method: str, registerOptions: Optional[RegisterOptions]=None):
        self.id = id
        self.method = method
        if registerOptions:
            self.registerOptions = registerOptions

    @classmethod
    def fromDict(cls, param):
        options = None
        if 'registerOptions' in param:
            options = RegisterOptions.fromDict(param['registerOptions'])
        return cls(param['id'], param['method'], options)
