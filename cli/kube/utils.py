import json
from pathlib import Path
from typing import Dict

import yaml

from cli import constants, utils


def write_secret(name: str, data: dict, path: Path):
    for k in data:
        data[k] = str(data[k])

    content = {
        'apiVersion': 'v1',
        'kind': 'Secret',
        'metadata': {
            'name': name,
        },
        'type': 'Opaque',
        'stringData': data,
    }

    with path.open(mode='w') as f:
        yaml.safe_dump(content, f)


def get_terraform_outputs() -> Dict[str, Dict[str, str]]:
    output = utils.get_output(
        ['terraform', 'output', '-json'],
        cwd=constants.TERRAFORM_DIR,
    )
    return json.loads(output)


def get_resource_description(resource: str, name: str) -> dict:
    cmd = [
        'kubectl',
        '--namespace', 'forcad',
        'get', resource, name,
        '-o', 'json',
    ]
    result = utils.get_output(cmd, cwd=constants.BASE_DIR)
    return json.loads(result)
