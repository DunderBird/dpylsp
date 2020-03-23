# https://github.com/Microsoft/vscode-uri/blob/e59cab84f5df6265aed18ae5f43552d3eef13bb9/lib/index.ts
import urllib.parse as parse
import os
import re

driverLetterPath = re.compile(r'^\/[a-zA-Z]:')


def urlparse(uri: str):
    scheme, netloc, path, params, query, fragment = parse.urlparse(uri)
    return (parse.unquote(scheme), parse.unquote(netloc), parse.unquote(path),
            parse.unquote(params), parse.unquote(query),
            parse.unquote(fragment))


def uriTofsPath(uri: str):
    scheme, netloc, path, params, query, fragment = urlparse(uri)
    if netloc and path and scheme == 'file':
        value = f'//{netloc}${path}'
    elif driverLetterPath.match(path):
        value = path[1].lower() + path[2:]
    else:
        value = path

    if os.name == 'nt':
        value = value.replace('/', '\\')

    return value


def fsPathToUri(path: str):
    scheme = 'file'
    netloc = ''
    params = ''
    query = ''
    fragment = ''

    if os.name == 'nt':
        path = path.replace('\\', '/')
    if path[:2] == '//':
        try:
            idx = path.index('/', 2)
            netloc = path[2:idx]
            path = path[idx:]
        except (ValueError):
            netloc = path[2:]
    if not path.startswith('/'):
        path = '/' + path

    if driverLetterPath.match(path):
        quoted_path = path[:3] + parse.quote(path[3:])
    else:
        quoted_path = parse.quote(path)

    return parse.urlunparse(
        (parse.quote(scheme), parse.quote(netloc), quoted_path,
         parse.quote(params), parse.quote(query), parse.quote(fragment)))
