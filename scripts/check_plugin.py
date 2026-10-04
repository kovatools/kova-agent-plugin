#!/usr/bin/env python3
"""Zero-token checks for a multi-host Kova plugin. Run from the plugin root.

1. Every manifest parses and carries the same name and version.
2. Remote MCP endpoints are https.
3. Each skill uses only portable frontmatter, its name matches its folder,
   and its description fits the 1,024-character limit.
4. No verdict vocabulary (buy/sell calls, price targets, return promises) in
   shipped text, except on lines that state the prohibition.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path('.')
errors, warnings = [], []

MANIFESTS = {
    'plugin.json': lambda m: (m['name'], m['version']),
    '.claude-plugin/plugin.json': lambda m: (m['name'], m['version']),
    '.claude-plugin/marketplace.json': lambda m: (m['plugins'][0]['name'], m['plugins'][0]['version']),
    '.codex-plugin/plugin.json': lambda m: (m['name'], m['version']),
    '.cursor-plugin/plugin.json': lambda m: (m['name'], m['version']),
    'gemini-extension.json': lambda m: (m['name'], m['version']),
}

seen = {}
for path, pick in MANIFESTS.items():
    p = ROOT / path
    if not p.exists():
        continue
    try:
        seen[path] = pick(json.loads(p.read_text()))
    except Exception as e:  # noqa: BLE001
        errors.append(f'{path}: {e}')
for extra in ('.mcp.json', 'mcp.json', '.app.json'):
    if (ROOT / extra).exists():
        try:
            json.loads((ROOT / extra).read_text())
        except Exception as e:  # noqa: BLE001
            errors.append(f'{extra}: {e}')

if len({v for _, v in seen.values()}) > 1:
    errors.append('version drift: ' + ', '.join(f'{k}={v[1]}' for k, v in seen.items()))
if len({n for n, _ in seen.values()}) > 1:
    errors.append('name drift: ' + ', '.join(f'{k}={v[0]}' for k, v in seen.items()))

for mcp_file in ('.mcp.json', 'mcp.json', 'gemini-extension.json'):
    p = ROOT / mcp_file
    if p.exists():
        for name, srv in json.loads(p.read_text()).get('mcpServers', {}).items():
            url = srv.get('url') or srv.get('httpUrl')
            if url and not url.startswith('https://'):
                errors.append(f'{mcp_file}: {name} url is not https')

PORTABLE = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
for skill in sorted(ROOT.glob('skills/*/SKILL.md')):
    text = skill.read_text()
    fm = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not fm:
        errors.append(f'{skill}: no frontmatter')
        continue
    keys = set(re.findall(r'^([\w-]+):', fm.group(1), re.M))
    if keys - PORTABLE:
        errors.append(f'{skill}: non-portable frontmatter {sorted(keys - PORTABLE)}')
    name = re.search(r'^name:\s*(.+)$', fm.group(1), re.M)
    if not name or name.group(1).strip() != skill.parent.name:
        errors.append(f'{skill}: name does not match folder')
    desc = re.search(r'^description:\s*(.*?)(?=^[\w-]+:|\Z)', fm.group(1), re.S | re.M)
    if not desc or len(desc.group(1).strip()) > 1024:
        errors.append(f'{skill}: description missing or over 1,024 characters')
    lines, tokens = text.count('\n'), int(len(text.split()) * 1.33)
    if lines > 500 or tokens > 5000:
        warnings.append(f'{skill}: {lines} lines, ~{tokens} tokens (guideline: under 500 lines, 5,000 tokens)')

VERDICT = re.compile(r'\b(price target|strong buy|rating:\s*(buy|sell)|we recommend|you should (buy|sell)|'
                     r'guaranteed returns?|will outperform|best stocks? to buy|can.t lose)\b', re.I)
PROHIBITION = re.compile(r"\b(never|don.t|do not|not|no|won.t|isn.t|without|fail if)\b", re.I)
SKIP_DIRS = {'.git', 'evals', 'scripts', 'node_modules'}
for f in ROOT.rglob('*'):
    if not f.is_file() or f.suffix not in {'.md', '.json'} or SKIP_DIRS & set(f.parts):
        continue
    for i, line in enumerate(f.read_text(errors='ignore').splitlines(), 1):
        if VERDICT.search(line) and not PROHIBITION.search(line):
            errors.append(f'{f}:{i}: verdict vocabulary: {line.strip()[:100]}')

for w in warnings:
    print('WARN ', w)
for e in errors:
    print('FAIL ', e)
print(f'{len(seen)} manifests, version {next(iter(seen.values()))[1] if seen else "?"}: '
      + ('OK' if not errors else f'{len(errors)} failure(s)'))
sys.exit(1 if errors else 0)
