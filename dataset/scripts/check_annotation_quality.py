from pathlib import Path
from collections import defaultdict


PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = PROJECT_ROOT / "dataset" / "annotated" / "images"
LABEL_DIR = PROJECT_ROOT / "dataset" / "annotated" / "labels"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

MIN_BOX_AREA = 0.0005


def read_labels(label_path):
    annotations = []

    with label_path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            parts = line.strip().split()

            if not parts:
                continue

            if len(parts) != 5:
                annotations.append(
                    {
                        "type": "invalid_format",
                        "line": line_number,
                        "raw": line.strip(),
                    }
                )
                continue

            try:
                class_id = int(parts[0])
                xc, yc, w, h = map(float, parts[1:])
            except ValueError:
                annotations.append(
                    {
                        "type": "invalid_values",
                        "line": line_number,
                        "raw": line.strip(),
                    }
                )
                continue

            annotations.append(
                {
                    "type": "annotation",
                    "class_id": class_id,
                    "xc": xc,
                    "yc": yc,
                    "w": w,
                    "h": h,
                }
            )

    return annotations


def main():
    flagged = defaultdict(list)

    images = [
        p for p in IMAGE_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    total = len(images)

    for image_path in images:
        label_path = LABEL_DIR / f"{image_path.stem}.txt"

        if not label_path.exists():
            flagged["missing_label"].append(image_path.name)
            continue

        annotations = read_labels(label_path)

        if not annotations:
            flagged["empty_label"].append(image_path.name)
            continue

        person_count = 0
        helmet_count = 0
        vest_count = 0

        for annotation in annotations:

            if annotation["type"] != "annotation":
                flagged[annotation["type"]].append(image_path.name)
                continue

            class_id = annotation["class_id"]
            xc = annotation["xc"]
            yc = annotation["yc"]
            w = annotation["w"]
            h = annotation["h"]

            if class_id not in {0, 1, 2}:
                flagged["unexpected_class"].append(
                    f"{image_path.name} -> class {class_id}"
                )

            if not (0 <= xc <= 1 and 0 <= yc <= 1):
                flagged["center_out_of_range"].append(image_path.name)

            if not (0 < w <= 1 and 0 < h <= 1):
                flagged["size_out_of_range"].append(image_path.name)

            x1 = xc - w / 2
            y1 = yc - h / 2
            x2 = xc + w / 2
            y2 = yc + h / 2

            if x1 < 0 or y1 < 0 or x2 > 1 or y2 > 1:
                flagged["box_touches_or_exceeds_boundary"].append(
                    image_path.name
                )

            area = w * h

            if area < MIN_BOX_AREA:
                flagged["very_small_box"].append(image_path.name)

            if class_id == 0:
                person_count += 1
            elif class_id == 1:
                helmet_count += 1
            elif class_id == 2:
                vest_count += 1

        if helmet_count > 0 and person_count == 0:
            flagged["helmet_without_person"].append(image_path.name)

        if vest_count > 0 and person_count == 0:
            flagged["vest_without_person"].append(image_path.name)

        if person_count >= 2 and helmet_count == 0 and vest_count == 0:
            flagged["multiple_people_without_ppe_boxes"].append(
                image_path.name
            )

    print("=" * 70)
    print("PHASE 5 AUTOMATED ANNOTATION QC")
    print("=" * 70)
    print(f"Images checked: {total}")

    total_flagged_images = set()

    for category, filenames in flagged.items():
        unique_files = sorted(set(filenames))

        print(f"\n{category}: {len(unique_files)}")

        for filename in unique_files[:50]:
            print(f"  {filename}")

        if len(unique_files) > 50:
            print(f"  ... and {len(unique_files) - 50} more")

        total_flagged_images.update(unique_files)

    print("\n" + "=" * 70)
    print(f"Unique flagged items: {len(total_flagged_images)}")
    print("=" * 70)


if __name__ == "__main__":
    main()