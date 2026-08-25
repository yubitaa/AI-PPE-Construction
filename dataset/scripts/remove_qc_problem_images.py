from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = PROJECT_ROOT / "dataset" / "annotated" / "images"
LABEL_DIR = PROJECT_ROOT / "dataset" / "annotated" / "labels"

REMOVED_DIR = PROJECT_ROOT / "dataset" / "qc_removed"
REMOVED_IMAGES = REMOVED_DIR / "images"
REMOVED_LABELS = REMOVED_DIR / "labels"

REMOVED_IMAGES.mkdir(parents=True, exist_ok=True)
REMOVED_LABELS.mkdir(parents=True, exist_ok=True)

# Strong annotation-problem groups identified by our QC.
PREFIXES = [
    # Helmet without Person
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

    # Multiple people without Helmet/Vest annotations
    "source_b_test_ppe_0014",
    "source_b_test_ppe_0133",
    "source_b_test_ppe_0872",
    "source_b_test_ppe_0915",
    "source_b_train_ppe_0085",
    "source_b_train_ppe_0111",
    "source_b_train_ppe_0490",
    "source_b_train_ppe_0671",
    "source_b_train_ppe_0693",
    "source_b_train_ppe_0696",
    "source_b_train_ppe_0760",
    "source_b_train_ppe_0809",
    "source_b_train_ppe_0819",
    "source_b_train_ppe_0946",
    "source_b_train_ppe_0967",
    "source_b_train_ppe_0968",
    "source_b_train_ppe_0970",
    "source_b_train_ppe_0990",
    "source_b_train_ppe_1008",
    "source_b_train_ppe_1019",
    "source_b_train_ppe_1023",
    "source_b_train_ppe_1035",
    "source_b_train_ppe_1094",
    "source_b_train_ppe_1113",
    "source_b_train_ppe_1218",
    "source_b_train_ppe_1232",
    "source_b_train_ppe_1247",
    "source_b_train_ppe_1248",
    "source_b_train_ppe_1259",
    "source_b_train_ppe_1271",
    "source_b_train_ppe_1284",
    "source_b_train_ppe_1300",
]

removed = 0

for image_path in list(IMAGE_DIR.iterdir()):
    if not image_path.is_file():
        continue

    if not any(image_path.name.startswith(prefix) for prefix in PREFIXES):
        continue

    label_path = LABEL_DIR / f"{image_path.stem}.txt"

    shutil.move(str(image_path), REMOVED_IMAGES / image_path.name)

    if label_path.exists():
        shutil.move(str(label_path), REMOVED_LABELS / label_path.name)

    removed += 1

print("=" * 60)
print("QC REMOVAL")
print("=" * 60)
print(f"Images removed: {removed}")
print(f"Remaining images: {len(list(IMAGE_DIR.iterdir()))}")
print(f"Removed files stored in: {REMOVED_DIR}")
print("=" * 60)