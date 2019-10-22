import io
import re
from typing import Pattern, TextIO, Union


def _read_until(fp: TextIO, pattern: Union[Pattern, str]) -> bool:
    """
    >>> file = io.StringIO("abc; header {spanish inquisition")
    >>> _read_until(file, r"header\s*{")
    True
    >>> file.read()
    'spanish inquisition'

    """
    text = ""
    while not re.search(pattern, text):
        c = fp.read(1)
        if not c:
            break
        text += c
    else:
        return True
    return False


def extract_header_body(fp: TextIO) -> str:
    """
    >>> header = 'trash;\\n header{\\n x=10;\\n} trash'
    >>> extract_header_body(io.StringIO(header)).strip()
    'x=10;'

    >>> header = 'trash; header{ x=10;} trash'
    >>> extract_header_body(io.StringIO(header)).strip()
    'x=10;'

    >>> header = 'header{\\n x = 10; z = {1,{2,3}};}'
    >>> extract_header_body(io.StringIO(header)).strip()
    'x = 10; z = {1,{2,3}};'

    >>> header = 'header{\\n x = 10; z = {1,{2,3}};} trash'
    >>> extract_header_body(io.StringIO(header)).strip()
    'x = 10; z = {1,{2,3}};'

    """
    _read_until(fp, r"header\s*{")
    nested_level = 1
    header = []
    is_in_quotes = False
    while nested_level != 0:
        char = fp.read(1)
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
