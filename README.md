[![Build Status](https://travis-ci.org/rafalslaby/vbf_parser.svg?branch=master)](https://travis-ci.org/rafalslaby/vbf_parser)

# VBF parser

vbf-parser is a Python library for parsing VBF files.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
pip install vbf-parser
```

## Usage

Simple parsing with converting to json in between:

```python
from vbf_parser import extract_header_body, parse_vbf_header
with open("file.vbf") as file:
    header_body = extract_header_body(file)
vbf = parse_vbf_header(header_body)
```

Proper lex + parse version
```python
from vbf_parser import extract_header_body, lex_vbf_header, parse_vbf_tokens
with open("file.vbf") as file:
    header_body = extract_header_body(file)
vbf = parse_vbf_tokens(lex_vbf_header(header_body))
```

## License
[MIT](https://choosealicense.com/licenses/mit/)