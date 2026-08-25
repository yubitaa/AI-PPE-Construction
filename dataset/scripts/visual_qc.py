from pathlib import Path
import random
import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_ROOT / "dataset" / "annotated" / "images"
LABEL_DIR = PROJECT_ROOT / "dataset" / "annotated" / "labels"
OUTPUT = PROJECT_ROOT / "dataset" / "annotation_qc_sample.jpg"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

CLASS_NAMES = {
    0: "Person",
    1: "Helmet",
    2: "Vest",
}

SAMPLES = 24
COLS = 4
THUMB_W = 320
THUMB_H = 240
TEXT_H = 30


def load_annotations(label_path):
    annotations = []

    with label_path.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])
            x_center, y_center, width, height = map(float, parts[1:])

            annotations.append(
                (class_id, x_center, y_center, width, height)
            )

    return annotations


def main():
    images = [
        p for p in IMAGE_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    random.seed(42)
    samples = random.sample(images, min(SAMPLES, len(images)))

    rows = int(np.ceil(len(samples) / COLS))
    sheet = np.zeros(
        (rows * (THUMB_H + TEXT_H), COLS * THUMB_W, 3),
        dtype=np.uint8
    )

    for index, image_path in enumerate(samples):
        image = cv2.imread(str(image_path))

        if image is None:
            continue

        h, w = image.shape[:2]

        label_path = LABEL_DIR / f"{image_path.stem}.txt"

        if label_path.exists():
            annotations = load_annotations(label_path)

            for class_id, xc, yc, bw, bh in annotations:
                x1 = int((xc - bw / 2) * w)
                y1 = int((yc - bh / 2) * h)
                x2 = int((xc + bw / 2) * w)
                y2 = int((yc + bh / 2) * h)

                x1 = max(0, min(w - 1, x1))
                y1 = max(0, min(h - 1, y1))
                x2 = max(0, min(w - 1, x2))
                y2 = max(0, min(h - 1, y2))

                cv2.rectangle(image, (x1, y1), (x2, y2), (255, 255, 255), 2)

                name = CLASS_NAMES.get(class_id, f"UNKNOWN-{class_id}")
                cv2.putText(
                    image,
                    name,
                    (x1, max(20, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

        thumbnail = cv2.resize(
            image,
            (THUMB_W, THUMB_H),
            interpolation=cv2.INTER_AREA
        )

        row = index // COLS
        col = index % COLS

        y = row * (THUMB_H + TEXT_H)
        x = col * THUMB_W

        sheet[y:y + THUMB_H, x:x + THUMB_W] = thumbnail

        label = image_path.name[:42]

        cv2.putText(
            sheet,
            label,
            (x + 5, y + THUMB_H + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    cv2.imwrite(str(OUTPUT), sheet)

    print(f"Created QC sample: {OUTPUT}")
    print(f"Images included: {len(samples)}")


if __name__ == "__main__":
    main()