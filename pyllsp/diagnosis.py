import asyncio

import jedi
from lsprotocol import types as lsp


async def syntax_errors(script: jedi.Script) -> list[lsp.Diagnostic]:
    errors = await asyncio.to_thread(script.get_syntax_errors)
    diagnostics = []

    for err in errors:
        diagnostics.append(
            lsp.Diagnostic(
                range=lsp.Range(
                    start=lsp.Position(
                        line=err.line - 1,
                        character=max(0, (err.column or 0) - 1),
                    ),
                    end=lsp.Position(
                        line=(err.until_line - 1) if err.until_line else (err.line - 1),
                        character=max(0, (err.until_column or err.column or 0) - 1),
                    ),
                ),
                severity=lsp.DiagnosticSeverity.Error,
                source="jedi",
                message=err.get_message(),
            )
        )

    return diagnostics


async def undefined_names(script: jedi.Script) -> list[lsp.Diagnostic]:
    names = await asyncio.to_thread(script.get_names, all_scopes=True, definitions=False, references=True)
    diagnostics = []

    for name in names:
        inferred = name.infer()
        if not inferred:
            diagnostics.append(
                lsp.Diagnostic(
                    range=lsp.Range(
                        start=lsp.Position(line=name.line - 1, character=name.column or 0),
                        end=lsp.Position(line=name.line - 1, character=(name.column or 0) + len(name.name)),
                    ),
                    severity=lsp.DiagnosticSeverity.Error,
                    source="jedi",
                    message=f"Undefined name: '{name.name}'",
                )
            )

    return diagnostics
