import json
from typing import Dict


def json2text(response: Dict):
    return json.dumps(response, indent=None)
