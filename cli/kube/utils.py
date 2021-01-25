from pathlib import Path

import yaml


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
