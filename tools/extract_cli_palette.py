#!/usr/bin/env python3
"""Read palette data from the installed native Claude binary; never execute it.

Usage: python3 -I tools/extract_cli_palette.py /path/to/claude-native
The embedded JS selector identifies the actual daltonized tables. Identifiers
are derived rather than assumed. Only scalar color data is exported.
"""
import hashlib
import json
import mmap
from pathlib import Path
import re
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]


def extract(binary, ansi_capture=None):
    with binary.open('rb') as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as data:
        result = {'binaryName': binary.name, 'binarySha256': hashlib.sha256(data).hexdigest(),
                  'method': 'Read embedded JavaScript and its theme selector; did not execute the binary',
                  'themes': {}}
        for mode in ('light-daltonized', 'dark-daltonized'):
            selector = re.search(rb'case"' + mode.encode() + rb'":return ([A-Za-z_$][\w$]*)', data)
            if selector is None:
                raise ValueError('No readable embedded selector for ' + mode)
            module_start = data.rfind(b'// @bun', 0, selector.start())
            module = data[module_start:selector.end()]
            version = re.search(rb'// Version: ([0-9.]+)', module)
            result['version'] = version.group(1).decode() if version else 'unknown'
            identifier = selector.group(1)
            table = re.search(rb'(?:var |,)' + re.escape(identifier) + rb'=\{([^{}]+)\}', module)
            if table is None:
                raise ValueError('Theme table missing for ' + mode)
            colors = {}
            for match in re.finditer(rb'(\w+):"rgb\(\s*(\d+),\s*(\d+),\s*(\d+)\)"', table.group(1)):
                colors[match.group(1).decode()] = '#' + ''.join(f'{int(match.group(i)):02X}' for i in (2, 3, 4))
            if not {'success', 'error', 'diffAdded', 'diffRemoved'} <= colors.keys():
                raise ValueError('Incomplete table for ' + mode)
            result['themes'][mode] = {'tableIdentifier': identifier.decode(),
                                      'tableByteOffset': module_start + table.start(),
                                      'selectorByteOffset': selector.start(), 'colors': colors}
        syntax_start = data.find(b'function ge(e){if(e.includes("ansi"))return"ansi";if(e.includes("dark"))return"Monokai Extended";return"GitHub"}')
        if syntax_start < 0:
            raise ValueError('Review syntax selector: this CLI build changed')
        syntax_source = data[syntax_start:syntax_start + 5000]
        maps = list(re.finditer(rb'([A-Za-z_$][\w$]*)=new Map\(\[(.*?)\]\)', syntax_source))
        result['syntax'] = {}
        for mode, name, table in zip(('dark', 'light'), ('Monokai Extended', 'GitHub'), maps):
            scopes = {}
            for entry in re.finditer(rb'\["([^"]+)",c\((\d+),(\d+),(\d+)\)\]', table.group(2)):
                scopes[entry.group(1).decode()] = '#' + ''.join(f'{int(entry.group(i)):02X}' for i in (2, 3, 4))
            if len(scopes) != 24:
                raise ValueError('Incomplete syntax scope table')
            result['syntax'][mode] = {'name': name, 'tableByteOffset': syntax_start + table.start(), 'scopes': scopes}
        renderer = re.search(rb'function V\(e,n\)\{.*?\}\}var he=', syntax_source)
        if renderer is None:
            raise ValueError('Code/Diff renderer missing')
        renderer_source = renderer.group(0)
        bindings = {m.group(1): '#' + ''.join(f'{int(m.group(i)):02X}' for i in (2, 3, 4))
                    for m in re.finditer(rb'(\w+)=c\((\d+),(\d+),(\d+)\)', renderer_source)}
        variants = list(re.finditer(rb'if\(r\)return\{([^}]+)\}', renderer_source))
        result['renderedDiff'] = {}
        for mode, variant in zip(('dark', 'light'), variants):
            colors = {}
            for key in ('addLine', 'addWord', 'addDecoration', 'deleteLine', 'deleteWord', 'deleteDecoration'):
                literal = re.search(key.encode() + rb':(?:s\?)?c\((\d+),(\d+),(\d+)\)', variant.group(1))
                if literal:
                    colors[key] = '#' + ''.join(f'{int(literal.group(i)):02X}' for i in (1, 2, 3))
                else:
                    reference = re.search(key.encode() + rb':(\w+)', variant.group(1))
                    colors[key] = bindings[reference.group(1)]
            result['renderedDiff'][mode] = {'rendererByteOffset': syntax_start + renderer.start(),
                                            'variantByteOffset': syntax_start + renderer.start() + variant.start(),
                                            'colors': colors}
    if ansi_capture:
        capture = ansi_capture.read_bytes()
        counts = Counter(re.findall(rb'\x1b\[48;2;(\d+);(\d+);(\d+)m', capture))
        result['nativeRenderEvidence'] = {
            'captureName': ansi_capture.name, 'captureSha256': hashlib.sha256(capture).hexdigest(),
            'backgroundColors': {'#' + ''.join(f'{int(x):02X}' for x in rgb): count for rgb, count in counts.items()},
            'note': 'Native emitted colors, not inferred from palette token names; terminal background affects rendering.'}
    return result


if __name__ == '__main__':
    source = Path(sys.argv[1]).expanduser().resolve()
    capture = Path(sys.argv[2]).expanduser().resolve() if len(sys.argv) > 2 else None
    output = ROOT / 'sources/claude-code-2.1.322-palette.json'
    output.parent.mkdir(exist_ok=True)
    result = extract(source, capture)
    if result['version'] != '2.1.322':
        raise ValueError('Review a new CLI version before changing the recorded palette')
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(output)
    for mode, theme in result['themes'].items():
        print(mode, {key: theme['colors'][key] for key in ('success', 'error', 'diffAdded', 'diffRemoved')})
