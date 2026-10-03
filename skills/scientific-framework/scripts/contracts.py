"""Shared contract utilities. JSON hashes are canonical UTF-8, not file bytes."""
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

SKILL = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def digest(data):
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()

def schema_errors(data, name):
    schema = read(SKILL/'schemas'/f'{name}.schema.json')
    Draft202012Validator.check_schema(schema)
    return [f'{"/".join(map(str,e.absolute_path))}: {e.message}'
            for e in Draft202012Validator(schema).iter_errors(data)]

def require_schema(data, name):
    errors = schema_errors(data, name)
    if errors: raise ValueError('\n'.join(errors))

def safe_xml(text):
    # XML 1.0 disallows most control characters, even if escaped.
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):
        raise ValueError('Invalid XML control character in label')
    return text
