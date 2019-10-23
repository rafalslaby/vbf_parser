import re
from typing import Generator, Match

VBF_TO_JSON_REPLACEMENTS = {";": ",", "{": "[", "}": "]", "=": ":"}


def _fix_missing_quotes(string: str) -> str:
    """
    >>> _fix_missing_quotes('identifier = value')
    '"identifier" = "value"'
    """
    return re.sub(r"([^\s={};,]+)", r'"\1"', string)


def _remove_asterisk_comments(string: str) -> str:
    """
    >>> _remove_asterisk_comments('before/* a\\nb\\nc*/after')
    'beforeafter'
    """
    return re.sub(r"/\*[^\\]*\*/", "", string)


def _remove_slash_comments(string: str) -> str:
    """
    >>> _remove_slash_comments('before// comment\\nafter')
    'before\\nafter'
    """
    return re.sub(r"//.*", "", string)


def _jsonify_vbf_part(vbf_string: str) -> str:
    jsonified = _remove_asterisk_comments(vbf_string)
    jsonified = _remove_slash_comments(jsonified)
    jsonified = _fix_missing_quotes(jsonified)
    for source, replacement in VBF_TO_JSON_REPLACEMENTS.items():
        jsonified = jsonified.replace(source, replacement)
    return jsonified


def _iter_quoted(str_: str) -> Generator[Match, None, None]:
    """
    >>> [match.group(0) for match in _iter_quoted('trash"str1" trash " str2"trash')]
    ['"str1"', '" str2"']

    """
    yield from re.finditer(r'"[^"]*"', str_)


# TODO: all values are treated as strings, you might want to interpret hashes as integers
def jsonify_vbf_header(header: str) -> str:
    """
    >>> from json import loads
    >>> loads(jsonify_vbf_header('abc = 10; //comment \\n z = "a b"; /* multi\\nline*/ y = {1,{2,3}  };'))
    {'abc': '10', 'z': 'a b', 'y': ['1', ['2', '3']]}
    """
    json_string = "{"
    last_quote_end_index = 0
    for quoted_string in _iter_quoted(header):
        unquoted_part = header[last_quote_end_index : quoted_string.start()]
        jsonified = _jsonify_vbf_part(unquoted_part)
        json_string += jsonified + quoted_string.group(0)
        last_quote_end_index = quoted_string.end()
    json_string += _jsonify_vbf_part(header[last_quote_end_index:])
    json_string = json_string.rstrip()
    assert json_string[-1] == ",", f"Expected ',' at the end; got {json_string[-1]}"
    return json_string[:-1] + "}"
