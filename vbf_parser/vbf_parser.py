import json
import re
from typing import List, Tuple, Union

VBF_SYNTAX = "={};,"
WHITESPACE = "\r\n\t\f\v "


def lex_vbf_header_simple(header: str):
    """
    >>> lex_vbf_header_simple('x = "ab"')
    ['x', '=', '"ab"']
    >>> lex_vbf_header_simple('y={1,2,3}')
    ['y', '=', '{', '1', ',', '2', ',', '3', '}']
    >>> lex_vbf_header_simple('y={{1,2},3};  abc=   0x12;')
    ['y', '=', '{', '{', '1', ',', '2', '}', ',', '3', '}', ';', 'abc', '=', '0x12', ';']
    """
    tokens = []
    is_inside_quotes = False
    token = ""
    for c in header:
        if not is_inside_quotes and c in WHITESPACE:
            if token:
                tokens.append(token)
                token = ""
        elif c == '"':
            token += c
            is_end_quote = is_inside_quotes
            if is_end_quote:
                tokens.append(token)
                token = ""
            is_inside_quotes = not is_inside_quotes
        elif c in VBF_SYNTAX:
            # flush current
            if token:
                tokens.append(token)
                token = ""
            tokens.append(c)
        else:
            token += c

    return tokens


def lex_quoted(header: str) -> Tuple[str, str]:
    """
    >>> lex_quoted('"abc";a=10')
    ('"abc"', ';a=10')
    >>> lex_quoted('a=10')
    ('', 'a=10')
    """
    if header[0] != '"':
        return "", header
    end_quote_pos = header.find('"', 1)
    return header[: end_quote_pos + 1], header[end_quote_pos + 1 :]


def lex_unquoted_value(header: str) -> Tuple[str, str]:
    """
    >>> lex_unquoted_value("abc=10")
    ('abc', '=10')
    >>> lex_unquoted_value(" a")
    ('', ' a')
    """
    if header[0] in VBF_SYNTAX + WHITESPACE:
        return "", header
    match = re.search(rf"[\s{VBF_SYNTAX}]", header)
    return header[: match.start()], header[match.start() :]


def lex_syntax(header: str) -> Tuple[str, str]:
    """
    >>> lex_syntax("=123")
    ('=', '123')
    """
    if header[0] not in VBF_SYNTAX:
        return "", header
    return header[0], header[1:]


def lex_whitespace(header: str) -> Tuple[str, str]:
    """
    >>> lex_whitespace(" a")
    ('', 'a')
    """
    if not re.match(r"\s", header[0]):
        return "", header
    return "", header[1:]


def lex_vbf_header(header: str) -> List[str]:
    """
    >>> lex_vbf_header('x = "ab"')
    ['x', '=', '"ab"']
    >>> lex_vbf_header('y={1,  2,3}')
    ['y', '=', '{', '1', ',', '2', ',', '3', '}']
    >>> lex_vbf_header('y={{1,2},3};  abc=   0x12;')
    ['y', '=', '{', '{', '1', ',', '2', '}', ',', '3', '}', ';', 'abc', '=', '0x12', ';']
    """
    tokens = []
    lexing_functions = [lex_quoted, lex_unquoted_value, lex_syntax, lex_whitespace]
    while header:
        for lex_func in lexing_functions:
            token, header = lex_func(header)
            if token:
                tokens.append(token)
                break
    return tokens


def _parse_array(tokens: List[str]) -> Tuple[Union[list, str], List[str]]:
    """
    >>> _parse_array(list("1,{2,3}};abc"))
    (['1', ['2', '3']], [';', 'a', 'b', 'c'])
    >>> _parse_array(list("1}"))
    (['1'], [])
    """
    array = []
    while tokens:
        token, *tokens = tokens
        if token == "}":
            return array, tokens
        elif token == "{":
            sub_array, tokens = _parse_array(tokens)
            array.append(sub_array)
        elif token != ",":
            array.append(token)
            assert tokens[0] == "}" or tokens[0] == ","


def parse_vbf_tokens(tokens: List[str]):
    """
    >>> tokens = lex_vbf_header('x = 10; yz={1,{2,3}};')
    >>> parse_vbf_tokens(tokens)
    {'x': '10', 'yz': ['1', ['2', '3']]}

    >>> tokens = lex_vbf_header('x = 0xff;')
    >>> parse_vbf_tokens(tokens)
    {'x': 255}

    """
    result = {}
    while tokens:
        name, equal_sign, *tokens = tokens
        assert equal_sign == "=", f"Syntax error: expected '=' got {equal_sign}; before: {''.join(tokens)}"
        if tokens[0] == "{":
            value, (semicolon, *tokens) = _parse_array(tokens[1:])
        else:
            value, semicolon, *tokens = tokens
            if value.startswith("0x"):
                value = int(value, base=16)
        assert semicolon == ";", f"Syntax error: expected ';' got {semicolon}; before: {''.join(tokens)}"
        result[name] = value
    return result
