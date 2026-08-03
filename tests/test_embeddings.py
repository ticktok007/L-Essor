# tests/test_embeddings.py
import pytest
from matching.embeddings import encode, encode_batch, DIMENSIONS

def test_encode_valid_text():
    vector = encode("Developing an AI startup for campus innovation.")
    assert len(vector) == DIMENSIONS
    assert isinstance(vector, list)
    assert isinstance(vector[0], float)

@pytest.mark.parametrize("invalid_input", [None, "", "   ", "\n\t"])
def test_encode_invalid_inputs(invalid_input):
    vector = encode(invalid_input)
    assert vector == [0.0] * DIMENSIONS

def test_encode_truncation_warning(caplog):
    oversized_text = "word " * 1000
    vector = encode(oversized_text)
    assert len(vector) == DIMENSIONS
    assert "Truncating" in caplog.text

def test_encode_batch_mixed_inputs():
    inputs = [
        "First valid pitch",
        "",
        "Second valid mandate",
        None
    ]
    vectors = encode_batch(inputs)
    assert len(vectors) == 4
    assert len(vectors[0]) == DIMENSIONS
    assert vectors[1] == [0.0] * DIMENSIONS
    assert len(vectors[2]) == DIMENSIONS
    assert vectors[3] == [0.0] * DIMENSIONS

def test_model_singleton_identity():
    from matching.embeddings import get_model
    model1 = get_model()
    model2 = get_model()
    assert model1 is model2