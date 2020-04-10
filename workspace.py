# thanks https://github.com/palantir/python-language-server
from typing import List, Dict, Optional, Union
import logging
import io
from .struct import (TextDocumentContentChangeEvent, WorkspaceFolder, DocumentUri)

logger = logging.getLogger(__name__)


class Document:
    def __init__(self, uri: str, text: str):
        self.uri = uri
        self.text = text

    @property
    def lines(self):
        return self.text.splitlines(True)

    def update(self, changes: List[TextDocumentContentChangeEvent]):
        for change in changes:
            if change.range is None:
                self.text = change.text
            else:
                start = change.range.start
                end = change.range.end
                changeText = change.text
                lines = self.lines
                if start.line >= len(lines):
                    self.text += changeText
                    return

                newIo = io.StringIO()
                for i, line in enumerate(lines):
                    if i < start.line:
                        newIo.write(line)
                    if i > end.line:
                        newIo.write(line)
                    if i == start.line:
                        newIo.write(line[:start.character])
                        newIo.write(changeText)
                    if i == end.line:
                        newIo.write(line[end.character:])
                self.text = newIo.getvalue()


class WorkSpace:
    def __init__(self):
        self.workspaceFolders: List[WorkSpaceFolder] = []
        self.name = ''
        self.documents: Dict[Document] = {}
    
    @property
    def rootUri(self) -> Optional[DocumentUri]:
        if len(self.workspaceFolders) > 0:
            return self.workspaceFolders[0].uri
        else:
            return None
    
    @rootUri.setter
    def rootUri(self, uri: DocumentUri):
        self.workspaceFolders.insert(0, WorkspaceFolder(uri, ''))  # TODO: implement name property
    
    def addFolder(self, folder: WorkspaceFolder):
        self.workspaceFolders.append(folder)  # TODO: check whether the folder already in the list
    
    def removeFolder(self, folder: WorkspaceFolder):
        try:
            self.workspaceFolders.remove(folder)
        except ValueError:
            logger.exception(f'No such folder. Folder name: {folder.name}')

    def addDocument(self, uri: str, text: str):
        if uri in self.documents:
            self.documents[uri].text = text
        else:
            self.documents[uri] = Document(uri, text)

    def removeDocument(self, uri: str):
        try:
            self.documents.pop(uri)
        except KeyError:
            logger.error('%s does not exist in the workspace of the server',
                         uri)

    def updateDocument(self, uri: str,
                       changes: List[TextDocumentContentChangeEvent]):
        if uri not in self.documents:
            logger.error('%s does not exist in the workspace of the server',
                         uri)
        else:
            self.documents[uri].update(changes)

    def getDocumentText(self, uri: str) -> str:
        return self.documents[uri].text
