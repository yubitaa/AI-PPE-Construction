from pathlib import Path
from collections import defaultdict
from PIL import Image
import hashlib


PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_ROOT / "dataset" / "annotated" / "images"


def file_hash(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def main():
    groups = defaultdict(list)

    images = [
        p for p in IMAGE_DIR.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    ]

    print(f"Images found: {len(images)}")

    corrupted = []

    for image_path in images:
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception:
            corrupted.append(image_path)
            continue

        groups[file_hash(image_path)].append(image_path)

    duplicate_groups = {
        digest: paths
        for digest, paths in groups.items()
        if len(paths) > 1
    }

    duplicate_count = sum(len(paths) - 1 for paths in duplicate_groups.values())

    print()
    print("=" * 60)
    print("EXACT DUPLICATE CHECK")
    print("=" * 60)
    print(f"Valid images:       {len(images) - len(corrupted)}")
    print(f"Corrupted images:   {len(corrupted)}")
    print(f"Duplicate groups:   {len(duplicate_groups)}")
    print(f"Duplicate copies:   {duplicate_count}")

    if corrupted:
        print("\nCorrupted/unreadable:")
        for path in corrupted:
            print(f"  {path.name}")

    if duplicate_groups:
        print("\nDuplicate groups:")
        for paths in duplicate_groups.values():
            print("  GROUP:")
            for path in paths:
                print(f"    {path.name}")

    print("=" * 60)


if __name__ == "__main__":
    main()