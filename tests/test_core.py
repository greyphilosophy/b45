import pytest

from b45 import decode, encode


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
    ("can't", "CAN%27T"),
    ("wow! @you #1 ^up & down (ok)?", "WOW+1 +2YOU +31 +6UP +7 DOWN +9OK+0+/"),
    ("hello, world", "HELLO: WORLD"),
    ('say "hi"', "SAY /HI/"),
    ("ratio 1:2", "RATIO 1::2"),
    ("path/to", "PATH//TO"),
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
        ("!@#^&()?", "+1+2+3+6+7+9+0+/"),
        ("$%*", "$%%*"),
        ("0123456789 $*-.", "0123456789 $*-."),
        (",'", ":%27"),
        ('"/,:', "%22%2F%2C%3A"),
    ],
)
def test_encode_decode_cases(text, encoded):
    assert encode(text) == encoded
    assert decode(encoded) == text


def test_decode_accepts_duplicate_shift_spellings():
    assert decode("+4+5+8") == "$%*"


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
        "+:",
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
