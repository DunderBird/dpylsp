# Copyright 2018 Palantir Technologies, Inc.
import logging
import threading
from concurrent import futures

try:
    import ujson as json
except Exception:  # pylint: disable=broad-except
    import json

log = logging.getLogger(__name__)


class JsonRpcStreamReader(object):

    def __init__(self, rfile):
        self._rfile = rfile

    def close(self):
        self._rfile.close()

    def read_message(self):
        """Reads the contents of a message.

        Returns:
            A json
        """
        try:
            line = self._rfile.readline()

            if not line:
                return None

            content_length = self._content_length(line)

            # Blindly consume all header lines
            while line and line.strip():
                line = self._rfile.readline()

            if not line:
                return None

            # Grab the body
            result = self._rfile.read(content_length)
        except ValueError:
            if self._rfile.closed():
                return None
            else:
                log.exception("Failed to read from rfile")
        else:
            if result is None:
                return None
            try:
                return json.loads(result.decode('utf-8'))
            except ValueError:
                log.exception(f"Failed to parse {result}")

    @staticmethod
    def _content_length(line):
        """Extract the content length from an input line."""
        if line.startswith(b'Content-Length: '):
            _, value = line.split(b'Content-Length: ')
            value = value.strip()
            try:
                return int(value)
            except ValueError:
                raise ValueError("Invalid Content-Length header: {}".format(value))

        return None


class JsonRpcStreamWriter(object):

    def __init__(self, wfile, **json_dumps_args):
        self._wfile = wfile
        self._wfile_lock = threading.Lock()
        self._json_dumps_args = json_dumps_args

    def close(self):
        with self._wfile_lock:
            self._wfile.close()

    def write(self, message):
        with self._wfile_lock:
            if self._wfile.closed:
                return
            try:
                body = json.dumps(message, **self._json_dumps_args)

                # Ensure we get the byte length, not the character length
                content_length = len(body) if isinstance(body, bytes) else len(body.encode('utf-8'))

                response = (
                    "Content-Length: {}\r\n"
                    "Content-Type: application/vscode-jsonrpc; charset=utf8\r\n\r\n"
                    "{}".format(content_length, body)
                )

                self._wfile.write(response.encode('utf-8'))
                self._wfile.flush()
            except Exception:  # pylint: disable=broad-except   
                log.exception("Failed to write message to output file %s", message)
