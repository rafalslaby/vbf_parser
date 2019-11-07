[![Build Status](https://travis-ci.org/rafalslaby/vbf_parser.svg?branch=master)](https://travis-ci.org/rafalslaby/vbf_parser)
[![codecov](https://codecov.io/gh/rafalslaby/vbf_parser/branch/master/graph/badge.svg)](https://codecov.io/gh/rafalslaby/vbf_parser)
[![PyPI](https://img.shields.io/pypi/v/vbf_parser)](https://pypi.org/project/vbf-parser/)
[![Python: 3.6+](https://img.shields.io/badge/python-3.6%2B-blue)](https://img.shields.io/badge/python-3.6%2B-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code quality: MyPy](https://img.shields.io/badge/static%20analysis-mypy-informational)](https://github.com/python/mypy)
[![Security: bandit](https://img.shields.io/badge/security-bandit-blueviolet)](https://github.com/PyCQA/bandit)

# VBF parser

vbf-parser is a Python library for parsing VBF files.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
pip install vbf-parser
```

## Usage

Simple parsing with converting to json:

```python
import json
from vbf_parser import extract_header_body, jsonify_vbf_header
with open("file.vbf", "rb") as file:
    header_body = extract_header_body(file)
vbf = json.loads(jsonify_vbf_header(header_body))
```

#### Work in progress:
Proper lexing and manual parsing:
```python
from vbf_parser import extract_header_body, lex_vbf_header, parse_vbf_tokens
with open("file.vbf", "rb") as file:
    header_body = extract_header_body(file)
vbf = parse_vbf_tokens(lex_vbf_header(header_body))
```

## License
[MIT](https://choosealicense.com/licenses/mit/)