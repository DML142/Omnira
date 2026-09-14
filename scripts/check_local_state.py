#!/usr/bin/env python3
"""Check private execution state separately from public CI."""
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
local = root / '.ai'
required = ['AGENTS.md', 'PRODUCT.md', 'ARCHITECTURE.md', 'DESIGN.md', 'ROADMAP.md',
            'CURRENT.md', 'STATE.json', 'DECISIONS.md', 'MEMORY.md']
for name in required:
    if not (local / name).is_file():
        raise SystemExit(f'Missing local project memory: {name}; restore it before source work.')
state = json.loads((local / 'STATE.json').read_text())
for field in ['current_phase', 'current_feature', 'branch', 'status', 'allowed_services',
              'allowed_paths', 'blocked_features', 'required_checks']:
    if field not in state:
        raise SystemExit(f'Missing state field: {field}')
branch = subprocess.check_output(['git', '-C', str(root), 'branch', '--show-current'], text=True).strip()
if branch != state['branch']:
    raise SystemExit(f'Branch mismatch: actual={branch}, state={state["branch"]}')
current = (local / 'CURRENT.md').read_text()
for value in [state['branch'], state['current_phase'], state['status']]:
    if value not in current:
        raise SystemExit(f'CURRENT.md does not match state: {value}')
phases = sorted((local / 'roadmap').glob('*.md'))
if [p.name[:2] for p in phases] != [f'{i:02}' for i in range(25)]:
    raise SystemExit('Expected all 25 ordered roadmap phases.')
index = (local / 'ROADMAP.md').read_text()
headings = ['Goal', 'Why', 'Prerequisites', 'Scope', 'Required tasks', 'Acceptance criteria',
            'Tests', 'Documentation impact', 'Explicitly not included', 'Exit criteria']
for phase in phases:
    text = phase.read_text()
    for heading in headings:
        if f'## {heading}\n' not in text:
            raise SystemExit(f'{phase.name}: missing {heading}')
    if f'roadmap/{phase.name}' not in index:
        raise SystemExit(f'Phase missing from index: {phase.name}')
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        if not (phase.parent / target).exists():
            raise SystemExit(f'Broken phase link: {phase.name}: {target}')
if not (local / 'roadmap' / (state['current_phase'] + '.md')).is_file():
    raise SystemExit('Current phase does not exist.')
for local_name, public_name in [('PRODUCT.md', 'docs/product/vision.md'), ('DESIGN.md', 'docs/product/design.md')]:
    if (local / local_name).read_text() != (root / public_name).read_text():
        raise SystemExit(f'Durable document mirrors diverged: {local_name}')
print(f'Local state checks passed ({len(phases)} phases; {state["status"]}).')
