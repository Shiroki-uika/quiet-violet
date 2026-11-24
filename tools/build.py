#!/usr/bin/env python3
"""Build a dependency-free, declarative VS Code theme extension and VSIX."""
import json
from pathlib import Path
import zipfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CLI = json.loads((ROOT / "sources/claude-code-2.1.322-palette.json").read_text())
PALETTES = {
    "light": dict(
        bg="#F8F8F8", fg="#333333", muted="#64616E", faint="#76717D",
        sidebar="#F0EEF3", surface="#EBE7F0", elevated="#FCFAFD", border="#CBC5D2",
        accent="#705697", accentText="#705697", focus="#9769DC", accentSoft="#E5DCF0",
        title="#C4B7D7", titleFg="#382D46", titleInactive="#D6CFE2",
        button="#705697", buttonFg="#FFFFFF", buttonHover="#604783",
        status="#705697", statusFg="#FFFFFF", hover="#E8E2EF", selection="#E6DFF0",
        line="#F1EDF5", yellow="#765600", warningBg="#F4ECD2",
        terminalBg="#F8F8F8", shadow="#382D4622",
    ),
    "dark": dict(
        bg="#1E1E1E", fg="#F8F8F2", muted="#B5ACBF", faint="#9A90A7",
        sidebar="#25212D", surface="#302938", elevated="#2B2533", border="#51465D",
        accent="#C4B0DF", accentText="#C4B0DF", focus="#C4B0DF", accentSoft="#40334F",
        title="#40334F", titleFg="#E9DFF5", titleInactive="#2E2738",
        button="#BDA3DB", buttonFg="#241D2D", buttonHover="#CDB7E6",
        status="#493759", statusFg="#F4EDF9", hover="#352D40", selection="#302B3A",
        line="#242126", yellow="#FFCC00", warningBg="#393322",
        terminalBg="#1E1E1E", shadow="#00000055",
    ),
}


def transparent_word_color(word, line):
    """At alpha 128, reproduce the native word background over its line."""
    alpha = 128 / 255
    rgb = [round((int(word[i:i + 2], 16) - int(line[i:i + 2], 16) * (1 - alpha)) / alpha)
           for i in (1, 3, 5)]
    if any(not 0 <= x <= 255 for x in rgb):
        raise ValueError("Cannot represent native word color with this alpha")
    return "#" + "".join(f"{x:02X}" for x in rgb) + "80"


