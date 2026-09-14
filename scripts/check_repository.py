#!/usr/bin/env python3
"""Validate documentation links, whitespace, and protected Git paths."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def protected(name):
    path = Path(name)
    return ('.ai' in path.parts or 'secrets' in path.parts
            or path.name == '.env' or path.name.startswith('.env.')
            or path.suffix in {'.pem', '.key'})


def main():
    indexed = git('ls-files', '-z').decode().split('\0')
    files = set(indexed + git('ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')) - {''}
    errors = []
    for name in indexed:
        if name and protected(name):
            errors.append(f'Protected file tracked: {name}')
    probes = ['.ai/STATE.json', '.env', '.env.local', 'services/orders/.env.test',
              'secrets/token', 'infra/tls/server.pem', 'infra/tls/server.key']
    for probe in probes:
        result = subprocess.run(['git', '-C', str(ROOT), 'check-ignore', '--no-index', '-q', probe])
        if result.returncode != 0:
            errors.append(f'Missing ignore protection: {probe}')
    for name in sorted(files):
        path = ROOT / name
        if not path.is_file() or path.suffix not in {'.md', '.py', '.yml', '.yaml'}:
            continue
        content = path.read_text()
        if not content.endswith('\n'):
            errors.append(f'Missing final newline: {name}')
        for line_number, line in enumerate(content.splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f'Trailing whitespace: {name}:{line_number}')
        if path.suffix == '.md':
            prose = re.sub(r'```.*?```', '', content, flags=re.S)
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', prose):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                    continue
                target = target.split('#')[0]
                if target and not (path.parent / target).exists():
                    errors.append(f'Broken link: {name} -> {target}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Repository checks passed ({len(files)} public files).')


if __name__ == '__main__':
    main()
