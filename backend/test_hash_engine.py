"""Tests for real perceptual image signatures."""
import pytest
from PIL import Image, ImageEnhance

from services.hash_engine import HashEngine


def test_phash_is_stable_for_same_image_and_has_typed_signature():
    engine = HashEngine()
    image = Image.new("RGB", (128, 128), "navy")
    first = engine.compute_phash(image)
    second = engine.compute_phash(image.copy())
    assert first.startswith("phash:")
    assert first == second
    assert engine.compute_hamming_distance(first, second) == 0
    assert engine.is_similar(first, second)


def test_phash_is_resilient_to_small_brightness_change():
    engine = HashEngine()
    image = Image.new("RGB", (128, 128), "navy")
    brighter = ImageEnhance.Brightness(image).enhance(1.05)
    assert engine.compute_hamming_distance(
        engine.compute_phash(image), engine.compute_phash(brighter)
    ) <= 10


def test_mixed_hash_algorithms_cannot_be_compared():
    engine = HashEngine()
    with pytest.raises(ValueError, match="different hash algorithms"):
        engine.compute_hamming_distance("phash:0000000000000000", "pdq:" + "0" * 64)


def test_malformed_signature_is_rejected():
    with pytest.raises(ValueError):
        HashEngine().compute_hamming_distance("not-a-hash", "not-a-hash")
