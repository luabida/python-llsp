from lsprotocol import types as lsp
import jedi

def suggest_import(name, script: jedi.Script) -> lsp.CodeAction:
    suggestions = []
    completions = script.complete(line=1, column=0)

    for comp in completions:
        if comp.name != name:
            continue
        if not comp.module_name:
            continue
        suggestions.append(f"from {comp.module_name} import {name}\n")

    seen = set()
    ordered = []
    for imp in suggestions:
        if imp not in seen:
            seen.add(imp)
            ordered.append(imp)

    actions = []
    for stmt in ordered:
        actions.append(lsp.CodeAction(
            title=f"Add import: {stmt.strip()}",
            kind=lsp.CodeActionKind.QuickFix,
            edit=lsp.WorkspaceEdit(
                changes={
                    uri: [
                        lsp.TextEdit(
                            range=lsp.Range(start=lsp.Position(line=0, character=0), end=lsp.Position(line=0, character=0)),
                            new_text=stmt
                        )
                    ]
                }
            )
        ))

    return actions
