import csv
from typing import Dict, Optional, List
_name_by_code: Dict[(str, str)] = None
_code_by_name: Dict[(str, str)] = None
_codes: List[str] = None
_names: List[str] = None

def init():
    global _code_by_name
    global _codes
    global _name_by_code
    global _names
    with open('./aws_translate_supported_languages.csv') as csvfile:
        aws_translate_supported_languages = csv.reader(csvfile, delimiter='\t')
        _name_by_code = dict()
        _code_by_name = dict()
        _names = list()
        _codes = list()
        for row in aws_translate_supported_languages:
            name, code = row
            name = name.strip()
            code = code.strip().lower()
            _names.append(name)
            _codes.append(code)
            _name_by_code[code] = name
            _code_by_name[name] = code

        _names.sort()
        _codes.sort()


def name_by_code(code: str) -> Optional[str]:
    if _name_by_code is None:
        init()
    return _name_by_code.get(code)


def code_by_name(name: str) -> Optional[str]:
    if _code_by_name is None:
        init()
    return _code_by_name.get(name)


def codes() -> List[str]:
    if _codes is None:
        init()
    return _codes


def names() -> List[str]:
    if _names is None:
        init()
    return _names