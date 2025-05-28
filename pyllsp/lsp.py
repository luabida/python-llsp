from pyllsp import __version__
from pathlib import Path

import jedi
from lsprotocol import types as lsp

from pygls.lsp.server import LanguageServer

server = LanguageServer("pyllsp", __version__)


def start() -> None:
    server.start_io()


@server.feature(lsp.TEXT_DOCUMENT_HOVER)
def hover(params: lsp.HoverParams) -> lsp.Hover:
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


@server.feature(lsp.TEXT_DOCUMENT_COMPLETION)
def completions(server: LanguageServer, params: lsp.CompletionParams):
    server.window_show_message(
        lsp.LogMessageParams(
            message="completions",
            type=lsp.MessageType.Info,
        )
    )


@server.feature(lsp.TEXT_DOCUMENT_DEFINITION)
def definition(server: LanguageServer, params: lsp.TextDocumentPositionParams):
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
def implementation(server: LanguageServer, params: lsp.TextDocumentPositionParams):
    server.window_show_message(lsp.LogMessageParams(message="implementation", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_DECLARATION)
def declaration(server: LanguageServer, params: lsp.TextDocumentPositionParams):
    server.window_show_message(lsp.LogMessageParams(message="declaration", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_TYPE_DEFINITION)
def type_definition(server: LanguageServer, params: lsp.TextDocumentPositionParams):
    server.window_show_message(lsp.LogMessageParams(message="type definition", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_REFERENCES)
def references(server: LanguageServer, params: lsp.ReferenceParams):
    server.window_show_message(lsp.LogMessageParams(message="references", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_SIGNATURE_HELP)
def signature_help(server: LanguageServer, params: lsp.SignatureHelpParams):
    server.window_show_message(lsp.LogMessageParams(message="signature help", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbol(server: LanguageServer, params: lsp.DocumentSymbolParams):
    server.window_show_message(lsp.LogMessageParams(message="document symbol", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_RENAME)
def rename(server: LanguageServer, params: lsp.RenameParams):
    server.window_show_message(lsp.LogMessageParams(message="rename", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_FORMATTING)
def formatting(server: LanguageServer, params: lsp.DocumentFormattingParams):
    server.window_show_message(lsp.LogMessageParams(message="formatting", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_CODE_ACTION)
def code_action(server: LanguageServer, params: lsp.CodeActionParams):
    server.window_show_message(lsp.LogMessageParams(message="code action", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(server: LanguageServer, params: lsp.DidOpenTextDocumentParams):
    project = jedi.get_default_project()
    server.window_show_message(lsp.LogMessageParams(message=f"{project}", type=lsp.MessageType.Info))



@server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def did_change(server: LanguageServer, params: lsp.DidChangeTextDocumentParams):
    server.window_show_message(lsp.LogMessageParams(message="did change", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(server: LanguageServer, params: lsp.DidSaveTextDocumentParams):
    server.window_show_message(lsp.LogMessageParams(message="did save", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: LanguageServer, params: lsp.DidCloseTextDocumentParams):
    server.window_show_message(lsp.LogMessageParams(message="did close", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL)
def semantic_tokens_full(server: LanguageServer, params: lsp.SemanticTokensParams):
    server.window_show_message(lsp.LogMessageParams(message="semantic tokens full", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_CODE_LENS)
def code_lens(server: LanguageServer, params: lsp.CodeLensParams):
    server.window_show_message(lsp.LogMessageParams(message="code lens", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_INLAY_HINT)
def inlay_hint(server: LanguageServer, params: lsp.InlayHintParams):
    server.window_show_message(lsp.LogMessageParams(message="inlay hint", type=lsp.MessageType.Info))


@server.feature(types.INLAY_HINT_RESOLVE)
def inlay_hint_resolve(hint: types.InlayHint):
    server.window_show_message(lsp.LogMessageParams(message="inlay hint resolve", type=lsp.MessageType.Info))


@server.feature(lsp.WORKSPACE_SYMBOL)
def workspace_symbol(server: LanguageServer, params: lsp.WorkspaceSymbolParams):
    server.window_show_message(lsp.LogMessageParams(message="workspace symbol", type=lsp.MessageType.Info))


@server.feature(lsp.WORKSPACE_DID_CHANGE_CONFIGURATION)
def did_change_configuration(server: LanguageServer, params: lsp.DidChangeConfigurationParams):
    server.window_show_message(lsp.LogMessageParams(message="did change configuration", type=lsp.MessageType.Info))


@server.feature(lsp.WORKSPACE_DID_CHANGE_WATCHED_FILES)
def did_change_watched_files(server: LanguageServer, params: lsp.DidChangeWatchedFilesParams):
    server.window_show_message(lsp.LogMessageParams(message="did change watched files", type=lsp.MessageType.Info))


@server.feature(lsp.TEXT_DOCUMENT_PREPARE_RENAME)
def prepare_rename(server: LanguageServer, params: lsp.PrepareRenameParams):
    server.window_show_message(lsp.LogMessageParams(message="prepare rename", type=lsp.MessageType.Info))


@server.feature(lsp.WINDOW_SHOW_MESSAGE_REQUEST)
def show_message_request(server: LanguageServer, params: lsp.ShowMessageRequestParams):
    server.window_show_message(lsp.LogMessageParams(message="show message request", type=lsp.MessageType.Info))


@server.feature(lsp.WINDOW_LOG_MESSAGE)
def log_message(server: LanguageServer, params: lsp.LogMessageParams):
    server.window_show_message(lsp.LogMessageParams(message="log message", type=lsp.MessageType.Info))
