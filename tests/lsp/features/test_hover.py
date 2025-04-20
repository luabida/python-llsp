import pytest
from lsprotocol import types as lsp

from pyllsp.lsp import server

@pytest.fixture
def dummy_server():
    return server


def test_hover(dummy_server):
    params = lsp.HoverParams(
        text_document=lsp.TextDocumentIdentifier(uri="file:///dummy.py"),
        position=lsp.Position(line=0, character=0)
    )
    # assert hover_response is not None
    # assert hover_response.contents.value == "dummy content"

