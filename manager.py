# https://github.com/palantir/python-language-server
import logging
import threading
from typing import Optional, Union
from concurrent import futures
from .streams import JsonRpcStreamReader, JsonRpcStreamWriter
from .methodMap import event_map
from .dpylsp import LspItem
from .param import (NullParams, PublishDiagnosticParams, ConfigurationParams,
                    CancelParams, ShowMessageParams, LogMessageParams)
from .struct import ResponseError
from .exception import JsonRpcRequestCancelled, JsonRpcException
from . import constant as ct

logger = logging.getLogger(__name__)


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
        self.__id_counter_lock = threading.RLock()

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
            logger.info(f'{new_json}')  # TODO: fix race(use producer-consumer model)
            new_worker.start()

    def exit(self):
        self.jsonreader.close()
        self.jsonwriter.close()

    def dispatch(self, message):
        if 'method' in message:
            handle_map = event_map.get(message['method'])
            if handle_map is None:
                if message['method'][:2] == r'$/' and 'id' in message:
                    self.send_error_response(message['id'], ct.ErrorCodes.METHODNOTFOUND)
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
            if new_item.cancelled:
                self.send_error_response(msg_id, ct.ErrorCodes.REQUESTCANCELLED)
            else:
                self.send_response(msg_id, result)

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
            request_item = self.client_request.get(msg_id, None)
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
            'jsonrpc': ct.JSONRPC_VERSION,
            'id': msg_id,
            'method': method,
            'params': param_item
        }
        with self.server_request_lock:
            self.server_request[msg_id] = ServerRequestRecord(callback)

        self.jsonwriter.write(request)

    def send_response(self, id, result=None, error: Optional[ResponseError]=None):
        logger.debug(f'{id} response: {result}')
        with self.client_request_lock:
            if id in self.client_request:
                result_item = result.getDict() if isinstance(result, LspItem) else result
                response = {'jsonrpc': '2.0', 'id': id}
                if result_item:
                    response['result'] = result_item
                if error:
                    response['error'] = error.getDict()
                self.jsonwriter.write(response)
                self.client_request.pop(id, None)

    def send_error_response(self, id, error_code: ct.ErrorCodes, message=''):
        with self.client_request_lock:
            if id in self.client_request:
                error_response = ResponseError(error_code, message)
                response = {
                    'jsonrpc': ct.JSONRPC_VERSION,
                    'id': id,
                    'error': error_response.getDict()
                }
                self.jsonwriter.write(response)
                self.client_request.pop(id, None)

    def send_notification(self, method: str, param: LspItem):
        param_item = param.getDict()
        notification = {
            'jsonrpc': ct.JSONRPC_VERSION,
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

    def show_message(self, message: str, messageType: Union[ct.MessageType, int]):
        '''
            This function is different from others
            because we don't require a LspItem for simplicity.
        '''
        self.send_notification('window/showMessage',
                               ShowMessageParams(messageType, message))
    
    def log_message(self, message: str, messageType: int = Union[ct.MessageType, int]):
        self.send_notification('window/logMessage', LogMessageParams(messageType, message))
