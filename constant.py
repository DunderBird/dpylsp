from typing import List
from enum import IntEnum

JSONRPC_VERSION = '2.0'

class TextDocumentSyncKind(IntEnum):
    NONE = 0
    FULL = 1
    INCREMENTAL = 2


class DiagnosticSeverity(IntEnum):
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


class DiagnosticTag(IntEnum):
    UNNECESSARY = 1
    DEPRECATED = 2


class MessageType(IntEnum):
    ERROR = 1
    WARNING = 2
    INFO = 3
    LOG = 4

class ErrorCodes(IntEnum):
    PARSEERROR = -32700
    INVALIDREQUEST = -32600
    METHODNOTFOUND = -32601
    INVALIDPARAMS = -32602
    INTERNALERROR = -32603
    SERVERERRORSTART = -32099
    SERVERERROREND = -32000
    SERVERNOTINITIALIZED = -32002
    UNKNOWNERRORCODE = -32001
    
    REQUESTCANCELLED = -32800
    CONTENTMODIFIED = -32801

class WatchKind(IntEnum):
    CREATE = 1
    CHANGE = 2
    DELETE = 4


class FileChangeType(IntEnum):
    CREATED = 1
    CHANGED = 2
    DELETED = 3