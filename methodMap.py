'''
    This file should not be exposed to the user
'''
from . import param as p


class MessageMap:
    def __init__(self, rpctype, method=None, resultType=None, paramType=None):
        self.rpctype = rpctype
        self.method = method
        self.resultType = resultType
        self.paramType = paramType


class N_Map(MessageMap):
    '''
        Notification map
    '''
    def __init__(self, method: str, paramType=None):
        super().__init__('Notification', method=method, paramType=paramType)


class Rq_Map(MessageMap):
    '''
        Request map
    '''
    def __init__(self, method: str, paramType=None):
        super().__init__('Request', method=method, paramType=paramType)


class Rp_Map(MessageMap):
    '''
        Response map
    '''
    def __init__(self, resultType):
        super().__init__('Response', resultType=resultType)


event_map = {
    'initialize':
    Rq_Map('onInitialize', p.InitializeParams),
    'initialized':
    N_Map('onInitialized', p.InitializedParams),
    'shutdown':
    Rq_Map('onShutdown', p.NullParams),
    'exit':
    N_Map('onExit', p.NullParams),
    'textDocument/didOpen':
    N_Map('onDidOpenTextDocument', p.DidOpenTextDocumentParams),
    'textDocument/didChange':
    N_Map('onDidChangeTextDocument', p.DidChangeTextDocumentParams),
    'textDocument/didClose':
    N_Map('onDidCloseTextDocument', p.DidCloseTextDocumentParams),
    'textDocument/didSave':
    N_Map('onDidSaveTextDocument', p.DidSaveTextDocumentParams),
    'workspace/didChangeConfiguration':
    N_Map('onDidChangeConfiguration', p.DidChangeConfigurationParams),
    'workspace/didChangeWorkspaceFolders':
    N_Map('onDidChangeWorkspaceFolders', p.DidChangeWorkspaceFoldersParams),
}
