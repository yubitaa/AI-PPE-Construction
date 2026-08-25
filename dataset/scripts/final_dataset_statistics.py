from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_ROOT = PROJECT_ROOT / "dataset"

CLASS_NAMES = {
    0: "Person",
    1: "Helmet",
    2: "Vest",
}


def analyze_split(split):
    label_dir = DATASET_ROOT / split / "labels"

    image_count = 0
    class_instances = Counter()
    images_with_class = Counter()

    both_helmet_vest = 0
    missing_helmet = 0
    missing_vest = 0

    for label_path in label_dir.glob("*.txt"):
        image_count += 1

        classes = []

        with label_path.open("r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()

                if len(parts) != 5:
                    continue

                class_id = int(parts[0])

                if class_id in CLASS_NAMES:
                    class_instances[class_id] += 1
                    classes.append(class_id)

        unique_classes = set(classes)

        for class_id in unique_classes:
            images_with_class[class_id] += 1

        if 1 in unique_classes and 2 in unique_classes:
            both_helmet_vest += 1

        if 0 in unique_classes and 1 not in unique_classes:
            missing_helmet += 1

        if 0 in unique_classes and 2 not in unique_classes:
            missing_vest += 1

    return {
        "images": image_count,
        "instances": class_instances,
        "images_with_class": images_with_class,
        "both": both_helmet_vest,
        "missing_helmet": missing_helmet,
        "missing_vest": missing_vest,
    }


def main():
    print("=" * 70)
    print("PHASE 5 FINAL DATASET STATISTICS")
    print("=" * 70)

    totals = {
        "images": 0,
        "instances": Counter(),
        "images_with_class": Counter(),
        "both": 0,
        "missing_helmet": 0,
        "missing_vest": 0,
    }

    for split in ["train", "val", "test"]:
        result = analyze_split(split)

        print(f"\n{split.upper()}")
        print("-" * 40)

        print(f"Images: {result['images']}")
        print(f"Person instances: {result['instances'][0]}")
        print(f"Helmet instances: {result['instances'][1]}")
        print(f"Vest instances: {result['instances'][2]}")

        print(f"Images with Helmet: {result['images_with_class'][1]}")
        print(f"Images with Vest: {result['images_with_class'][2]}")
        print(f"Images with both: {result['both']}")
        print(f"Images missing Helmet: {result['missing_helmet']}")
        print(f"Images missing Vest: {result['missing_vest']}")

        totals["images"] += result["images"]
        totals["instances"].update(result["instances"])
        totals["images_with_class"].update(result["images_with_class"])
        totals["both"] += result["both"]
        totals["missing_helmet"] += result["missing_helmet"]
        totals["missing_vest"] += result["missing_vest"]

    print("\n" + "=" * 70)
    print("TOTAL DATASET")
    print("=" * 70)

    print(f"Images: {totals['images']}")
    print(f"Person instances: {totals['instances'][0]}")
    print(f"Helmet instances: {totals['instances'][1]}")
    print(f"Vest instances: {totals['instances'][2]}")
    print(f"Images with Helmet: {totals['images_with_class'][1]}")
    print(f"Images with Vest: {totals['images_with_class'][2]}")
    print(f"Images with both: {totals['both']}")
    print(f"Images missing Helmet: {totals['missing_helmet']}")
    print(f"Images missing Vest: {totals['missing_vest']}")
    print("=" * 70)


if __name__ == "__main__":
    main()