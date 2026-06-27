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

Characters outside the supported alphabet are encoded using hexadecimal
escapes.

    ,

↓

    %2C

    '

↓

    %27

Hexadecimal digits use uppercase `A–F`.

------------------------------------------------------------------------

## Example

Original

    The quick brown fox jumps over the lazy dog.

Encoded

    +THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG.

------------------------------------------------------------------------

## Decoding

Decode left to right.

1.  `++` → `+`
2.  `%%` → `%`
3.  `%HH` → byte represented by hexadecimal value `HH`
4.  `+X` → uppercase `X`
5.  Remaining alphabetic characters → lowercase
6.  Remaining supported characters pass through unchanged

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

Undecided.

This repository currently documents the concept and serves as a
checkpoint for future research.
