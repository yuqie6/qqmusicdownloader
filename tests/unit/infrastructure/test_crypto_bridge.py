import base64

import pytest

from qqmusicdownloader.infrastructure.crypto.bridge import (
    NodeCryptoError,
    decrypt_response,
    encrypt_payload,
)


def test_encrypt_decrypt_roundtrip() -> None:
    plain = "{\"msg\": \"hello\"}"
    body, sign = encrypt_payload(plain)

    assert isinstance(sign, str) and sign
    payload = base64.b64decode(body)
    text, parsed = decrypt_response(payload)
    assert isinstance(text, str) and text
    if parsed is not None:
        assert isinstance(parsed, dict)


def test_encrypt_payload_propagates_node_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_request(*_args, **_kwargs):  # pragma: no cover - used only in test
        raise NodeCryptoError("boom")

    monkeypatch.setattr(
        "qqmusicdownloader.infrastructure.crypto.bridge._node_request",
        fake_request,
    )

    with pytest.raises(NodeCryptoError):
        encrypt_payload("{}")