def make_theme(mode):
    state = CLI["themes"][mode + "-daltonized"]["colors"]
    syntax = CLI["syntax"][mode]["scopes"]
    diff = CLI["renderedDiff"][mode]["colors"]
    p = dict(PALETTES[mode], blue=state["success"], red=state["error"],
             pink=syntax["keyword"], teal=syntax["_storage"], comment=syntax["comment"],
             string=syntax["string"], number=syntax["number"], addBg=diff["addLine"], delBg=diff["deleteLine"])
    colors = {}

    def put(value, *keys):
        for key in keys:
            colors[key] = p.get(value, value)

    put("fg", "foreground", "editor.foreground", "descriptionForeground", "icon.foreground",
        "input.foreground", "dropdown.foreground", "sideBar.foreground", "panelTitle.activeForeground",
        "tab.activeForeground", "tab.inactiveForeground", "editorWidget.foreground",
        "notificationCenterHeader.foreground", "notifications.foreground", "breadcrumb.foreground",
        "quickInput.foreground", "menu.foreground", "agentsChatInput.foreground")
    put("bg", "editor.background", "panel.background", "tab.activeBackground", "agentsPanel.background")
    put("sidebar", "sideBar.background", "editorGroupHeader.tabsBackground", "tab.inactiveBackground",
        "activityBar.background", "agents.background", "agentsNewSessionButton.background")
    put("surface", "sideBarSectionHeader.background", "editorGroupHeader.noTabsBackground",
        "notificationCenterHeader.background", "button.secondaryBackground", "input.background",
        "inputOption.hoverBackground", "badge.background", "textBlockQuote.background")
    put("elevated", "dropdown.background", "editorWidget.background", "quickInput.background",
        "notifications.background", "menu.background", "peekViewEditor.background",
        "peekViewResult.background", "terminalStickyScroll.background", "agentsChatInput.background")
    put("border", "sideBar.border", "sideBarSectionHeader.border", "panel.border", "panelSection.border",
        "editorGroup.border", "editorWidget.border", "input.border", "dropdown.border", "menu.border",
        "notifications.border", "widget.border", "tab.border", "tab.lastPinnedBorder",
        "agentsPanel.border", "agentsChatInput.border", "agentsNewSessionButton.border",
        "chat.requestBorder", "terminal.border")
    put("accent", "activityBar.foreground", "activityBar.activeBorder", "activityBarBadge.background",
        "badge.foreground", "progressBar.background", "panelTitle.activeBorder", "tab.activeBorderTop",
        "tab.unfocusedActiveBorderTop", "editorCursor.foreground", "editorLineNumber.activeForeground",
        "list.highlightForeground", "list.focusHighlightForeground", "textLink.foreground",
        "textLink.activeForeground", "textBlockQuote.border", "textSeparator.foreground",
        "settings.modifiedItemIndicator", "sash.hoverBorder", "keybindingLabel.foreground",
        "modernSash.gripForeground", "agentsChatInput.focusBorder")
    put("focus", "focusBorder", "inputOption.activeBorder", "list.focusOutline", "contrastActiveBorder")
    put("accentSoft", "inputOption.activeBackground", "chat.requestBackground",
        "welcomePage.tileBackground", "editor.wordHighlightBackground", "editor.wordHighlightStrongBackground")
    put("fg", "inputOption.activeForeground", "list.activeSelectionForeground",
        "list.inactiveSelectionForeground", "list.focusForeground", "list.hoverForeground")
    put("selection", "selection.background", "editor.selectionBackground", "editor.inactiveSelectionBackground",
        "list.activeSelectionBackground", "list.inactiveSelectionBackground", "list.focusBackground",
        "quickInputList.focusBackground", "editor.selectionHighlightBackground", "minimap.selectionHighlight")
    put("hover", "list.hoverBackground", "tab.hoverBackground", "toolbar.hoverBackground",
        "button.secondaryHoverBackground")
    put("line", "editor.lineHighlightBackground", "editor.stackFrameHighlightBackground")
    put("muted", "activityBar.inactiveForeground", "editorLineNumber.foreground", "editorCodeLens.foreground",
        "editorInlayHint.foreground", "input.placeholderForeground", "panelTitle.inactiveForeground",
        "tab.unfocusedInactiveForeground", "tab.unfocusedActiveForeground", "disabledForeground",
        "terminalCommandDecoration.defaultBackground", "gitDecoration.ignoredResourceForeground")
    put("surface", "editorInlayHint.background")
    put("faint", "editorWhitespace.foreground", "editorIndentGuide.background1")
    put("accent", "editorIndentGuide.activeBackground1", "editorBracketMatch.border")
    put("accentSoft", "editorBracketMatch.background")
    put("title", "titleBar.activeBackground")
    put("titleFg", "titleBar.activeForeground", "titleBar.inactiveForeground")
    put("titleInactive", "titleBar.inactiveBackground")
    put("button", "button.background", "extensionButton.prominentBackground")
    put("buttonFg", "button.foreground", "extensionButton.prominentForeground", "activityBarBadge.foreground")
    put("buttonHover", "button.hoverBackground", "extensionButton.prominentHoverBackground")
    put("fg", "button.secondaryForeground")
    put("status", "statusBar.background", "statusBar.noFolderBackground", "statusBar.debuggingBackground",
        "statusBar.inactiveBackground", "statusBarItem.remoteBackground")
    put("statusFg", "statusBar.foreground", "statusBar.noFolderForeground", "statusBar.debuggingForeground",
        "statusBarItem.remoteForeground")
    put("#FFFFFF20", "statusBarItem.hoverBackground")
    put("shadow", "widget.shadow", "scrollbar.shadow")
    put("#70569744" if mode == "light" else "#C4B0DF44", "scrollbarSlider.background")
    put("#70569777" if mode == "light" else "#C4B0DF77", "scrollbarSlider.hoverBackground")
    put("#705697AA" if mode == "light" else "#C4B0DFAA", "scrollbarSlider.activeBackground")
    put("blue", "editorInfo.foreground", "editorGutter.addedBackground", "diffEditorGutter.insertedLineBackground",
        "gitDecoration.addedResourceForeground", "gitDecoration.untrackedResourceForeground",
        "terminalCommandDecoration.successBackground", "testing.iconPassed", "debugIcon.startForeground",
        "charts.blue", "charts.green", "ports.iconRunningProcessForeground", "editorOverviewRuler.addedForeground",
        "minimapGutter.addedBackground", "inputValidation.infoBorder")
    put("red", "editorError.foreground", "errorForeground", "list.errorForeground",
        "editorOverviewRuler.errorForeground", "minimap.errorHighlight", "editorGutter.deletedBackground",
        "diffEditorGutter.removedLineBackground", "gitDecoration.deletedResourceForeground",
        "gitDecoration.conflictingResourceForeground", "terminalCommandDecoration.errorBackground",
        "testing.iconFailed", "charts.red", "editorOverviewRuler.deletedForeground",
        "minimapGutter.deletedBackground", "inputValidation.errorBorder")
    put("yellow", "editorWarning.foreground", "list.warningForeground", "problemsWarningIcon.foreground",
        "gitDecoration.stageDeletedResourceForeground", "inputValidation.warningBorder", "charts.yellow")
    put("accent", "editorGutter.modifiedBackground", "gitDecoration.modifiedResourceForeground",
        "editorOverviewRuler.modifiedForeground", "minimapGutter.modifiedBackground", "charts.purple")
    put("blue", "problemsInfoIcon.foreground")
    put("red", "problemsErrorIcon.foreground")
    put("muted", "editorHint.foreground")
    put("addBg", "diffEditor.insertedLineBackground", "diffEditorGutter.insertedLineBackground",
        "inputValidation.infoBackground")
    put("delBg", "diffEditor.removedLineBackground", "diffEditorGutter.removedLineBackground",
        "inputValidation.errorBackground")
    put(transparent_word_color(diff["addWord"], diff["addLine"]), "diffEditor.insertedTextBackground")
    put(transparent_word_color(diff["deleteWord"], diff["deleteLine"]), "diffEditor.removedTextBackground")
    put("fg", "editor.selectionForeground")
    put("warningBg", "inputValidation.warningBackground", "editor.findMatchBackground")
    put("fg", "inputValidation.infoForeground", "inputValidation.errorForeground", "inputValidation.warningForeground",
        "editor.findMatchForeground")
    put("yellow", "editor.findMatchBorder", "editor.findMatchHighlightBorder")
    put("warningBg", "editor.findMatchHighlightBackground")
    put("accent", "peekView.border", "peekViewTitleLabel.foreground", "pickerGroup.foreground")
    put("surface", "peekViewTitle.background")
    put("selection", "peekViewResult.selectionBackground")
    put("fg", "peekViewResult.selectionForeground")
    put("blue", "editorBracketHighlight.foreground1", "editorBracketHighlight.foreground4")
    put("accent", "editorBracketHighlight.foreground2", "editorBracketHighlight.foreground5")
    put("pink", "editorBracketHighlight.foreground3", "editorBracketHighlight.foreground6")
    put("red", "editorBracketHighlight.unexpectedBracket.foreground")
    put("terminalBg", "terminal.background")
    put("fg", "terminal.foreground", "terminalCursor.foreground")
    put("selection", "terminal.selectionBackground")
    # ANSI success stays blue and errors stay red. Native truecolor syntax is
    # independently reproduced below; it is not this ANSI slot mapping.
    ansi = {
        "Black": p["muted"], "Red": p["red"], "Green": p["blue"], "Yellow": p["yellow"],
        "Blue": state["permission"], "Magenta": p["pink"], "Cyan": p["teal"], "White": p["fg"],
    }
    for name, value in ansi.items():
        put(value, f"terminal.ansi{name}", f"terminal.ansiBright{name}")

    rules = []

    def token(name, scope, color, style=""):
        rules.append(dict(name=name, scope=scope, settings=dict(foreground=p.get(color, color), fontStyle=style)))

    token("Default / embedded", ["meta.embedded", "source.groovy.embedded", "meta.jsx.children"], "fg")
    token("Comments", ["comment", "punctuation.definition.comment", "meta.preprocessor"], syntax["comment"])
    token("Keywords", "keyword", syntax["keyword"])
    token("Storage declarations", ["storage", "storage.type", "storage.modifier"], syntax["_storage"])
    token("Operators", "keyword.operator", syntax["operator"])
    token("Punctuation", "punctuation", syntax["punctuation"])
    token("Variables", ["variable", "support.variable"], syntax["variable"])
    token("Parameters", "variable.parameter", syntax["params"])
    token("Functions", "entity.name.function", syntax["title.function"])
    token("Built-in functions / types", ["support.function", "support.type", "support.class"], syntax["built_in"])
    token("Class titles", ["entity.name.type", "entity.name.class", "entity.name.namespace",
        "entity.other.inherited-class"], syntax["title.class"])
    token("Strings", "string", syntax["string"])
    token("Numbers", "constant.numeric", syntax["number"])
    token("Literals", ["constant.language", "support.constant", "constant.character"], syntax["literal"])
    token("Language variables", "variable.language", syntax["variable.language"])
    token("Symbols", "constant.other.symbol", syntax["symbol"])
    token("Escapes and regular expressions", ["constant.character.escape", "string.regexp"], syntax["regexp"])
    token("Tags", "entity.name.tag", syntax["keyword"])
    token("Attributes", ["entity.other.attribute-name", "support.type.property-name"], syntax["attr"])
    token("Properties", ["variable.other.property", "variable.other.object.property"], syntax["property"])
    token("CSS values", "support.constant.property-value", syntax["string"])
    token("Invalid", ["invalid", "markup.error"], "red", "underline")
    token("Markdown headings", ["markup.heading", "entity.name.section"], "accentText", "bold")
    token("Markdown links", ["markup.underline.link", "meta.link"], "blue", "underline")
    token("Markdown inline code", ["markup.inline.raw", "markup.raw"], syntax["string"])
    token("Markdown quote", "markup.quote", "muted", "italic")
    token("Markdown emphasis", "markup.italic", "fg", "italic")
    token("Markdown strong", "markup.bold", "fg", "bold")
    token("Markdown strikethrough", "markup.strikethrough", "muted", "strikethrough")
    token("Diff addition (+)", "markup.inserted", diff["addDecoration"])
    token("Diff deletion (-)", "markup.deleted", diff["deleteDecoration"])
    token("Diff change", "markup.changed", "accentText")
    semantic = {
        "variable": syntax["variable"], "property": syntax["property"], "parameter": syntax["params"],
        "function": syntax["title.function"], "method": syntax["title.function"],
        "function.defaultLibrary": syntax["built_in"], "method.defaultLibrary": syntax["built_in"],
        "type": syntax["type"], "class": syntax["title.class"], "interface": syntax["title.class"],
        "enum": syntax["title.class"], "namespace": syntax["title.class"], "typeParameter": syntax["type"],
        "keyword": syntax["keyword"], "modifier": syntax["_storage"],
        "string": syntax["string"], "number": syntax["number"], "regexp": syntax["regexp"],
        "comment": syntax["comment"], "operator": syntax["operator"],
        "enumMember": syntax["literal"], "variable.readonly": syntax["variable"],
        "*.deprecated": dict(strikethrough=True),
    }
    return {"$schema": "vscode://schemas/color-theme", "name": f"Quiet Violet {mode.title()}",
            "type": mode, "semanticHighlighting": True, "colors": colors,
            "tokenColors": rules, "semanticTokenColors": semantic}


