#!/usr/bin/env python3
"""Create local credentials once, without overwriting an existing environment."""
import os
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
target = root / '.env'
content = (root / 'config/environment.example').read_text()
for name in ('POSTGRES_PASSWORD', 'RABBITMQ_PASSWORD', 'REDIS_PASSWORD'):
    content = content.replace(f'{name}=\n', f'{name}={secrets.token_hex(32)}\n')
try:
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    print('Existing .env preserved. See docs/development.md for credential changes.')
else:
    with os.fdopen(fd, 'w') as output:
        output.write(content)
    print('Created ignored .env with private local credentials (mode 0600).')
