'''
    This file should not be exposed to the user
'''
from . import param as p
from enum import IntEnum


class WorkerType(IntEnum):
    '''
        select which worker to respond this event
    '''
    EDITOR = 1
    NORMAL = 2
    URGENT = 3  # events we need to respond immediately(shutdown...)

class MessageMap:
    def __init__(self, rpctype, method=None, resultType=None, paramType=None, worker=WorkerType.NORMAL):
        self.rpctype = rpctype
        self.method = method
        self.resultType = resultType
        self.paramType = paramType
        self.worker = worker


class N_Map(MessageMap):
    '''
        Notification map
    '''
    def __init__(self, method: str, paramType=None, worker=WorkerType.NORMAL):
        super().__init__('Notification', method=method, paramType=paramType, worker=worker)


class Rq_Map(MessageMap):
    '''
        Request map
    '''
    def __init__(self, method: str, paramType=None, worker=WorkerType.NORMAL):
        super().__init__('Request', method=method, paramType=paramType, worker=worker)


class Rp_Map(MessageMap):
    '''
        Response map
    '''
    def __init__(self, resultType, worker=WorkerType.NORMAL):
        super().__init__('Response', resultType=resultType, worker=worker)


event_map = {
    'initialize':
    Rq_Map('onInitialize', p.InitializeParams, worker=WorkerType.URGENT),
    'initialized':
    N_Map('onInitialized', p.InitializedParams),
    # shutdown shouldn't be dispatched to another thread because that thread may join itself
    'shutdown':
    Rq_Map('onShutdown', p.NullParams, worker=WorkerType.URGENT),
    'exit':
    N_Map('onExit', p.NullParams, worker=WorkerType.URGENT),
    'textDocument/didOpen':
    N_Map('onDidOpenTextDocument', p.DidOpenTextDocumentParams, worker=WorkerType.EDITOR),
    'textDocument/didChange':
    N_Map('onDidChangeTextDocument', p.DidChangeTextDocumentParams, worker=WorkerType.EDITOR),
    'textDocument/didClose':
    N_Map('onDidCloseTextDocument', p.DidCloseTextDocumentParams, worker=WorkerType.EDITOR),
    'textDocument/didSave':
    N_Map('onDidSaveTextDocument', p.DidSaveTextDocumentParams, worker=WorkerType.EDITOR),
    'workspace/didChangeConfiguration':
    N_Map('onDidChangeConfiguration', p.DidChangeConfigurationParams),
    'workspace/didChangeWorkspaceFolders':
    N_Map('onDidChangeWorkspaceFolders', p.DidChangeWorkspaceFoldersParams),
}
