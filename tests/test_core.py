import pytest

from b45 import decode, encode, is_canonical


def test_encode_readme_example():
    assert encode("The quick brown fox jumps over the lazy dog.") == (
        "+THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG."
    )


def test_decode_readme_example():
    assert decode("+THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG.") == (
        "The quick brown fox jumps over the lazy dog."
    )


TEST_VECTORS = [
    ("hello world", "HELLO WORLD"),
    ("Hello World", "+HELLO +WORLD"),
    ("a+b", "A++B"),
    ("50% off", "50%% OFF"),
    ("can't", "CAN/T"),
    ("wow! @you #1 ^up & down (ok)?", "WOW+1 +2YOU +31 +6UP +7 DOWN +9OK+0+/"),
    ("hello, world", "HELLO..WORLD"),
    ('say "hi"', "SAY *HI*"),
    ("ratio 1:2", "RATIO 1:2"),
    ("path/to", "PATH%2FTO"),
    ("é", "%C3%A9"),
    ("😀", "%F0%9F%98%80"),
    (
        "The quick brown fox jumps over the lazy dog.",
        "+THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG.",
    ),
]


@pytest.mark.parametrize(("text", "encoded"), TEST_VECTORS)
def test_test_vectors(text, encoded):
    assert encode(text) == encoded
    assert decode(encoded) == text
    assert decode(encode(text)) == text


@pytest.mark.parametrize(
    ("text", "encoded"),
    [
        ("abcxyz", "ABCXYZ"),
        ("ABCXYZ", "+A+B+C+X+Y+Z"),
        ("+%", "++%%"),
        ("!@#^&()?;", "+1+2+3+6+7+9+0+/+:"),
        ("$%*", "$%%%2A"),
        ("0123456789 $*.", "0123456789 $%2A."),
        ("rock-n-roll", "ROCK-N-ROLL"),
        (",'", "../"),
        ("''", "//"),
        ("'-", "/-"),
        ('"/,:', "*%2F%2C:"),
    ],
)
def test_encode_decode_cases(text, encoded):
    assert encode(text) == encoded
    assert decode(encoded) == text


@pytest.mark.parametrize("encoded", ["HELLO", "%%", "%C3%A9"])
def test_is_canonical_accepts_canonical_forms(encoded):
    assert is_canonical(encoded) is True
    assert encode(decode(encoded)) == encoded


@pytest.mark.parametrize(
    "encoded",
    [
        "%24",  # decodes as $, but literal $ is shorter
        "%25",  # decodes as %, but %% is canonical
        "%22",  # decodes as double quote, but * is shorter
        "%27",  # decodes as apostrophe, but / is shorter
    ],
)
def test_is_canonical_rejects_decodable_non_canonical_forms(encoded):
    assert decode(encoded)
    assert is_canonical(encoded) is False
    assert encode(decode(encoded)) != encoded


def test_is_canonical_rejects_invalid_encoded_input():
    assert is_canonical("+") is False


def test_mixed_round_trip():
    text = 'Hello, "QR" + b45 / 100%: café 😀'
    assert decode(encode(text)) == text


@pytest.mark.parametrize(
    "encoded",
    [
        "+",  # bare trailing plus
        "%",  # bare trailing percent
        "+%",
        "+-",
        "+4",
        "+5",
        "+8",
        "%A",  # percent followed by fewer than two characters
        "%G0",  # percent followed by non-hex characters
        "%0G",
        "%C3%28",  # percent escapes that form invalid UTF-8
        "_",  # outside the QR Alphanumeric alphabet
        "abc",
    ],
)
def test_invalid_encoded_input_raises_value_error(encoded):
    with pytest.raises(ValueError):
        decode(encoded)


def test_encoding_is_total_for_valid_unicode_strings():
    text = 'Hello, "b45" + 100% / — café 😀\0'
    assert decode(encode(text)) == text
