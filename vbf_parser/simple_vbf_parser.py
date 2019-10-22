import json
import re

VBF_TO_JSON_REPLACEMENTS = {";": ",", "{": "[", "}": "]", "=": ":"}


def _fix_missing_quotes(vbf_string: str) -> str:
    return re.sub(r"([^\s={};,]+)", r'"\1"', vbf_string)


def _jsonify_vbf_part(vbf_string: str) -> str:
    jsonified = _fix_missing_quotes(vbf_string)
    for source, replacement in VBF_TO_JSON_REPLACEMENTS.items():
        jsonified = jsonified.replace(source, replacement)
    return jsonified


def _iter_quoted_strings(str_: str):
    yield from re.finditer(r'"[^"]*"', str_)


# TODO: all values are treated as strings, you might want to interpret hashes as integers
def parse_vbf_header(header: str) -> dict:
    """
    >>> parse_vbf_header('abc = 10; z = "a b"; y = {1,{2,3}  };')
    {'abc': '10', 'z': 'a b', 'y': ['1', ['2', '3']]}

    """
    json_string = "{"
    last_quote_end_index = 0
    for quoted_string in _iter_quoted_strings(header):
        unquoted_part = header[last_quote_end_index : quoted_string.start()]
        jsonified = _jsonify_vbf_part(unquoted_part)
        json_string += jsonified + quoted_string.group(0)
        last_quote_end_index = quoted_string.end()
    json_string += _jsonify_vbf_part(header[last_quote_end_index:])
    json_string = json_string.rstrip()
    assert json_string[-1] == ",", f"Expected ',' at the end; got {json_string[-1]}"
    json_string = json_string[:-1] + "}"
    return json.loads(json_string)