def build_terminal_schemes(themes):
    directory = ROOT / "terminal"
    directory.mkdir(exist_ok=True)
    windows_schemes = []
    ansi_names = ("Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White")
    for mode, theme in themes.items():
        colors = theme["colors"]
        scheme = {"name": theme["name"], "background": colors["terminal.background"],
                  "foreground": colors["terminal.foreground"], "cursorColor": colors["editorCursor.foreground"],
                  "selectionBackground": colors["terminal.selectionBackground"]}
        kitty = [f"background {scheme['background']}", f"foreground {scheme['foreground']}",
                 f"cursor {scheme['cursorColor']}", f"selection_background {scheme['selectionBackground']}",
                 f"selection_foreground {scheme['foreground']}"]
        for prefix in ("", "Bright"):
            for index, name in enumerate(ansi_names):
                color = colors[f"terminal.ansi{prefix}{name}"]
                key = "purple" if name == "Magenta" else name.lower()
                scheme["bright" + key.capitalize() if prefix else key] = color
                kitty.append(f"color{index + (8 if prefix else 0)} {color}")
        (directory / f"kitty-{mode}.conf").write_text("\n".join(kitty) + "\n")
        windows_schemes.append(scheme)
    (directory / "windows-terminal.json").write_text(json.dumps(windows_schemes, indent=2) + "\n")


