# https://github.com/palantir/python-language-server
import logging
from concurrent import futures
from streams import JsonRpcStreamReader, JsonRpcStreamWriter
from .methodMap import event_map
from .dpylsp import LspItem
from .param import (NullParams, PublishDiagnosticParams, ConfigurationParams,
                    CancelParams, ShowMessageParams)
from .exception import JsonRpcRequestCancelled, JsonRpcException
from . import constant as ct

logger = logging.getLogger(__name__)

jsonrpc_version = '2.0'
cancel_method = '$/cancelRequest'


class ServerManager:
    def __init__(self, masterServer, reader, writer, max_worker=5):
        self.master = masterServer
        self.jsonreader = JsonRpcStreamReader(reader, max_worker)
        self.jsonwriter = JsonRpcStreamWriter(writer)
        self.server_request_futures = {}
        self.client_request_futures = {}
        self.__id_counter = 1

    def getRequestId(self):
        ''' get an unique id for server's request '''
        result = self.__id_counter + 1
        return result

    def start(self):
        self.jsonreader.listen(self.dispatch)

    def exit(self):
        self.executor.shutdown()
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
        result = getattr(self.master, name)(param)

        if callable(result):
            request_future = self.executor.submit(result)
            self.client_request_futures[msg_id] = request_future
            request_future.add_done_callback(self._request_callback(msg_id))
        elif isinstance(result, futures.Future):
            self.client_request_futures[msg_id] = request_future
            request_future.add_done_callback(self._request_callback(msg_id))
        else:
            self.send_response(msg_id, result)

    def _request_callback(self, msg_id):
        '''
            request callback
            after get the result then send it to the client
            the future's result should be a LspItem
        '''
        def callback(future):
            self.client_request_futures.pop(msg_id, None)
            if future.cancelled():
                future.set_exception(JsonRpcRequestCancelled())
            self.send_response(msg_id, future.result())

    def handle_response(self, id, result=None, error=None, **kwargs):
        '''
            called by dispatch
            result is None or a dict
            this will trigger the request_future's callback function
        '''
        request_future = self.server_request_futures.pop(id, None)
        if not request_future:
            return
        if error is not None:
            request_future.set_exception(JsonRpcException.fromDict())
            return
        request_future.set_result(result)

    def handle_notification(self, name, param, **kwargs):
        getattr(self.master, name)(param)

    def handle_cancel_notification(self, msg_id):
        request_future = self.client_request_futures.pop(msg_id, None)
        if not request_future:
            return
        request_future.cancel()

    def send_request(self, msg_id: int, method: str, param: LspItem):
        '''
            Send request to client and save a future in server_request_futures
            if client responds, then the future's callback will be called.
            Note that this function won't run the future and add callback.
        '''
        param_item = param.getDict()
        # msg_id = self.getRequestId()
        request = {
            'jsonrpc': jsonrpc_version,
            'id': msg_id,
            'method': method,
            'params': param_item
        }
        request_future = futures.Future()
        # request_future.add_done_callback(self._cancel_callback(msg_id))

        self.server_request_futures[msg_id] = request_future
        self.jsonwriter.write(request)

        return request_future

    def _cancel_callback(self, request_id):
        ''' cancellation callback for a request '''
        def callback(future):
            if future.cancelled():
                self.send_notification(cancel_method, CancelParams(request_id))
                future.set_exception(JsonRpcRequestCancelled())

        return callback

    def send_response(self, id, result: LspItem):
        result_item = result.getDict()
        response = {'jsonrpc': '2.0', 'id': id, 'result': result_item}
        self.jsonwriter.write(response)

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
        def callback(future):
            if future.cancelled():
                return
            else:
                self.master.onReceiveWorkspaceConfiguration(future.result())

        msg_id = self.getRequestId()
        ask_future = self.send_request(msg_id, 'workspace/configuration',
                                       param)
        ask_future.add_done_callback(callback)

    def show_message(self, message: str, messageType: int = ct.MessageType):
        '''
            This function is different from others
            since we don't require a LspItem for simplicity.
        '''
        self.send_notification('window/showMessage',
                               ShowMessageParams(messageType, message))
