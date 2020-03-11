import logging
from pyls_jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter
from .config import event_map
from .dpylsp import LspItem
from .param import NullParams, PublishDiagnosticParams

logger = logging.getLogger(__name__)


class ServerManager:
    def __init__(self, masterServer, reader, writer):
        self.master = masterServer
        self.jsonreader = JsonRpcStreamReader(reader)
        self.jsonwriter = JsonRpcStreamWriter(writer)

    def start(self):
        self.jsonreader.listen(self.dispatch)

    def exit(self):
        self.jsonreader.close()
        self.jsonwriter.close()

    def dispatch(self, message):
        if 'method' in message:
            handle_map = event_map.get(message['method'])
            if handle_map is None:
                logging.warning(
                    f"{message['method']} haven't been implemented")
            else:
                param_dict = message.get('params')
                handler_name = handle_map.method

                try:
                    handler_param = handle_map.paramType.fromDict(
                        param_dict
                    ) if param_dict and handle_map.paramType else NullParams
                except KeyError:
                    logger.error('Parameter parse error: %s %s',
                                 message['method'], str(param_dict))
                    return

                if hasattr(self.master, handler_name):
                    if handle_map.rpctype == 'Notification':
                        self.handle_notification(handler_name, handler_param)
                    elif handle_map.rpctype == 'Request':
                        self.handle_request(message['id'], handler_name,
                                            handler_param)

    def handle_request(self, id, name, param):
        result = getattr(self.master, name)(param)
        self.send_response(id, result)

    def handle_notification(self, name, param):
        getattr(self.master, name)(param)

    def handle_response(self):
        pass

    def send_response(self, id, result: LspItem):
        result_item = result.getDict()
        response = {'jsonrpc': '2.0', 'id': id, 'result': result_item}
        self.jsonwriter.write(response)

    def send_notification(self, method: str, param: LspItem):
        param_item = param.getDict()
        notification = {
            'jsonrpc': '2.0',
            'method': method,
            'params': param_item
        }
        self.jsonwriter.write(notification)

    def send_diagnostics(self, diagnostics: PublishDiagnosticParams):
        self.send_notification('textDocument/publishDiagnostics', diagnostics)
