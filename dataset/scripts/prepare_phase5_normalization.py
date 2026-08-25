from pathlib import Path
import shutil
import cv2


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCES = {
    "source_a": {
        "root": PROJECT_ROOT / "dataset" / "raw" / "source_a_ppe_person",
        "splits": ["train", "valid", "test"],
        # Source A:
        # 0 = Gloves
        # 1 = Helmet
        # 2 = Person
        # 3 = Vest
        "class_map": {
            1: 1,  # Helmet -> Helmet
            2: 0,  # Person -> Person
            3: 2,  # Vest -> Vest
        },
        "ignored_classes": {0},  # Gloves
    },
    "source_b": {
        "root": PROJECT_ROOT / "dataset" / "raw" / "source_b_construction_safety",
        "splits": ["train", "valid", "test"],
        # Source B:
        # 0 = helmet
        # 1 = no-helmet
        # 2 = no-vest
        # 3 = person
        # 4 = vest
        "class_map": {
            0: 1,  # helmet -> Helmet
            3: 0,  # person -> Person
            4: 2,  # vest -> Vest
        },
        "ignored_classes": {1, 2},  # no-helmet, no-vest
    },
}


OUTPUT_IMAGES = PROJECT_ROOT / "dataset" / "annotated" / "images"
OUTPUT_LABELS = PROJECT_ROOT / "dataset" / "annotated" / "labels"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def validate_yolo_line(parts, label_path):
    if len(parts) != 5:
        raise ValueError(
            f"Invalid YOLO annotation in {label_path}: "
            f"expected 5 values, got {len(parts)}"
        )

    class_id = int(parts[0])
    coords = [float(value) for value in parts[1:]]

    for value in coords:
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"Invalid normalized coordinate in {label_path}: {value}"
            )

    return class_id, coords


def process_source(source_name, config):
    total_images = 0
    processed_images = 0
    skipped_images = 0
    invalid_images = 0

    total_source_annotations = 0
    kept_annotations = 0
    removed_annotations = 0

    class_counts = {0: 0, 1: 0, 2: 0}

    root = config["root"]

    for split in config["splits"]:
        images_dir = root / split / "images"
        labels_dir = root / split / "labels"

        if not images_dir.exists() or not labels_dir.exists():
            print(f"[WARNING] Missing images/labels directory for {source_name}/{split}")
            continue

        for image_path in sorted(images_dir.iterdir()):
            if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            total_images += 1

            label_path = labels_dir / f"{image_path.stem}.txt"

            if not label_path.exists():
                print(f"[SKIP] Missing label: {label_path}")
                skipped_images += 1
                continue

            image = cv2.imread(str(image_path))
            if image is None:
                print(f"[SKIP] Corrupted/unreadable image: {image_path}")
                invalid_images += 1
                continue

            kept_lines = []

            try:
                with label_path.open("r", encoding="utf-8") as file:
                    for raw_line in file:
                        line = raw_line.strip()

                        if not line:
                            continue

                        parts = line.split()
                        class_id, coords = validate_yolo_line(parts, label_path)

                        total_source_annotations += 1

                        if class_id in config["class_map"]:
                            new_class_id = config["class_map"][class_id]
                            kept_lines.append(
                                f"{new_class_id} "
                                + " ".join(f"{value:.6f}" for value in coords)
                            )

                            kept_annotations += 1
                            class_counts[new_class_id] += 1

                        elif class_id in config["ignored_classes"]:
                            removed_annotations += 1

                        else:
                            raise ValueError(
                                f"Unexpected class ID {class_id} in {label_path}"
                            )

            except (ValueError, OSError) as exc:
                print(f"[SKIP] Invalid label {label_path}: {exc}")
                invalid_images += 1
                continue

            # If an image contains no Person/Helmet/Vest after filtering,
            # it is not useful for our final 3-class dataset.
            if not kept_lines:
                skipped_images += 1
                continue

            output_stem = f"{source_name}_{split}_{image_path.stem}"

            output_image = OUTPUT_IMAGES / f"{output_stem}{image_path.suffix.lower()}"
            output_label = OUTPUT_LABELS / f"{output_stem}.txt"

            shutil.copy2(image_path, output_image)

            with output_label.open("w", encoding="utf-8") as file:
                file.write("\n".join(kept_lines) + "\n")

            processed_images += 1

    return {
        "total_images": total_images,
        "processed_images": processed_images,
        "skipped_images": skipped_images,
        "invalid_images": invalid_images,
        "total_source_annotations": total_source_annotations,
        "kept_annotations": kept_annotations,
        "removed_annotations": removed_annotations,
        "class_counts": class_counts,
    }


def main():
    OUTPUT_IMAGES.mkdir(parents=True, exist_ok=True)
    OUTPUT_LABELS.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PHASE 5 DATASET NORMALIZATION")
    print("Final classes: 0=Person, 1=Helmet, 2=Vest")
    print("=" * 60)

    results = {}

    for source_name, config in SOURCES.items():
        print(f"\nProcessing {source_name}...")
        results[source_name] = process_source(source_name, config)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    for source_name, result in results.items():
        print(f"\n{source_name}")
        print(f"  Input images:        {result['total_images']}")
        print(f"  Kept images:         {result['processed_images']}")
        print(f"  Skipped images:      {result['skipped_images']}")
        print(f"  Invalid images:      {result['invalid_images']}")
        print(f"  Source annotations:  {result['total_source_annotations']}")
        print(f"  Kept annotations:    {result['kept_annotations']}")
        print(f"  Removed annotations: {result['removed_annotations']}")
        print(f"  Person:              {result['class_counts'][0]}")
        print(f"  Helmet:              {result['class_counts'][1]}")
        print(f"  Vest:                {result['class_counts'][2]}")

    final_images = len(list(OUTPUT_IMAGES.iterdir()))
    final_labels = len(list(OUTPUT_LABELS.glob("*.txt")))

    print("\n" + "=" * 60)
    print("FINAL NORMALIZED DATASET")
    print("=" * 60)
    print(f"Images: {final_images}")
    print(f"Labels: {final_labels}")
    print(f"Output: {OUTPUT_IMAGES}")
    print(f"        {OUTPUT_LABELS}")
    print("=" * 60)


if __name__ == "__main__":
    main()