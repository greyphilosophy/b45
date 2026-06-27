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
    ("hello, world", "HELLO%2C WORLD"),
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
        ("0123456789 $*-. /:", "0123456789 $*-. /:"),
        (",'", "%2C%27"),
    ],
)
def test_encode_decode_cases(text, encoded):
    assert encode(text) == encoded
    assert decode(encoded) == text


def test_mixed_round_trip():
    text = "Hello, QR + b45 % café 😀"
    assert decode(encode(text)) == text


@pytest.mark.parametrize("encoded", ["+", "+1", "%", "%G0", "%C3%28", "_"])
def test_invalid_encoded_input_raises_value_error(encoded):
    with pytest.raises(ValueError):
        decode(encoded)
