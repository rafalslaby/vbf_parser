import re
import io
from typing import TextIO


def extract_header_body(fp: TextIO) -> str:
    """
    >>> header = 'trash;\\n header{\\n x=10;\\n} trash'
    >>> extract_header_body(io.StringIO(header)).strip()
    'x=10;'

    >>> header = 'header{\\n x = 10; z = {1,{2,3}};}'
    >>> extract_header_body(io.StringIO(header)).strip()
    'x = 10; z = {1,{2,3}};'

    >>> header = 'header{\\n x = 10; z = {1,{2,3}};} trash'
    >>> extract_header_body(io.StringIO(header)).strip()
    'x = 10; z = {1,{2,3}};'

    """
    line = ""
    # TODO: won't work without newline after "header {"
    while not re.search(r"header\s*{", line):
        line = fp.readline()
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
