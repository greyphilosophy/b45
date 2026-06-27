"""Core b45 encoder and decoder."""

from __future__ import annotations

import string

_QR_ALPHANUMERIC = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
_PASS_THROUGH = set(string.digits + " $*-. ")
_HEX = set(string.hexdigits.upper())
_SHIFT_ESCAPES = {
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
_SHIFT_ESCAPE_KEYS_BY_CHAR = {value: key for key, value in _SHIFT_ESCAPES.items()}


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
        if char in ',:':
            index = _encode_special_run(text, index, ',:', parts)
            continue
        if char in '"/':
            index = _encode_special_run(text, index, '"/', parts)
            continue
        _encode_char(char, parts)
        index += 1
    return "".join(parts)


def _encode_special_run(text: str, index: int, alphabet: str, parts: list[str]) -> int:
    start = index
    while index < len(text) and text[index] in alphabet:
        index += 1

    if index - start == 1:
        char = text[start]
        if char == ",":
            parts.append(":")
        elif char == ":":
            parts.append("::")
        elif char == '"':
            parts.append("/")
        else:
            parts.append("//")
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
    elif char in _SHIFT_ESCAPE_KEYS_BY_CHAR:
        parts.append(f"+{_SHIFT_ESCAPE_KEYS_BY_CHAR[char]}")
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
            if index + 1 >= length:
                raise ValueError("dangling '+' escape at end of input")
            next_char = encoded[index + 1]
            if next_char == "+":
                output.append("+")
            elif "A" <= next_char <= "Z":
                output.append(next_char)
            elif next_char in _SHIFT_ESCAPES:
                output.append(_SHIFT_ESCAPES[next_char])
            else:
                raise ValueError(f"invalid '+' escape at position {index}: '+{next_char}'")
            index += 2
            continue

        if char == ":":
            if index + 1 < length and encoded[index + 1] == ":":
                output.append(":")
                index += 2
            else:
                output.append(",")
                index += 1
            continue

        if char == "/":
            if index + 1 < length and encoded[index + 1] == "/":
                output.append("/")
                index += 2
            else:
                output.append('"')
                index += 1
            continue

        if char == "%":
            if index + 1 < length and encoded[index + 1] == "%":
                output.append("%")
                index += 2
                continue

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
                output.append(bytes(bytes_run).decode("utf-8"))
            except UnicodeDecodeError as exc:
                raise ValueError(
                    f"invalid UTF-8 byte escape run starting at position {start}"
                ) from exc
            continue

        if "A" <= char <= "Z":
            output.append(char.lower())
        elif char in _PASS_THROUGH:
            output.append(char)
        else:
            raise ValueError(f"invalid b45 character at position {index}: {char!r}")
        index += 1

    return "".join(output)


def _is_hex_byte(value: str) -> bool:
    return len(value) == 2 and all(char in _HEX for char in value)
