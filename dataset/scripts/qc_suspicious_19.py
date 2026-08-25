from pathlib import Path
import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = PROJECT_ROOT / "dataset" / "annotated" / "images"
LABEL_DIR = PROJECT_ROOT / "dataset" / "annotated" / "labels"
OUTPUT = PROJECT_ROOT / "dataset" / "qc_suspicious_19.jpg"

CLASS_NAMES = {
    0: "Person",
    1: "Helmet",
    2: "Vest",
}

TARGET_PREFIXES = [
    "source_b_test_ppe_0781",
    "source_b_test_ppe_0901",
    "source_b_train_ppe_0169",
    "source_b_train_ppe_0247",
    "source_b_train_ppe_0358",
    "source_b_train_ppe_0360",
    "source_b_train_ppe_0424",
    "source_b_train_ppe_0507",
    "source_b_train_ppe_0653",
    "source_b_train_ppe_0712",
    "source_b_train_ppe_0961",
    "source_b_train_ppe_1064",
    "source_b_train_ppe_1235",
    "source_b_valid_ppe_0062",
    "source_b_valid_ppe_0132",
    "source_b_valid_ppe_0439",
    "source_b_valid_ppe_0532",
]


def load_labels(label_path):
    annotations = []

    with label_path.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])
            xc, yc, w, h = map(float, parts[1:])

            annotations.append((class_id, xc, yc, w, h))

    return annotations


def main():
    image_files = []

    for image_path in IMAGE_DIR.iterdir():
        if not image_path.is_file():
            continue

        if any(image_path.name.startswith(prefix) for prefix in TARGET_PREFIXES):
            image_files.append(image_path)

    image_files.sort()

    print(f"Images found: {len(image_files)}")

    thumb_w = 420
    thumb_h = 300
    text_h = 35
    cols = 3
    rows = int(np.ceil(len(image_files) / cols))

    sheet = np.zeros(
        (rows * (thumb_h + text_h), cols * thumb_w, 3),
        dtype=np.uint8,
    )

    for i, image_path in enumerate(image_files):
        image = cv2.imread(str(image_path))

        if image is None:
            continue

        h, w = image.shape[:2]

        label_path = LABEL_DIR / f"{image_path.stem}.txt"

        if label_path.exists():
            for class_id, xc, yc, bw, bh in load_labels(label_path):
                x1 = int((xc - bw / 2) * w)
                y1 = int((yc - bh / 2) * h)
                x2 = int((xc + bw / 2) * w)
                y2 = int((yc + bh / 2) * h)

                x1 = max(0, min(w - 1, x1))
                y1 = max(0, min(h - 1, y1))
                x2 = max(0, min(w - 1, x2))
                y2 = max(0, min(h - 1, y2))

                cv2.rectangle(
                    image,
                    (x1, y1),
                    (x2, y2),
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    image,
                    CLASS_NAMES.get(class_id, str(class_id)),
                    (x1, max(20, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

        thumbnail = cv2.resize(
            image,
            (thumb_w, thumb_h),
            interpolation=cv2.INTER_AREA,
        )

        row = i // cols
        col = i % cols

        y = row * (thumb_h + text_h)
        x = col * thumb_w

        sheet[y:y + thumb_h, x:x + thumb_w] = thumbnail

        cv2.putText(
            sheet,
            image_path.stem[:55],
            (x + 5, y + thumb_h + 23),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    cv2.imwrite(str(OUTPUT), sheet)

    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()