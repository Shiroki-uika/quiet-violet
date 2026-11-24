#!/usr/bin/env python3
"""Check source-palette fidelity, UI contrast, generated files and VSIX.

Native syntax colors are NOT silently recolored to pass a contrast target.
Any native low-contrast combinations are reported separately and honestly.
"""
import importlib.util
import json
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('theme_build', ROOT / 'tools/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def luminance(color):
    rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def composite(color, background):
    if len(color) == 7:
        return color
    alpha = int(color[7:9], 16) / 255
    return '#' + ''.join(f'{round(int(color[i:i + 2], 16) * alpha + int(background[i:i + 2], 16) * (1 - alpha)):02X}'
                         for i in (1, 3, 5))


def contrast(a, b):
    assert len(a) == len(b) == 7, 'Resolve transparent colors first'
    x, y = sorted((luminance(a), luminance(b)))
    return (y + 0.05) / (x + 0.05)


def check():
    package = json.loads((ROOT / 'package.json').read_text())
    assert len(package['contributes']['themes']) == 2
    assert not any(k in package for k in ('main', 'browser', 'activationEvents', 'dependencies'))
    assert set(package['contributes']) == {'themes'}
    source = build.CLI
    assert source['version'] == '2.1.322'
    report = {'cliVersion': source['version'], 'nativeSyntaxRecolored': False, 'themes': {}}
    native_rules = {
        'Comments': 'comment', 'Keywords': 'keyword', 'Storage declarations': '_storage',
        'Operators': 'operator', 'Punctuation': 'punctuation', 'Variables': 'variable',
        'Parameters': 'params', 'Functions': 'title.function', 'Built-in functions / types': 'built_in',
        'Class titles': 'title.class', 'Strings': 'string', 'Numbers': 'number', 'Literals': 'literal',
        'Language variables': 'variable.language', 'Symbols': 'symbol', 'Attributes': 'attr',
        'Properties': 'property', 'Escapes and regular expressions': 'regexp',
    }
    schemes = json.loads((ROOT / 'terminal/windows-terminal.json').read_text())
    assert len(schemes) == 2
    for mode in ('light', 'dark'):
        theme = json.loads((ROOT / f'themes/quiet-violet-{mode}.json').read_text())
        assert theme == build.make_theme(mode), 'Rebuild generated JSON'
        assert theme['type'] == mode and theme['semanticHighlighting'] is True
        colors = theme['colors']
        scheme = next(s for s in schemes if s['name'] == theme['name'])
        kitty = dict(line.split() for line in (ROOT / f'terminal/kitty-{mode}.conf').read_text().splitlines())
        for index, ansi in enumerate(('Black', 'Red', 'Green', 'Yellow', 'Blue', 'Magenta', 'Cyan', 'White')):
            key = 'purple' if ansi == 'Magenta' else ansi.lower()
            assert kitty[f'color{index}'] == scheme[key] == colors['terminal.ansi' + ansi]
            assert kitty[f'color{index + 8}'] == scheme['bright' + key.capitalize()] == colors['terminal.ansiBright' + ansi]
        for key, kitty_key, theme_key in [('foreground', 'foreground', 'terminal.foreground'),
                                         ('background', 'background', 'terminal.background'),
                                         ('cursorColor', 'cursor', 'editorCursor.foreground'),
                                         ('selectionBackground', 'selection_background', 'terminal.selectionBackground')]:
            assert scheme[key] == kitty[kitty_key] == colors[theme_key]
        for key, value in colors.items():
            assert re.fullmatch(r'#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?', value), (key, value)
        state = source['themes'][mode + '-daltonized']['colors']
        syntax = source['syntax'][mode]['scopes']
        diff = source['renderedDiff'][mode]['colors']
        rules = {rule['name']: rule for rule in theme['tokenColors']}
        for name, scope in native_rules.items():
            assert rules[name]['settings']['foreground'] == syntax[scope], (mode, name, scope)
            assert rules[name]['settings']['fontStyle'] == '', 'Do not invent syntax font styling'
        for semantic, scope in {'keyword': 'keyword', 'modifier': '_storage', 'string': 'string',
                               'comment': 'comment', 'function': 'title.function', 'class': 'title.class',
                               'type': 'type', 'parameter': 'params', 'variable': 'variable',
                               'property': 'property', 'number': 'number', 'operator': 'operator'}.items():
            assert theme['semanticTokenColors'][semantic] == syntax[scope]
        assert colors['editorError.foreground'] == colors['terminal.ansiRed'] == state['error']
        assert colors['editorGutter.addedBackground'] == colors['terminal.ansiGreen'] == state['success']
        assert colors['diffEditor.insertedLineBackground'] == diff['addLine']
        assert colors['diffEditor.removedLineBackground'] == diff['deleteLine']
        for kind, native in (('inserted', 'add'), ('removed', 'delete')):
            text = colors[f'diffEditor.{kind}TextBackground']
            assert len(text) == 9 and text[-2:] != 'FF', 'Keep word highlight translucent'
            assert composite(text, diff[native + 'Line']) == diff[native + 'Word']
        pairs = [('foreground', 'editor.background'), ('descriptionForeground', 'sideBar.background'),
                 ('button.foreground', 'button.background'), ('button.foreground', 'button.hoverBackground'),
                 ('button.secondaryForeground', 'button.secondaryBackground'),
                 ('statusBar.foreground', 'statusBar.background'),
                 ('titleBar.activeForeground', 'titleBar.activeBackground'),
                 ('titleBar.inactiveForeground', 'titleBar.inactiveBackground'),
                 ('input.foreground', 'input.background'), ('input.placeholderForeground', 'input.background'),
                 ('list.activeSelectionForeground', 'list.activeSelectionBackground'),
                 ('editor.selectionForeground', 'editor.selectionBackground'),
                 ('activityBarBadge.foreground', 'activityBarBadge.background'),
                 ('editorLineNumber.foreground', 'editor.background'),
                 ('editorError.foreground', 'editor.background'),
                 ('editorWarning.foreground', 'editor.background'),
                 ('editorInfo.foreground', 'editor.background'),
                 ('gitDecoration.addedResourceForeground', 'sideBar.background'),
                 ('gitDecoration.deletedResourceForeground', 'sideBar.background'),
                 ('editorLineNumber.foreground', 'diffEditorGutter.insertedLineBackground'),
                 ('editorLineNumber.foreground', 'diffEditorGutter.removedLineBackground')]
        ui_ratios = {f'{fg} / {bg}': round(contrast(colors[fg], colors[bg]), 3) for fg, bg in pairs}
        for pair, ratio in ui_ratios.items():
            assert ratio >= 4.5, (mode, pair, ratio)
        surfaces = {'editor': colors['editor.background'], 'currentLine': colors['editor.lineHighlightBackground'],
                    'addedLine': diff['addLine'], 'deletedLine': diff['deleteLine'],
                    'addedWord': diff['addWord'], 'deletedWord': diff['deleteWord']}
        native_contrast = {scope: {surface: round(contrast(color, bg), 3) for surface, bg in surfaces.items()}
                           for scope, color in syntax.items()}
        below_aa = {scope: ratio['editor'] for scope, ratio in native_contrast.items() if ratio['editor'] < 4.5}
        if mode == 'light':
            assert colors['titleBar.activeBackground'] == '#C4B7D7'
            assert colors['button.background'] == colors['statusBar.background'] == '#705697'
            assert syntax['keyword'] == '#A71D5D' and syntax['string'] == '#183691'
        else:
            assert syntax['keyword'] == '#F92672' and syntax['_storage'] == '#66D9EF'
        report['themes'][mode] = {'nativeSyntaxPalette': source['syntax'][mode]['name'],
                                 'uiMinimumCheckedContrast': min(ui_ratios.values()), 'uiRatios': ui_ratios,
                                 'nativeSyntaxContrast': native_contrast, 'nativeBelowAAOnEditor': below_aa}
    vsix = ROOT / f"dist/{package['name']}-{package['version']}.vsix"
    with zipfile.ZipFile(vsix) as archive:
        assert archive.testzip() is None
        for relative in [entry['path'] for entry in package['contributes']['themes']] + [
                'terminal/windows-terminal.json', 'terminal/kitty-light.conf', 'terminal/kitty-dark.conf']:
            assert archive.read('extension/' + Path(relative).as_posix()) == (ROOT / relative).read_bytes()
        ET.fromstring(archive.read('extension.vsixmanifest'))
        ET.fromstring(archive.read('[Content_Types].xml'))
        assert json.loads(archive.read('extension/package.json')) == package
        assert json.loads(archive.read('extension/sources/claude-code-2.1.322-palette.json')) == source
        assert not any(name.endswith(('.js', '.ts', '.py')) for name in archive.namelist())
    (ROOT / 'dist/contrast-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('PASS — native syntax/state colors and rendered Diff match; valid theme-only VSIX')
    for mode, result in report['themes'].items():
        print(f"{mode}: {result['nativeSyntaxPalette']}; UI minimum {result['uiMinimumCheckedContrast']}:1")
        print('Native colors preserved below 4.5:1:', result['nativeBelowAAOnEditor'])


if __name__ == '__main__':
    check()
