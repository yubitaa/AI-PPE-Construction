from pathlib import Path
from collections import defaultdict
import random
import shutil
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_IMAGES = PROJECT_ROOT / "dataset" / "annotated" / "images"
SOURCE_LABELS = PROJECT_ROOT / "dataset" / "annotated" / "labels"

OUTPUT_ROOT = PROJECT_ROOT / "dataset"

RANDOM_SEED = 42

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

source_a_pattern = re.compile(r"^source_a_[^_]+_frame_(\d+)_")


def get_images():
    return sorted(
        p for p in SOURCE_IMAGES.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
    )


def source_a_groups(images):
    grouped = defaultdict(list)

    for image in images:
        match = source_a_pattern.match(image.name)

        if match:
            frame_number = int(match.group(1))

            # Group contiguous frame sequences.
            grouped["source_a"].append((frame_number, image))

    frames = sorted(grouped["source_a"], key=lambda x: x[0])

    groups = []
    current = [frames[0]]

    for item in frames[1:]:
        if item[0] == current[-1][0] + 1:
            current.append(item)
        else:
            groups.append(current)
            current = [item]

    if current:
        groups.append(current)

    return groups


def split_grouped_items(groups, target_train, target_val, total):
    groups = list(groups)

    # Large groups first so allocation reaches the targets efficiently.
    groups.sort(key=len, reverse=True)

    train = []
    val = []
    test = []

    train_count = 0
    val_count = 0
    test_count = 0

    targets = {
        "train": target_train,
        "val": target_val,
        "test": total - target_train - target_val,
    }

    for group in groups:
        remaining = {
            "train": max(targets["train"] - train_count, 0),
            "val": max(targets["val"] - val_count, 0),
            "test": max(targets["test"] - test_count, 0),
        }

        destination = max(remaining, key=remaining.get)

        if destination == "train":
            train.extend(image for _, image in group)
            train_count += len(group)
        elif destination == "val":
            val.extend(image for _, image in group)
            val_count += len(group)
        else:
            test.extend(image for _, image in group)
            test_count += len(group)

    return train, val, test


def copy_pair(image, split):
    label = SOURCE_LABELS / f"{image.stem}.txt"

    if not label.exists():
        raise FileNotFoundError(f"Missing label for {image.name}")

    image_dir = OUTPUT_ROOT / split / "images"
    label_dir = OUTPUT_ROOT / split / "labels"

    image_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(image, image_dir / image.name)
    shutil.copy2(label, label_dir / label.name)


def main():
    random.seed(RANDOM_SEED)

    images = get_images()

    source_a = []
    source_b = []

    for image in images:
        if image.name.startswith("source_a_"):
            source_a.append(image)
        elif image.name.startswith("source_b_"):
            source_b.append(image)

    total = len(images)

    target_train = round(total * 0.80)
    target_val = round(total * 0.10)

    print("=" * 60)
    print("PHASE 5 LEAKAGE-SAFE DATASET SPLIT")
    print("=" * 60)
    print(f"Total images: {total}")
    print(f"Source A: {len(source_a)}")
    print(f"Source B: {len(source_b)}")

    # Source A: preserve contiguous frame groups.
    a_groups = source_a_groups(source_a)

    # Approximate target allocation proportional to Source A size.
    a_train_target = round(len(source_a) * 0.80)
    a_val_target = round(len(source_a) * 0.10)

    a_train, a_val, a_test = split_grouped_items(
        a_groups,
        a_train_target,
        a_val_target,
        len(source_a),
    )

    # Source B: independent image split.
    random.shuffle(source_b)

    b_train_count = round(len(source_b) * 0.80)
    b_val_count = round(len(source_b) * 0.10)

    b_train = source_b[:b_train_count]
    b_val = source_b[b_train_count:b_train_count + b_val_count]
    b_test = source_b[b_train_count + b_val_count:]

    splits = {
        "train": a_train + b_train,
        "val": a_val + b_val,
        "test": a_test + b_test,
    }

    for split in splits:
        random.shuffle(splits[split])

    for split, split_images in splits.items():
        for image in split_images:
            copy_pair(image, split)

    print("\nFINAL SPLIT")
    for split, split_images in splits.items():
        print(f"{split}: {len(split_images)} images")

    print("\nSource A:")
    print(f"  Train: {len(a_train)}")
    print(f"  Val:   {len(a_val)}")
    print(f"  Test:  {len(a_test)}")

    print("\nSource B:")
    print(f"  Train: {len(b_train)}")
    print(f"  Val:   {len(b_val)}")
    print(f"  Test:  {len(b_test)}")

    print("=" * 60)


if __name__ == "__main__":
    main()