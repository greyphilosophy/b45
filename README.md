# b45

*A reversible, human-readable transform for QR Alphanumeric Mode.*

> **Status:** Concept Draft (Revision 0.1)

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

### Unsupported characters

Source text is interpreted as Unicode text and encoded as UTF-8 bytes.
Characters outside the supported alphabet are then represented by one
`%HH` hexadecimal escape for each UTF-8 byte.

    ,

↓

    %2C

    '

↓

    %27

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
    `%`: `$`, `*`, `-`, `.`, `/`, `:`

Lowercase ASCII alphabetic characters are converted to their uppercase
forms in the output alphabet and are decoded back to lowercase. Original
uppercase ASCII alphabetic characters are escaped.

### Escape forms

The only escape forms are:

-   `++` for a literal plus sign (`+`)
-   `%%` for a literal percent sign (`%`)
-   `%HH` for one escaped byte, where `HH` is two uppercase hexadecimal
    digits (`0`-`9`, `A`-`F`)
-   `+X` for an original uppercase ASCII alphabetic character, where `X`
    is `A` through `Z`

### Decoding precedence

Decoding is performed strictly left to right. At each position, apply the
first matching rule in this order:

1.  `++` decodes to a literal `+`.
2.  `%%` decodes to a literal `%`.
3.  `%HH` decodes to the byte represented by hexadecimal value `HH`;
    adjacent byte escapes are collected and decoded as UTF-8 text.
4.  `+X` decodes to original uppercase alphabetic character `X`.
5.  Unescaped alphabetic characters `A` through `Z` decode to lowercase
    `a` through `z`.
6.  Literal pass-through characters decode to themselves.

This precedence makes sequences beginning with `+` or `%` unambiguous.

------------------------------------------------------------------------


## Invalid Encoded Input

Decoders MUST treat malformed encoded input as invalid and reject it with
an explicit error. Decoders MUST NOT silently guess, repair, or reinterpret
malformed input.

The following encoded inputs are invalid:

-   A bare trailing `+`.
-   A bare trailing `%`.
-   `+` followed by any character other than an uppercase ASCII letter
    (`A` through `Z`) or another `+`.
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
| `can't` | `CAN%27T` |
| `hello, world` | `HELLO%2C WORLD` |
| `é` | `%C3%A9` |
| `😀` | `%F0%9F%98%80` |
| `The quick brown fox jumps over the lazy dog.` | `+THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG.` |

------------------------------------------------------------------------

## Decoding

Decode left to right. Literal escapes are restored as characters, while
`%HH` byte escapes are collected and reconstructed into bytes. The
resulting byte sequences are decoded as UTF-8 text.

1.  `++` → `+`
2.  `%%` → `%`
3.  One or more `%HH` escapes → bytes represented by hexadecimal values
    `HH`, decoded as UTF-8
4.  `+X` → uppercase `X`
5.  Remaining alphabetic characters → lowercase
6.  Remaining supported characters pass through unchanged

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