def build():
    (ROOT / "themes").mkdir(exist_ok=True)
    themes = {mode: make_theme(mode) for mode in PALETTES}
    for mode, theme in themes.items():
        path = ROOT / "themes" / f"quiet-violet-{mode}.json"
        path.write_text(json.dumps(theme, ensure_ascii=False, indent=2) + "\n")
    build_terminal_schemes(themes)
    package = json.loads((ROOT / "package.json").read_text())
    name, publisher, version = (package[k] for k in ("name", "publisher", "version"))
    title, description = (escape(package[k]) for k in ("displayName", "description"))
    manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
 <Metadata><Identity Language="en-US" Id="{name}" Version="{version}" Publisher="{publisher}"/>
 <DisplayName>{title}</DisplayName><Description xml:space="preserve">{description}</Description>
 <Tags>theme,colorblind,accessible,purple,light,dark</Tags><Categories>Themes</Categories>
 <Properties><Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.85.0"/>
 <Property Id="Microsoft.VisualStudio.Code.ExtensionDependencies" Value=""/>
 <Property Id="Microsoft.VisualStudio.Code.ExtensionPack" Value=""/>
 <Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="ui"/>
 <Property Id="Microsoft.VisualStudio.Code.LocalizedLanguages" Value=""/>
 <Property Id="Microsoft.VisualStudio.Code.EnabledApiProposals" Value=""/>
 <Property Id="Microsoft.VisualStudio.Code.ExecutesCode" Value="false"/></Properties></Metadata>
 <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation><Dependencies/>
 <Assets><Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
 <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true"/>
 <Asset Type="Microsoft.VisualStudio.Services.Content.License" Path="extension/LICENSE" Addressable="true"/></Assets>
</PackageManifest>'''
    content_types = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="json" ContentType="application/json"/><Default Extension="vsixmanifest" ContentType="text/xml"/><Default Extension="md" ContentType="text/markdown"/><Default Extension="conf" ContentType="text/plain"/><Default Extension="png" ContentType="image/png"/><Default Extension="" ContentType="text/plain"/></Types>'''
    (ROOT / "dist").mkdir(exist_ok=True)
    vsix = ROOT / "dist" / f"{name}-{version}.vsix"
    with zipfile.ZipFile(vsix, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("extension.vsixmanifest", manifest)
        archive.writestr("[Content_Types].xml", content_types)
        for relative in ["package.json", "README.md", "DESIGN.md", "LICENSE", "sources/claude-code-2.1.322-palette.json",
                         "themes/quiet-violet-light.json", "themes/quiet-violet-dark.json",
                         "terminal/kitty-light.conf", "terminal/kitty-dark.conf", "terminal/windows-terminal.json"]:
            archive.write(ROOT / relative, "extension/" + relative)
    print(vsix)


if __name__ == "__main__":
    build()
