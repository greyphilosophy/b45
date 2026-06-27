"""Core b45 encoder and decoder."""

from __future__ import annotations

import string

_QR_ALPHANUMERIC = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
_PASS_THROUGH = set(string.digits + " $*-. ")
_HEX = set(string.hexdigits.upper())
_SHIFT_DECODE_BY_KEY = {
    "1": "!",
    "2": "@",
    "3": "#",
    "4": "$",
    "5": "%",
    "6": "^",
    "7": "&",
    "8": "*",
    "9": "(",
    "0": ")",
    "/": "?",
}
_SHIFT_ENCODE_BY_CHAR = {value: key for key, value in _SHIFT_DECODE_BY_KEY.items()}
_SPECIAL_RUN_ALPHABET_BY_CHAR = {
    ",": ",:",
    ":": ",:",
    '"': '"/',
    "/": '"/',
}
_SPECIAL_SINGLE_ESCAPE_BY_CHAR = {
    ",": ":",
    ":": "::",
    '"': "/",
    "/": "//",
}
_SPECIAL_DOUBLE_ESCAPE_BY_CHAR = {
    ":": ":",
    "/": "/",
}
_SPECIAL_SINGLE_DECODE_BY_CHAR = {
    ":": ",",
    "/": '"',
}


def encode(text: str) -> str:
    """Encode Unicode text as b45 QR Alphanumeric text.

    Lowercase ASCII letters are uppercased, original uppercase ASCII letters
    are escaped as ``+X``, literal ``+`` and ``%`` are doubled, isolated common
    ``,`` and ``"`` characters use ``:`` and ``/``, isolated literal ``:`` and
    ``/`` use ``::`` and ``//``, keyboard-shift punctuation uses ``+``
    escapes, supported QR Alphanumeric punctuation passes through, and every
    unsupported character is emitted as uppercase UTF-8
    ``%HH`` byte escapes.
    """

    parts: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in _SPECIAL_RUN_ALPHABET_BY_CHAR:
            index = _encode_special_run(
                text, index, _SPECIAL_RUN_ALPHABET_BY_CHAR[char], parts
            )
            continue
        _encode_char(char, parts)
        index += 1
    return "".join(parts)


def _encode_special_run(text: str, index: int, alphabet: str, parts: list[str]) -> int:
    start = index
    while index < len(text) and text[index] in alphabet:
        index += 1

    if index - start == 1:
        parts.append(_SPECIAL_SINGLE_ESCAPE_BY_CHAR[text[start]])
        return index

    for char in text[start:index]:
        _encode_utf8_escape(char, parts)
    return index


def _encode_char(char: str, parts: list[str]) -> None:
    if "a" <= char <= "z":
        parts.append(char.upper())
    elif "A" <= char <= "Z":
        parts.append(f"+{char}")
    elif char == "+":
        parts.append("++")
    elif char == "%":
        parts.append("%%")
    elif char in _PASS_THROUGH:
        parts.append(char)
    elif char in _SHIFT_ENCODE_BY_CHAR:
        parts.append(f"+{_SHIFT_ENCODE_BY_CHAR[char]}")
    else:
        _encode_utf8_escape(char, parts)


def _encode_utf8_escape(char: str, parts: list[str]) -> None:
    parts.extend(f"%{byte:02X}" for byte in char.encode("utf-8"))


def decode(encoded: str) -> str:
    """Decode b45 QR Alphanumeric text back to Unicode text.

    Invalid escape sequences, characters outside the QR Alphanumeric alphabet,
    or invalid UTF-8 byte escape runs raise ``ValueError`` with a clear message.
    """

    output: list[str] = []
    index = 0
    length = len(encoded)

    while index < length:
        char = encoded[index]
        if char not in _QR_ALPHANUMERIC:
            raise ValueError(f"invalid b45 character at position {index}: {char!r}")

        if char == "+":
            decoded, index = _decode_plus_escape(encoded, index)
            output.append(decoded)
            continue

        if char in _SPECIAL_SINGLE_DECODE_BY_CHAR:
            decoded, index = _decode_special_escape(encoded, index)
            output.append(decoded)
            continue

        if char == "%":
            decoded, index = _decode_percent_run(encoded, index)
            output.append(decoded)
            continue

        if "A" <= char <= "Z":
            output.append(char.lower())
        elif char in _PASS_THROUGH:
            output.append(char)
        else:
            raise ValueError(f"invalid b45 character at position {index}: {char!r}")
        index += 1

    return "".join(output)


def _decode_plus_escape(encoded: str, index: int) -> tuple[str, int]:
    length = len(encoded)
    if index + 1 >= length:
        raise ValueError("dangling '+' escape at end of input")

    next_char = encoded[index + 1]
    if next_char == "+":
        return "+", index + 2
    if "A" <= next_char <= "Z":
        return next_char, index + 2
    if next_char in _SHIFT_DECODE_BY_KEY:
        return _SHIFT_DECODE_BY_KEY[next_char], index + 2

    raise ValueError(f"invalid '+' escape at position {index}: '+{next_char}'")


def _decode_special_escape(encoded: str, index: int) -> tuple[str, int]:
    char = encoded[index]
    if index + 1 < len(encoded) and encoded[index + 1] == char:
        return _SPECIAL_DOUBLE_ESCAPE_BY_CHAR[char], index + 2
    return _SPECIAL_SINGLE_DECODE_BY_CHAR[char], index + 1


def _decode_percent_run(encoded: str, index: int) -> tuple[str, int]:
    length = len(encoded)
    if index + 1 < length and encoded[index + 1] == "%":
        return "%", index + 2

    bytes_run = bytearray()
    start = index
    while index < length and encoded[index] == "%":
        if index + 2 >= length:
            raise ValueError(f"incomplete percent escape at position {index}")
        hex_digits = encoded[index + 1 : index + 3]
        if not _is_hex_byte(hex_digits):
            if index == start:
                raise ValueError(
                    f"invalid percent escape at position {index}: '%{hex_digits}'"
                )
            break
        bytes_run.append(int(hex_digits, 16))
        index += 3

    try:
        return bytes(bytes_run).decode("utf-8"), index
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"invalid UTF-8 byte escape run starting at position {start}"
        ) from exc


def _is_hex_byte(value: str) -> bool:
    return len(value) == 2 and all(char in _HEX for char in value)
