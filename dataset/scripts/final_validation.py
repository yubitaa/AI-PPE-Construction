from pathlib import Path

ROOT = Path("dataset")
SPLITS = ["train", "val", "test"]
VALID_CLASSES = {0, 1, 2}

errors = []

for split in SPLITS:
    image_dir = ROOT / split / "images"
    label_dir = ROOT / split / "labels"

    for image_path in image_dir.iterdir():
        if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            continue

        label_path = label_dir / f"{image_path.stem}.txt"

        if not label_path.exists():
            errors.append(f"{split}: missing label for {image_path.name}")
            continue

        for line_no, line in enumerate(label_path.read_text().splitlines(), start=1):
            parts = line.split()

            if len(parts) != 5:
                errors.append(
                    f"{split}/{label_path.name}: line {line_no}: "
                    f"expected 5 values, got {len(parts)}"
                )
                continue

            try:
                class_id = int(parts[0])
                coords = [float(x) for x in parts[1:]]
            except ValueError:
                errors.append(
                    f"{split}/{label_path.name}: line {line_no}: non-numeric value"
                )
                continue

            if class_id not in VALID_CLASSES:
                errors.append(
                    f"{split}/{label_path.name}: line {line_no}: "
                    f"invalid class {class_id}"
                )

            if not all(0.0 <= x <= 1.0 for x in coords):
                errors.append(
                    f"{split}/{label_path.name}: line {line_no}: "
                    f"coordinate outside [0,1]"
                )

            if coords[2] <= 0 or coords[3] <= 0:
                errors.append(
                    f"{split}/{label_path.name}: line {line_no}: "
                    f"non-positive width/height"
                )

print("=" * 60)
print("FINAL PHASE 5 YOLO VALIDATION")
print("=" * 60)

if errors:
    print(f"ERRORS FOUND: {len(errors)}")
    for error in errors[:50]:
        print(error)
else:
    print("All final labels are valid YOLO annotations.")
    print("All class IDs are 0, 1, or 2.")
    print("All coordinates are normalized.")
    print("All bounding-box widths/heights are positive.")

print("=" * 60)