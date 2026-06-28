"""Reference implementation of the b45 text transform."""

from .core import decode, encode, is_canonical

__version__ = "1.0.0"

__all__ = ["decode", "encode", "is_canonical", "__version__"]
