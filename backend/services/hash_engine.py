"""Perceptual image signatures.

PDQ is used when the optional pdqhash binding is installed. The portable
ImageHash pHash algorithm is the default, and signatures are labelled so a
cryptographic hash is never confused with a perceptual image hash.
"""
from __future__ import annotations

from PIL import Image
import imagehash


class HashEngine:
    """Compute typed image signatures and compare matching signature types."""

    def compute_pdq_hash(self, image: Image.Image) -> str:
        """Return a genuine 256-bit PDQ hash when pdqhash is installed.

        The core project intentionally does not require a compiler-only native
        binding to install on every developer machine. Use compute_best_hash
        for a portable pHash fallback.
        """
        try:
            import numpy as np
            import pdqhash
        except ImportError as exc:
            raise RuntimeError("PDQ support requires the optional pdqhash package.") from exc

        bits, _quality = pdqhash.compute(np.asarray(image.convert("RGB")))
        values = np.asarray(bits).reshape(-1)
        if values.size == 256:
            bit_string = "".join("1" if bool(v) else "0" for v in values)
            value = int(bit_string, 2)
        elif values.size == 32:
            value = int.from_bytes(bytes(int(v) for v in values), "big")
        else:
            raise RuntimeError(f"Unexpected PDQ output length: {values.size}")
        return f"pdq:{value:064x}"

    def compute_phash(self, image: Image.Image) -> str:
        """Return a standard 64-bit DCT perceptual hash."""
        return f"phash:{imagehash.phash(image.convert('RGB'), hash_size=8)}"

    def compute_best_hash(self, image: Image.Image) -> str:
        """Prefer true PDQ when available, otherwise use portable pHash."""
        try:
            return self.compute_pdq_hash(image)
        except (ImportError, RuntimeError, ValueError, TypeError):
            return self.compute_phash(image)

    @staticmethod
    def _normalise(signature: str) -> tuple[str, str]:
        if ":" not in signature:
            raise ValueError("Hash signatures must include an algorithm prefix, e.g. phash:...")
        kind, value = signature.split(":", 1)
        if kind not in {"pdq", "phash"}:
            raise ValueError("Unsupported perceptual hash type.")
        if not value or any(ch not in "0123456789abcdefABCDEF" for ch in value):
            raise ValueError("Hash signatures must contain hexadecimal digits.")
        return kind, value.lower()

    def compute_hamming_distance(self, hash1: str, hash2: str) -> int:
        kind1, value1 = self._normalise(hash1)
        kind2, value2 = self._normalise(hash2)
        if kind1 != kind2:
            raise ValueError("Cannot compare different hash algorithms.")
        if len(value1) != len(value2):
            raise ValueError("Hash lengths must match.")
        return (int(value1, 16) ^ int(value2, 16)).bit_count()

    def is_similar(self, hash1: str, hash2: str, threshold: int = 10) -> bool:
        if threshold < 0:
            raise ValueError("Threshold must be non-negative.")
        return self.compute_hamming_distance(hash1, hash2) <= threshold
