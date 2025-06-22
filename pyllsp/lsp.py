from pyllsp import __version__
from pathlib import Path

import jedi
import trio
import asyncio
from lsprotocol import types as lsp

from .server import PyLLSPServer, Notifier
from . import diagnosis, actions


server = PyLLSPServer()
notifier = Notifier(server)


def start() -> None:
    server.start_io()


@server.feature(lsp.TEXT_DOCUMENT_HOVER)
async def hover(params: lsp.HoverParams) -> lsp.Hover:
    """
    `a`
    """
    doc = server.workspace.get_text_document(params.text_document.uri)
    code = doc.source
    line = doc.lines[params.position.line].strip()
    script = jedi.Script(code, path=doc.path)
    definitions = script.goto(
        line=params.position.line + 1,
        column=params.position.character,
        follow_imports=True
    )

    if definitions:
        definition = definitions[0]
        name = definition.name
        type = definition.type
        module_name = definition.module_name
        docstring = definition.docstring(raw=True)
        full_name = definition.full_name
        server.window_show_message(
            lsp.LogMessageParams(
                message=f"{server.workspace}",
                type=lsp.MessageType.Info,
            )
        )

        return
        return lsp.Hover(
            contents=[
                lsp.MarkedString(language="python", value=code_content),
                lsp.MarkedString(value=docstring_content)
            ]
        )

    content = (
        "   ▐▀▄       ▄▀▌   ▄▄▄▄▄▄▄             \n"
        "   ▌▒▒▀▄▄▄▄▄▀▒▒▐▄▀▀▒██▒██▒▀▀▄          \n"
        "  ▐▒▒▒▒▀▒▀▒▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▀▄        \n"
        "  ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄▒▒▒▒▒▒▒▒▒▒▒▒▀▄      \n"
        "▀█▒▒▒█▌▒▒█▒▒▐█▒▒▒▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌     \n"
        "▀▌▒▒▒▒▒▒▀▒▀▒▒▒▒▒▒▀▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐   ▄▄\n"
        "▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌▄█▒█\n"
        "▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒█▀ \n"
        "▐▒▒▒▒▒▒▒▒▒▒▒▒▒NOTHING▒▒▒▒▒▒▒▒▒▒▒▒▒█▀   \n"
        "▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌    \n"
        " ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐     \n"
        " ▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌     \n"
        "  ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐      \n"
        "  ▐▄▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄▌      \n"
        "    ▀▄▄▀▀▀▀▀▄▄▀▀▀▀▀▀▀▄▄▀▀▀▀▀▄▄▀        \n"
    )
    return lsp.Hover(
        contents=lsp.MarkupContent(
            kind=lsp.MarkupKind.PlainText,
            value=content
        )
    )


@server.feature(
    lsp.TEXT_DOCUMENT_COMPLETION,
    lsp.CompletionOptions(trigger_characters=[".", "{"])
)
async def completions(server: PyLLSPServer, params: lsp.CompletionParams):
    COMPLETION_TYPE = {
        "module": lsp.CompletionItemKind.Module,
        "class": lsp.CompletionItemKind.Class,
        "instance": lsp.CompletionItemKind.Variable,
        "function": lsp.CompletionItemKind.Function,
        "method": lsp.CompletionItemKind.Method,
        "constructor": lsp.CompletionItemKind.Constructor,
        "field": lsp.CompletionItemKind.Field,
        "variable": lsp.CompletionItemKind.Variable,
        "param": lsp.CompletionItemKind.Variable,
        "property": lsp.CompletionItemKind.Property,
        "unit": lsp.CompletionItemKind.Unit,
        "value": lsp.CompletionItemKind.Value,
        "enum": lsp.CompletionItemKind.Enum,
        "keyword": lsp.CompletionItemKind.Keyword,
        "snippet": lsp.CompletionItemKind.Snippet,
        "color": lsp.CompletionItemKind.Color,
        "file": lsp.CompletionItemKind.File,
        "reference": lsp.CompletionItemKind.Reference,
        "folder": lsp.CompletionItemKind.Folder,
        "enum_member": lsp.CompletionItemKind.EnumMember,
        "constant": lsp.CompletionItemKind.Constant,
        "struct": lsp.CompletionItemKind.Struct,
        "event": lsp.CompletionItemKind.Event,
        "operator": lsp.CompletionItemKind.Operator,
        "type_parameter": lsp.CompletionItemKind.TypeParameter,
        "statement": lsp.CompletionItemKind.Text,
        "text": lsp.CompletionItemKind.Text,
    }

    doc = server.workspace.get_text_document(params.text_document.uri)
    script = jedi.Script(
        code=doc.source,
        path=doc.path,
        project=server.project,
    )
    completions = script.complete(
        line=params.position.line + 1,
        column=params.position.character,
    )
    return [
        lsp.CompletionItem(
            label=comp.name,
            kind=COMPLETION_TYPE.get(
                comp.type.lower(),
                lsp.CompletionItemKind.Text
            ),
            detail=comp.description,
            documentation=comp.docstring()
        )
        for comp in completions
    ]


