class JsonRpcRequestCancelled(Exception):
    pass


class JsonRpcException(Exception):
    @staticmethod
    def fromDict(error):
        pass
