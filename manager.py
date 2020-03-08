from languageserver import LanguageServer
from pyls_jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter
from config import MessageMap, N_Map, Rp_Map, Rq_Map


class ServerManager:
    def __init__(self, masterServer: LanguageServer, reader, writer):
        self.master = masterServer
        self.jsonreader = JsonRpcStreamReader(reader)
        self.jsonwriter = JsonRpcStreamWriter(writer)

    def start(self):
        self.jsonreader.listen(self.dispatch)

    def dispatch(self, message):
        pass

    def constructParam(self, param):
        pass

    @staticmethod
    def sendNotification(self, message):
        pass

    @staticmethod
    def sendRequest(self, message):
        pass

    @staticmethod
    def sendResponse(self, message):
        pass
