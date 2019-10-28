import re
from typing import Generator, Match, Tuple

VBF_TO_JSON_REPLACEMENTS = {";": ",", "{": "[", "}": "]", "=": ":"}


def _fix_missing_quotes(string: str) -> str:
    """
    >>> _fix_missing_quotes('identifier = value')
    '"identifier" = "value"'
    >>> _fix_missing_quotes('x = 0x2f')
    '"x" = 0x2f'
    """

    def quote_if_not_hex(match: Match) -> str:
        if re.fullmatch(r"0x[a-fA-F0-9]+", match.group(0)):
            return match.group(0)
        return f'"{match.group(0)}"'

    return re.sub(r"[^\s={};,]+", quote_if_not_hex, string)


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


def _convert_all_hexes_to_ints(vbf_string: str) -> str:
    """
    >>> _convert_all_hexes_to_ints('abc 0xff def 0XF')
    'abc 255 def 15'
    """

    def hex_match_to_int_str(match: Match) -> str:
        return str(int(match.group(0), base=16))

    return re.sub(r"(?i)0x[0-9-a-f]+", hex_match_to_int_str, vbf_string)


def _jsonify_vbf_part(vbf_string: str) -> str:
    jsonified = _remove_asterisk_comments(vbf_string)
    jsonified = _remove_slash_comments(jsonified)
    jsonified = _fix_missing_quotes(jsonified)
    jsonified = _convert_all_hexes_to_ints(jsonified)
    for source, replacement in VBF_TO_JSON_REPLACEMENTS.items():
        jsonified = jsonified.replace(source, replacement)
    return jsonified


def _iter_quoted(str_: str) -> Generator[Match, None, None]:
    """
    >>> [match.group(0) for match in _iter_quoted('trash"str1" trash " str2"trash')]
    ['"str1"', '" str2"']
    """
    yield from re.finditer(r'"[^"]*"', str_)


def _iter_unquoted_quoted_parts(str_: str) -> Generator[Tuple[str, str], None, None]:
    """
    >>> list(_iter_unquoted_quoted_parts('no"yes"no'))
    [('no', '"yes"'), ('no', '')]
    >>> list(_iter_unquoted_quoted_parts('"yes"no'))
    [('', '"yes"'), ('no', '')]
    >>> list(_iter_unquoted_quoted_parts('"yes"no"yes"'))
    [('', '"yes"'), ('no', '"yes"')]
    >>> list(_iter_unquoted_quoted_parts('"yes"'))
    [('', '"yes"')]
    >>> list(_iter_unquoted_quoted_parts('no'))
    [('no', '')]
    """
    last_quote_end_index = 0
    for quoted_match in _iter_quoted(str_):
        unquoted_part = str_[last_quote_end_index : quoted_match.start()]
        last_quote_end_index = quoted_match.end()
        quoted_part = quoted_match.group(0)
        yield unquoted_part, quoted_part
    unquoted_part = str_[last_quote_end_index:]
    if unquoted_part:
        yield unquoted_part, ""


def jsonify_vbf_header(header: str) -> str:
    """
    >>> from json import loads
    >>> loads(jsonify_vbf_header('abc = 0xff; //comment \\n z = "a b"; /* multi\\nline*/ y = {1,{2,3}  };'))
    {'abc': 255, 'z': 'a b', 'y': ['1', ['2', '3']]}
    """
    json_string = "{"
    for unquoted, quoted in _iter_unquoted_quoted_parts(header):
        json_string += _jsonify_vbf_part(unquoted) + quoted
    assert json_string[-1] == ",", f"Expected ',' at the end; got {json_string[-1]}"
    return json_string[:-1] + "}"
