import base64
import hashlib
import uuid

import zlib


def get_id_hash():
    return hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()


def to_base64(data: str, as_bytes: bool = False):
    result = base64.b64encode(data) if data else b""
    return result if as_bytes else result.decode()


def from_base64(data: str, as_bytes: bool = False):
    result = base64.b64decode(data) if data else b""
    return result if as_bytes else result.decode()


def compress(data, as_bytes: bool = False):
    return zlib.compress(data) if as_bytes else zlib.compress(data).decode()


def decompress(data, as_bytes: bool = False):
    return zlib.decompress(data) if as_bytes else zlib.decompress(data).decode()
