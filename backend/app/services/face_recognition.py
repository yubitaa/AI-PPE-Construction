import hashlib
import random

TARGET_DIMENSION = 512

def generate_embedding(image_bytes: bytes) -> dict:
    """
    Deterministic Mock Implementation using isolated random state.
    """
    if len(image_bytes) < 100:
        return {
            "success": False,
            "error": "NO_FACE_DETECTED"
        }

    image_hash = hashlib.md5(image_bytes).hexdigest()
    
    # Creates an isolated random generator so we don't mess with Python's global state
    rng = random.Random(image_hash)
    
    mock_vector = [rng.uniform(-1.0, 1.0) for _ in range(TARGET_DIMENSION)]

    return {
        "success": True,
        "embedding": mock_vector
    }