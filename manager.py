# https://github.com/palantir/python-language-server
import logging
import threading
from concurrent import futures
from .streams import JsonRpcStreamReader, JsonRpcStreamWriter
from .methodMap import event_map
from .dpylsp import LspItem
from .param import (NullParams, PublishDiagnosticParams, ConfigurationParams,
                    CancelParams, ShowMessageParams)
from .exception import JsonRpcRequestCancelled, JsonRpcException
from . import constant as ct

logger = logging.getLogger(__name__)

jsonrpc_version = '2.0'
cancel_method = '$/cancelRequest'


class ClientRequestRecord:
    def __init__(self):
        self.cancelled = False
    
    def cancel(self):
        self.cancelled = True


class ServerRequestRecord:
    def __init__(self, callback):
        self.callback = callback
    
    def run(self, result, error, *args, **kwargs):
        self.callback(result=result, error=error, **kwargs)

class ServerManager:
    def __init__(self, masterServer, reader, writer, max_workers=5):
        self.master = masterServer
        self.jsonreader = JsonRpcStreamReader(reader)
        self.jsonwriter = JsonRpcStreamWriter(writer)
        self.server_request = {}
        self.server_request_lock = threading.RLock()
        self.client_request = {}
        self.client_request_lock = threading.RLock()
        self.__id_counter = 1
        self.__id_counter_lock = threading.Lock()

    def getRequestId(self):
        ''' get an unique id for server's request '''
        with self.__id_counter_lock:
            result = self.__id_counter
            self.__id_counter += 1
            return result

    def start(self):
        while True:
            new_json = self.jsonreader.read_message()
            new_worker = threading.Thread(target=self.dispatch, args=(new_json,))
            logger.info(f'threading count: {threading.active_count()}')
            new_worker.start()

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
        else:
            self.handle_response(**message)

    def handle_request(self, msg_id, name, param, **kwargs):
        '''
            handle request from client.
            msg_id: request's id
            name: the handler's name of languageserver
            param: parameter
            See https://github.com/palantir/python-language-server
        '''
        try:
            handler = getattr(self.master, name)
        except:
            logger.exception(f'No {name} method')
        else:
            with self.client_request_lock:
                new_item = ClientRequestRecord()
                self.client_request[msg_id] = new_item
            result = handler(param)
            if result and not new_item.cancelled:
                self.send_response(msg_id, result)

    
    def __client_request_callback(self, msg_id: int):
        def callback(future: futures.Future):
            nonlocal msg_id
            if future.cancelled():
                return
            else:
                try:
                    logger.info(f'id: {msg_id}')
                    result = future.result()
                    self.send_response(msg_id, result)
                except:
                    logger.exception('Failed to get the result')
        return callback

    def handle_response(self, id, result=None, error=None, **kwargs):
        '''
            called by dispatch
            result is None or a dict
            this will trigger the request_future's callback function
        '''
        with self.server_request_lock:
            record = self.server_request.pop(id, None)
            if record:
                if error is not None:
                    # TODO: furthur modification
                    return
                record.run(result=result, error=error, **kwargs)
            self.server_request.pop(id)

    def handle_notification(self, name, param, **kwargs):
        getattr(self.master, name)(param)

    def handle_cancel_notification(self, msg_id):
        with self.client_request_lock:
            request_item = self.client_request.pop(msg_id, None)
            if request_item:
                request_item.cancel()

    def send_request(self, method: str, param: LspItem, callback):
        '''
            Send request to client and save a future in server_request_futures
            if client responds, then the future's callback will be called.
            Note that this function won't run the future and add callback.
        '''
        param_item = param.getDict()
        msg_id = self.getRequestId()
        request = {
            'jsonrpc': jsonrpc_version,
            'id': msg_id,
            'method': method,
            'params': param_item
        }
        with self.server_request_lock:
            self.server_request[msg_id] = ServerRequestRecord(callback)

        self.jsonwriter.write(request)

    def _cancel_callback(self, request_id):
        ''' cancellation callback for a request '''
        def callback(future):
            if future.cancelled():
                self.send_notification(cancel_method, CancelParams(request_id))
                future.set_exception(JsonRpcRequestCancelled())

        return callback

    def send_response(self, id, result: LspItem):
        logger.info(f'send response {id} {result.getDict()}')
        with self.client_request_lock:
            if id in self.client_request:
                result_item = result.getDict()
                response = {'jsonrpc': '2.0', 'id': id, 'result': result_item}
                self.jsonwriter.write(response)
                self.client_request.pop(id, None)

    def send_notification(self, method: str, param: LspItem):
        param_item = param.getDict()
        notification = {
            'jsonrpc': jsonrpc_version,
            'method': method,
            'params': param_item
        }
        self.jsonwriter.write(notification)

    def send_diagnostics(self, diagnostics: PublishDiagnosticParams):
        self.send_notification('textDocument/publishDiagnostics', diagnostics)

    def ask_workspaceConfiguration(self, param: ConfigurationParams):
        def callback(result, error, *args, **kwargs):
            self.master.onReceiveWorkspaceConfiguration(result)

        self.send_request('workspace/configuration',
                                       param, callback)

    def show_message(self, message: str, messageType: int = ct.MessageType):
        '''
            This function is different from others
            since we don't require a LspItem for simplicity.
        '''
        self.send_notification('window/showMessage',
                               ShowMessageParams(messageType, message))
