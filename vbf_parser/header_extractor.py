"""
Helper module to safely extract header from vbf file
"""

import io  # noqa: F401 pylint: disable=unused-import
import re
from typing import BinaryIO, Pattern, Union

VBF_ENCODING = "ascii"


def _read_until(file_handle: BinaryIO, pattern: Union[Pattern, str]) -> bool:
    """
    >>> file = io.BytesIO("abc; header {spanish inquisition".encode(VBF_ENCODING))
    >>> _read_until(file, r'header\\s*{')
    True
    >>> file.read().decode(VBF_ENCODING)
    'spanish inquisition'
    >>> file = io.BytesIO("no pattern".encode(VBF_ENCODING))
    >>> _read_until(file,r"\\{")
    False
    """
    text = ""
    while not re.search(pattern, text):
        char = file_handle.read(1).decode(VBF_ENCODING)
        if not char:
            return False
        text += char
    return True


def extract_header_body(file_handle: BinaryIO) -> str:
    """
    >>> header = 'trash;\\n header{\\n x=10;\\n} trash'
    >>> extract_header_body(io.BytesIO(header.encode(VBF_ENCODING))).strip()
    'x=10;'

    >>> header = 'trash; header{ x=10;} trash'
    >>> extract_header_body(io.BytesIO(header.encode(VBF_ENCODING))).strip()
    'x=10;'

    >>> header = 'header{\\n x = 10; z = {1,{2,3}};\\n }'
    >>> extract_header_body(io.BytesIO(header.encode(VBF_ENCODING))).strip()
    'x = 10; z = {1,{2,3}};'

    >>> header = 'header{\\n x = 10; z = {1,{2,3}};} trash'
    >>> extract_header_body(io.BytesIO(header.encode(VBF_ENCODING))).strip()
    'x = 10; z = {1,{2,3}};'

    >>> header = 'no pattern'
    >>> extract_header_body(io.BytesIO(header.encode(VBF_ENCODING))).strip()
    Traceback (most recent call last):
      ...
    ValueError: Reached file end before header was closed

    >>> header = 'header { x="}";}'
    >>> extract_header_body(io.BytesIO(header.encode(VBF_ENCODING))).strip()
    'x="}";'
    """
    _read_until(file_handle, r"header\s*{")
    nested_level = 1
    header = []
    is_in_quotes = False
    while nested_level != 0:
        char = file_handle.read(1).decode(VBF_ENCODING)
        if char == "":
            raise ValueError("Reached file end before header was closed")
        header.append(char)
        if char == '"':
            is_in_quotes = not is_in_quotes
        if not is_in_quotes:
            if char == "{":
                nested_level += 1
            elif char == "}":
                nested_level -= 1
    return "".join(header[:-1])
