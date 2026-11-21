"""Local-only proof-of-concept Dockerfile ancestry scanner. NOT production complete."""
import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

FROM = re.compile(r'^\s*FROM\s+(?:--platform=\S+\s+)?(\S+)(?:\s+AS\s+(\S+))?', re.I)
ARG = re.compile(r'^\s*ARG\s+([A-Za-z_][A-Za-z0-9_]*)(?:=(\S+))?', re.I)
SUB = re.compile(r'\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))')

def parse_dockerfile(path: Path, overrides=None):
    """Return external parent refs and unresolved expressions, with original line numbers.

    Handles simple ARG defaults/overrides and multi-stage aliases. Dynamic build logic
    requires additional resolvers; never silently assume it is resolved.
    """
    overrides = overrides or {}
    args, stages, parents, unresolved = {}, set(), [], []
    lines = path.read_text(encoding='utf-8').splitlines()
    for num, line in enumerate(lines, 1):
        # Concatenated instructions, heredocs and nonstandard templating not supported.
        if line.rstrip().endswith('\\'):
            unresolved.append({'line': num, 'expression': line.strip(), 'reason': 'continuation requires enhanced parser'})
        m = ARG.match(line)
        if m:
            k, default = m.groups()
            if k not in args:
                args[k] = overrides.get(k, default)
            continue
        m = FROM.match(line)
        if not m:
            continue
        raw, alias = m.groups()
        missing = []
        def replace(match):
            name = match.group(1) or match.group(2)
            val = args.get(name)
            if val is None:
                missing.append(name)
                return match.group(0)
            return val
        resolved = SUB.sub(replace, raw)
        if missing:
            unresolved.append({'line': num, 'expression': raw, 'reason': 'unresolved ARG: ' + ', '.join(sorted(set(missing)))})
        elif resolved.lower() != 'scratch' and resolved.lower() not in stages:
            parents.append({'reference': resolved, 'line': num, 'expression': raw})
        if alias:
            stages.add(alias.lower())
    return parents, unresolved

def analyze(inventory_path: Path):
    doc = json.loads(inventory_path.read_text(encoding='utf-8'))
    entries = doc['images']
    root = inventory_path.parent.parent if doc.get('paths_relative_to') == 'project_root' else inventory_path.parent
    by_ref = {}
    for entry in entries:
        if entry['image_ref'] in by_ref:
            raise ValueError('Duplicate image_ref in inventory: ' + entry['image_ref'])
        by_ref[entry['image_ref']] = entry['id']
    nodes = []
    edges = []
    unresolved = []
    for e in entries:
        file = (root / e['dockerfile']).resolve()
        if not file.is_relative_to(root.resolve()):
            raise ValueError('Dockerfile escapes inventory root: ' + str(file))
        if not file.is_file():
            raise FileNotFoundError(str(file))
        nodes.append({k: e.get(k) for k in ('id', 'image_ref', 'dockerfile', 'workflow', 'platform', 'source_repo')})
        parents, unknown = parse_dockerfile(file, e.get('build_args'))
        for u in unknown:
            unresolved.append({'image': e['id'], 'file': e['dockerfile'], **u})
        for p in parents:
            parent = by_ref.get(p['reference'])
            if parent:
                edges.append({'from': parent, 'to': e['id'], 'kind': 'build_from', 'reference': p['reference'],
                              'confidence': 'inferred', 'evidence': {'file': e['dockerfile'], 'line': p['line']}})
            else:
                unresolved.append({'image': e['id'], 'file': e['dockerfile'], 'line': p['line'],
                                   'expression': p['reference'], 'reason': 'parent not in catalog (possibly external)'})
    ids = {n['id'] for n in nodes}
    indegree = {i: 0 for i in ids}
    children = defaultdict(list)
    for edge in edges:
        indegree[edge['to']] += 1
        children[edge['from']].append(edge['to'])
    frontier = sorted([i for i in ids if indegree[i] == 0])
    waves = []
    while frontier:
        waves.append(frontier)
        upcoming = []
        for parent in frontier:
            for child in children[parent]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    upcoming.append(child)
        frontier = sorted(upcoming)
    cycle_nodes = sorted(i for i, n in indegree.items() if n > 0)
    return {'schema_version': '0.1-starter', 'nodes': nodes, 'edges': edges, 'unresolved': unresolved,
            'rebuild_waves': waves, 'cycle_or_blocked_nodes': cycle_nodes}

def write_outputs(graph, out):
    out.mkdir(parents=True, exist_ok=True)
    (out / 'graph.json').write_text(json.dumps(graph, indent=2) + '\n', encoding='utf-8')
    with (out / 'dependencies.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['from', 'to', 'kind', 'reference', 'confidence', 'file', 'line'])
        writer.writeheader()
        for e in graph['edges']:
            writer.writerow({**{k: e[k] for k in ('from', 'to', 'kind', 'reference', 'confidence')}, **e['evidence']})
    lines = ['flowchart TD']
    for n in graph['nodes']:
        lines.append('  ' + re.sub(r'\W', '_', n['id']) + '["' + n['id'].replace('"', '') + '"]')
    for e in graph['edges']:
        lines.append('  ' + re.sub(r'\W', '_', e['from']) + ' --> ' + re.sub(r'\W', '_', e['to']))
    (out / 'graph.mmd').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    report = ['# Dependency discovery report', '',
              '**Source-only assessment; no actual registry or workflow builds were verified.**', '', '## Build waves']
    for i, w in enumerate(graph['rebuild_waves'], 1):
        report.append(f'{i}. ' + ', '.join(w))
    report.extend(['', '## Unresolved parent/ARG references'])
    for u in graph['unresolved']:
        report.append(f"- `{u['image']}` `{u['file']}:{u['line']}`: {u['reason']} (`{u.get('expression', '')}`)")
    if not graph['unresolved']:
        report.append('- None found in current narrow scan scope')
    report.extend(['', '## Cycle/blocked nodes', ', '.join(graph['cycle_or_blocked_nodes']) or 'None', ''])
    (out / 'report.md').write_text('\n'.join(report), encoding='utf-8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=Path('output'))
    a = parser.parse_args()
    g = analyze(a.inventory)
    write_outputs(g, a.output_dir)
    print(f"Scanned {len(g['nodes'])} declared images; {len(g['edges'])} matched edges; {len(g['unresolved'])} unresolved; {len(g['cycle_or_blocked_nodes'])} cycle/blocked nodes")

if __name__ == '__main__':
    main()
