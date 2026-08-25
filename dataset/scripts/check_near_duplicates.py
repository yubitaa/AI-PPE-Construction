from pathlib import Path
from collections import defaultdict
import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_ROOT / "dataset" / "annotated" / "images"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Images with a Hamming distance <= this value will be considered
# near-duplicate candidates.
HAMMING_THRESHOLD = 8


def average_hash(image_path: Path, size: int = 16):
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        return None

    image = cv2.resize(image, (size, size), interpolation=cv2.INTER_AREA)

    mean = image.mean()

    bits = image > mean

    return bits.flatten()


def hamming_distance(hash_a, hash_b):
    return int(np.count_nonzero(hash_a != hash_b))


def main():
    images = sorted(
        p for p in IMAGE_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
    )

    print(f"Images found: {len(images)}")
    print("Computing perceptual hashes...")

    hashes = {}
    unreadable = []

    for image_path in images:
        image_hash = average_hash(image_path)

        if image_hash is None:
            unreadable.append(image_path)
        else:
            hashes[image_path] = image_hash

    print(f"Readable images: {len(hashes)}")
    print(f"Unreadable images: {len(unreadable)}")

    # Compare each image only with images after it
    # so we don't report the same pair twice.
    candidates = []

    hash_items = list(hashes.items())

    for i in range(len(hash_items)):
        path_a, hash_a = hash_items[i]

        for j in range(i + 1, len(hash_items)):
            path_b, hash_b = hash_items[j]

            distance = hamming_distance(hash_a, hash_b)

            if distance <= HAMMING_THRESHOLD:
                candidates.append((distance, path_a, path_b))

    candidates.sort(key=lambda x: x[0])

    print()
    print("=" * 70)
    print("NEAR-DUPLICATE CANDIDATES")
    print("=" * 70)
    print(f"Hamming threshold: {HAMMING_THRESHOLD}")
    print(f"Candidate pairs:   {len(candidates)}")

    if not candidates:
        print("\nNo near-duplicate candidates found.")
    else:
        print("\nClosest candidate pairs:")

        # Print at most 100 candidates for manageable output.
        for distance, path_a, path_b in candidates[:100]:
            print(f"\nDistance: {distance}")
            print(f"  {path_a.name}")
            print(f"  {path_b.name}")

    if unreadable:
        print("\nUnreadable images:")
        for path in unreadable:
            print(f"  {path.name}")

    print("=" * 70)


if __name__ == "__main__":
    main()