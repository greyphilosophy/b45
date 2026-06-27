# b45

*A reversible, human-readable transform for QR Alphanumeric Mode.*

> **Status:** Concept Draft (Revision 0.2)

## Installation

```bash
python -m pip install -e .
```

## Python API

```python
from b45 import encode, decode

encoded = encode("Hello World")
decoded = decode(encoded)
```

## Command Line

```bash
b45 encode "Hello World"
b45 decode "+HELLO +WORLD"
```

When `TEXT` is omitted, `b45 encode` and `b45 decode` read all text from
standard input exactly as provided. This is lossless: trailing newlines are
part of the input, so they are encoded and decoded instead of being stripped.

For example, `printf` does not add a newline by default:

```bash
printf 'Hello World' | b45 encode
# +HELLO +WORLD
```

By contrast, `echo` normally appends a trailing newline, and b45 preserves it
as `%0A`:

```bash
echo 'Hello World' | b45 encode
# +HELLO +WORLD%0A
```

Use `printf` when you do not want a trailing newline included in the encoded
output.


## Interactive Playground

Try the [hosted demo](https://greyphilosophy.github.io/b45/demo.html), or open
[`docs/demo.html`](docs/demo.html) locally.

------------------------------------------------------------------------

## Overview

**b45** is a reversible text transform designed to reduce the size of QR
codes containing predominantly English text while preserving human
readability.

Unlike traditional compression algorithms, b45 does not primarily reduce
the number of characters. Instead, it transforms text into the
restricted alphabet supported by QR Code **Alphanumeric Mode**, allowing
QR encoders to use a more efficient encoding mode than Byte Mode.

The transform is deterministic, lossless, and fully reversible.

------------------------------------------------------------------------

## Motivation

QR codes support multiple encoding modes.

Byte Mode stores arbitrary bytes but requires approximately 8 bits per
character.

Alphanumeric Mode stores only the following character set:

    0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:

and encodes them much more efficiently (roughly 5.5 bits per character).

Natural English is dominated by lowercase letters, preventing direct use
of Alphanumeric Mode. b45 bridges this gap.

------------------------------------------------------------------------

## Design Goals

-   Lossless
-   Human-readable
-   Deterministic
-   Stream-decodable
-   Optimized for lowercase-heavy English text
-   Compatible with QR Alphanumeric Mode

------------------------------------------------------------------------

## Encoding Rules

### Lowercase letters

Lowercase letters become uppercase.

    hello world

↓

    HELLO WORLD

### Uppercase letters

Uppercase letters are escaped with `+`.

    Hello World

↓

    +HELLO +WORLD

### Reserved characters

Literal `+`

    ++

Literal `%`

    %%

Common comma followed by a space

    ..

Comma followed by a double quote

    ..*

Comma followed by an apostrophe / single quote

    ../

Other commas

    %2C

Common double quote

    *

Common apostrophe / single quote

    /

Literal `*`

    %2A

Literal `/`

    //

Literal `:` or `-`

    : or -

Keyboard-shift punctuation uses `+` followed by the shifted key. For
example, `!` encodes as `+1`, `@` as `+2`, `^` as `+6`, `&` as `+7`,
`;` as `+:`, and `?` as `+/`.

Literal `..` is encoded with `%HH` byte escapes to preserve unambiguous
decoding because `..` is reserved for the common comma-space pair.

### Unsupported characters

Source text is interpreted as Unicode text and encoded as UTF-8 bytes.
Characters outside the supported alphabet are then represented by one
`%HH` hexadecimal escape for each UTF-8 byte.

Non-ASCII characters are encoded as their UTF-8 byte sequences.

    é

↓

    %C3%A9

Characters outside the Basic Multilingual Plane, such as emoji, may
require multiple escapes.

    😀

↓

    %F0%9F%98%80

Hexadecimal digits use uppercase `A–F`.

------------------------------------------------------------------------

## Formal Syntax

The complete allowed output alphabet is exactly:

    0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:

Every encoded b45 output character MUST be a member of this alphabet.
Because this alphabet is identical to the QR Code Alphanumeric Mode
character set, encoded b45 output is always valid QR Alphanumeric Mode
text.

### Literal pass-through characters

The following characters pass through unchanged when they occur literally
in source text:

-   Digits: `0` through `9`
-   Space: ` `
-   QR Alphanumeric punctuation other than the escape characters `+` and
    `%`, plus punctuation repurposed as common-character escapes (`*`
    and `/`): `$`, `.`, `-`, `:`

Lowercase ASCII alphabetic characters are converted to their uppercase
forms in the output alphabet and are decoded back to lowercase. Original
uppercase ASCII alphabetic characters are escaped.

### Escape forms

The only escape forms are:

-   `++` for a literal plus sign (`+`)
-   `%%` for a literal percent sign (`%`)
-   `..` for a comma followed by a space (`, `)
-   `..*` for a comma followed by a double quote (`,"`)
-   `../` for a comma followed by an apostrophe / single quote (`,'`)
-   `*` for a double quote (`"`)
-   `/` for an apostrophe / single quote (`'`)
-   `//` for a literal slash (`/`)
-   `+1`, `+2`, `+3`, `+6`, `+7`, `+9`, `+0`, `+/`, and `+:` for `!`,
    `@`, `#`, `^`, `&`, `(`, `)`, `?`, and `;`
-   `%HH` for one escaped byte, where `HH` is two uppercase hexadecimal
    digits (`0`-`9`, `A`-`F`)
-   `+X` for an original uppercase ASCII alphabetic character, where `X`
    is `A` through `Z`

### Decoding precedence

Decoding is performed strictly left to right. At each position, apply the
first matching rule in this order:

1.  `++` decodes to a literal `+`.
2.  `+X` decodes to original uppercase alphabetic character `X`.
3.  `+` followed by a shifted-key character decodes to its keyboard-shift
    punctuation, such as `+1` to `!` and `+/` to `?`.
4.  `..*` decodes to `,"`; `../` decodes to `,'`; otherwise `..` decodes
    to `, `.
5.  `*` decodes to `"`.
6.  `//` decodes to a literal `/`; otherwise `/` decodes to `'`.
7.  `%%` decodes to a literal `%`.
8.  `%HH` decodes to the byte represented by hexadecimal value `HH`;
    adjacent byte escapes are collected and decoded as UTF-8 text.
9.  Unescaped alphabetic characters `A` through `Z` decode to lowercase
    `a` through `z`.
10. Literal pass-through characters decode to themselves.

The encoder uses `%HH` byte escapes for literal `..`, literal `*`, literal
apostrophe/slash runs such as `''`, `//`, and `'/`, commas outside the
reserved comma pairs, and comma-space before a quote so this precedence
remains unambiguous.

### Canonical encoded form

Some inputs are valid and decodable but are not the canonical spelling
produced by `encode`. For example, percent escapes such as `%24`, `%25`,
`%22`, `%27`, and `%2F` decode successfully, but shorter canonical spellings are
available.

Use `is_canonical(encoded)` to test for the canonical encoder spelling.
Equivalently, valid encoded input is canonical when:

    encode(decode(encoded)) == encoded

Invalid encoded input is not canonical.

------------------------------------------------------------------------


## Invalid Encoded Input

Decoders MUST treat malformed encoded input as invalid and reject it with
an explicit error. Decoders MUST NOT silently guess, repair, or reinterpret
malformed input.

The following encoded inputs are invalid:

-   A bare trailing `+`.
-   A bare trailing `%`.
-   `+` followed by any character other than an uppercase ASCII letter
    (`A` through `Z`), another `+`, or a supported shifted key.
-   `%` followed by fewer than two characters.
-   `%` followed by characters that are not uppercase hexadecimal digits
    (`0` through `9` or `A` through `F`), except for `%%`, which is the
    literal percent escape.
-   One or more `%HH` byte escapes whose bytes do not form valid UTF-8.
-   Any character outside the QR Alphanumeric alphabet:

        0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:

Encoding remains total for all valid Unicode strings: every valid Unicode
string can be encoded as b45. These rejection requirements apply only when
decoding malformed encoded input.

------------------------------------------------------------------------

## Example

Original

    The quick brown fox jumps over the lazy dog.

Encoded

    +THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG.

------------------------------------------------------------------------


## Test Vectors

| Original | Encoded |
| --- | --- |
| `hello world` | `HELLO WORLD` |
| `Hello World` | `+HELLO +WORLD` |
| `a+b` | `A++B` |
| `50% off` | `50%% OFF` |
| `can't` | `CAN/T` |
| `wow! @you #1 ^up & down (ok)?;` | `WOW+1 +2YOU +31 +6UP +7 DOWN +9OK+0+/+:` |
| `hello, world` | `HELLO..WORLD` |
| `say "hi"` | `SAY *HI*` |
| `ratio 1:2` | `RATIO 1:2` |
| `path/to` | `PATH//TO` |
| `é` | `%C3%A9` |
| `😀` | `%F0%9F%98%80` |
| `The quick brown fox jumps over the lazy dog.` | `+THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG.` |

------------------------------------------------------------------------

## Decoding

Decode left to right. Literal escapes are restored as characters, while
`%HH` byte escapes are collected and reconstructed into bytes. The
resulting byte sequences are decoded as UTF-8 text.

1.  `++` → `+`
2.  `+X` → uppercase `X`
3.  Shift-style punctuation escapes, such as `+1` → `!` and `+/` → `?`
4.  `..*` → `,"`; `../` → `,'`; otherwise `..` → `, `
5.  `*` → `"`
6.  `//` → `/`; otherwise `/` → `'`
7.  `%%` → `%`
8.  One or more `%HH` escapes → bytes represented by hexadecimal values
    `HH`, decoded as UTF-8
9.  Remaining alphabetic characters → lowercase
10. Remaining supported characters pass through unchanged

For example, `%C3%A9` reconstructs the UTF-8 bytes `C3 A9` and decodes
to `é`; `%F0%9F%98%80` reconstructs the UTF-8 bytes `F0 9F 98 80` and
decodes to `😀`.

The encoding is unambiguous and fully reversible.

------------------------------------------------------------------------

## Characteristics

### Advantages

-   Human-readable after transformation
-   QR Alphanumeric compatible
-   Lossless
-   No dictionaries
-   No statistical models
-   Simple streaming implementation

### Less suitable for

-   Source code
-   JSON
-   Binary data
-   Unicode-heavy text
-   ALL CAPS text

------------------------------------------------------------------------

## Relationship to Base45

b45 is not a general binary-to-text Base45 codec. It is a
readability-preserving text transform.

Its output alphabet intentionally matches QR Alphanumeric Mode. The name
reflects the 45-character QR Alphanumeric alphabet, but the algorithm is
distinct from standardized Base45 binary encodings.

------------------------------------------------------------------------

## Relationship to Compression

b45 is best viewed as a **transport optimization**, not a traditional
compression algorithm.

It exploits the efficiency of QR Alphanumeric Mode by transforming text
into an alphabet that the transport medium can encode more efficiently.

------------------------------------------------------------------------

## Future Work

Possible improvements include:

-   More efficient escape sequences
-   Optimized handling of common punctuation
-   Unicode extensions
-   Automatic selection between Byte Mode and b45
-   Combining b45 with conventional compression
-   Generalization to other constrained communication channels

------------------------------------------------------------------------

## Open Questions

-   Is `+` the optimal escape character?
-   Should common punctuation receive dedicated escapes?
-   Can the transform be optimized further without sacrificing
    readability?
-   Can it be generalized beyond QR codes?

------------------------------------------------------------------------

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` for details.
