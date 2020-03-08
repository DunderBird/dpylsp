from manager import ServerManager
from enum import Enum


class ServerState(Enum):
    RUN = 0
    SHUTDOWN = 1
    HANG = 2


class LanguageServer:
    def __init__(self, reader, writer):
        self.state: ServerState = ServerState.HANG
        self.manager = ServerManager(self, reader, writer)

    def start(self):
        self.state = ServerState.RUN
        self.manager.start()

    def onDidChange
