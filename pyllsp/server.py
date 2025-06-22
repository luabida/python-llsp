import asyncio
from collections import defaultdict
from typing import Callable, Coroutine

import jedi
from lsprotocol import types as lsp
from lsprotocol.types import TextDocumentSyncKind
from pygls.lsp.server import LanguageServer
from pygls.protocol import LanguageServerProtocol

from pyllsp import __version__


class PyLLSPServer(LanguageServer):
    def __init__(self):
        super().__init__(
            name="pyllsp",
            version=__version__,
            protocol_cls=LanguageServerProtocol,
            text_document_sync_kind=TextDocumentSyncKind.Incremental,
        )
        self.project = jedi.get_default_project()


class Notifier:
    def __init__(self, server: LanguageServer):
        self.server = server
        self._cache: dict[str, list[lsp.Diagnostic]] = defaultdict(list)

    async def notify(
        self,
        uri: str,
        script: jedi.Script,
        funcs: list[Callable[[jedi.Script], Coroutine[None, None, list[lsp.Diagnostic]]]],
        clear: bool = True,
    ):
        if clear:
            self.clear(uri)

        tasks = [func(script) for func in funcs]

        for coro in asyncio.as_completed(tasks):
            diagnostics = await coro
            self._cache[uri].extend(diagnostics)
            self._publish(uri)

    def clear(self, uri: str):
        self._cache[uri].clear()

    def _publish(self, uri: str):
        self.server.protocol.notify(
            lsp.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS,
            lsp.PublishDiagnosticsParams(uri=uri, diagnostics=self._cache[uri]),
        )