@server.feature(lsp.TEXT_DOCUMENT_DEFINITION)
async def definition(server: PyLLSPServer, params: lsp.TextDocumentPositionParams):
    doc = server.workspace.get_text_document(params.text_document.uri)
    code = doc.source
    line = params.position.line + 1
    col = params.position.character

    script = jedi.Script(code, path=doc.path)
    definitions = script.goto(line, col)

    locations = []
    for d in definitions:
        if d.module_path is None:
            continue
        uri = server.workspace.get_text_document("file:" + str(d.module_path)).uri
        locations.append(lsp.Location(
            uri=uri,
            range=lsp.Range(
                start=lsp.Position(d.line - 1, d.column),
                end=lsp.Position(d.line - 1, d.column + len(d.name))
            )
        ))

    return locations if locations else None


@server.feature(lsp.TEXT_DOCUMENT_IMPLEMENTATION)
async def implementation(server: PyLLSPServer, params: lsp.TextDocumentPositionParams):
    server.window_show_message(lsp.LogMessageParams(message="implementation", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_DECLARATION)
async def declaration(server: PyLLSPServer, params: lsp.TextDocumentPositionParams):
    server.window_show_message(lsp.LogMessageParams(message="declaration", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_TYPE_DEFINITION)
async def type_definition(server: PyLLSPServer, params: lsp.TextDocumentPositionParams):
    server.window_show_message(lsp.LogMessageParams(message="type definition", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_REFERENCES)
async def references(server: PyLLSPServer, params: lsp.ReferenceParams):
    server.window_show_message(lsp.LogMessageParams(message="references", type=lsp.MessageType.Info))


@server.feature(
    lsp.TEXT_DOCUMENT_SIGNATURE_HELP,
    lsp.SignatureHelpOptions(trigger_characters=["(", "," ])
)
async def signature_help(server: PyLLSPServer, params: lsp.SignatureHelpParams):
    doc = server.workspace.get_text_document(params.text_document.uri)
    script = jedi.Script(
        code=doc.source,
        path=doc.path,
        project=server.project,
    )
    signatures = script.get_signatures(
        line=params.position.line + 1,
        column=params.position.character,
    )

    if not signatures:
        return None

    return lsp.SignatureHelp(
        signatures=[
            lsp.SignatureInformation(
                label=s.to_string(),
                documentation=s.docstring(),
                parameters=[
                    lsp.ParameterInformation(label=p.name, documentation=p.description)
                    for p in s.params
                ],
            )
            for s in signatures
        ],
        active_signature=0,
        active_parameter=signatures[0].index or 0,
    )


@server.feature(lsp.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
async def document_symbol(server: PyLLSPServer, params: lsp.DocumentSymbolParams):
    server.window_show_message(lsp.LogMessageParams(message="document symbol", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_RENAME)
async def rename(server: PyLLSPServer, params: lsp.RenameParams):
    server.window_show_message(lsp.LogMessageParams(message="rename", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_FORMATTING)
async def formatting(server: PyLLSPServer, params: lsp.DocumentFormattingParams):
    server.window_show_message(lsp.LogMessageParams(message="formatting", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_CODE_ACTION)
async def code_action(server: PyLLSPServer, params: lsp.CodeActionParams):
    server.window_show_message(lsp.LogMessageParams(message="code action", type=lsp.MessageType.Info))
    doc = server.workspace.get_text_document(params.text_document.uri)
    script = jedi.Script(
        code=doc.source,
        path=doc.path,
        project=server.project,
    )
    actions = []

    server.window_show_message(lsp.LogMessageParams(message=f"{params.context.diagnostics}", type=lsp.MessageType.Info))
    for diag in params.context.diagnostics:
        if "undefined" not in diag.message.lower():
            continue

        line_text = source.splitlines()[diag.range.start.line]
        name = line_text[diag.range.start.character:].split()[0]

        actions.extend(actions.suggest_import(name, script))

    return actions


@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
async def did_open(server: PyLLSPServer, params: lsp.DidOpenTextDocumentParams):
    doc = server.workspace.get_text_document(params.text_document.uri)

    script = jedi.Script(
        code=doc.source,
        path=doc.path,
        project=server.project,
    )

    await notifier.notify(doc.uri, script, [
        diagnosis.syntax_errors,
        diagnosis.undefined_names,
    ])


@server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
async def did_change(server: PyLLSPServer, params: lsp.DidChangeTextDocumentParams):
    doc = server.workspace.get_text_document(params.text_document.uri)

    script = jedi.Script(
        code=doc.source,
        path=doc.path,
        project=server.project,
    )

    await notifier.notify(doc.uri, script, [
        diagnosis.syntax_errors,
        diagnosis.undefined_names,
    ])


@server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
async def did_save(server: PyLLSPServer, params: lsp.DidSaveTextDocumentParams):
    doc = server.workspace.get_text_document(params.text_document.uri)

    script = jedi.Script(
        code=doc.source,
        path=doc.path,
        project=server.project,
    )

    await notifier.notify(doc.uri, script, [
        diagnosis.syntax_errors,
        diagnosis.undefined_names,
    ])


@server.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
async def did_close(server: PyLLSPServer, params: lsp.DidCloseTextDocumentParams):
    server.window_show_message(lsp.LogMessageParams(message="did close", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL)
async def semantic_tokens_full(server: PyLLSPServer, params: lsp.SemanticTokensParams):
    server.window_show_message(lsp.LogMessageParams(message="semantic tokens full", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_CODE_LENS)
async def code_lens(server: PyLLSPServer, params: lsp.CodeLensParams):
    server.window_show_message(lsp.LogMessageParams(message="code lens", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_INLAY_HINT)
async def inlay_hint(server: PyLLSPServer, params: lsp.InlayHintParams):
    server.window_show_message(lsp.LogMessageParams(message="inlay hint", type=lsp.MessageType.Info))


@server.feature(lsp.INLAY_HINT_RESOLVE)
async def inlay_hint_resolve(hint: lsp.InlayHint):
    server.window_show_message(lsp.LogMessageParams(message="inlay hint resolve", type=lsp.MessageType.Info))


@server.feature(lsp.WORKSPACE_SYMBOL)
async def workspace_symbol(server: PyLLSPServer, params: lsp.WorkspaceSymbolParams):
    server.window_show_message(lsp.LogMessageParams(message="workspace symbol", type=lsp.MessageType.Info))


@server.feature(lsp.WORKSPACE_DID_CHANGE_CONFIGURATION)
async def did_change_configuration(server: PyLLSPServer, params: lsp.DidChangeConfigurationParams):
    server.window_show_message(lsp.LogMessageParams(message="did change configuration", type=lsp.MessageType.Info))


@server.feature(lsp.WORKSPACE_DID_CHANGE_WATCHED_FILES)
async def did_change_watched_files(server: PyLLSPServer, params: lsp.DidChangeWatchedFilesParams):
    server.window_show_message(lsp.LogMessageParams(message="did change watched files", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_PREPARE_RENAME)
async def prepare_rename(server: PyLLSPServer, params: lsp.PrepareRenameParams):
    server.window_show_message(lsp.LogMessageParams(message="prepare rename", type=lsp.MessageType.Info))


@server.feature(lsp.WINDOW_SHOW_MESSAGE_REQUEST)
async def show_message_request(server: PyLLSPServer, params: lsp.ShowMessageRequestParams):
    server.window_show_message(lsp.LogMessageParams(message="show message request", type=lsp.MessageType.Info))


@server.feature(lsp.WINDOW_LOG_MESSAGE)
async def log_message(server: PyLLSPServer, params: lsp.LogMessageParams):
    server.window_show_message(lsp.LogMessageParams(message="log message", type=lsp.MessageType.Info))
