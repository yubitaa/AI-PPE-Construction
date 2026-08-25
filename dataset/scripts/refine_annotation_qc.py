from pathlib import Path
from collections import Counter, defaultdict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LABEL_DIR = PROJECT_ROOT / "dataset" / "annotated" / "labels"

CLASS_NAMES = {
    0: "Person",
    1: "Helmet",
    2: "Vest",
}

MIN_BOX_AREA = 0.0005
BOUNDARY_EPSILON = 0.001


def main():
    stats = {
        "boundary": Counter(),
        "small": Counter(),
        "boundary_files": defaultdict(set),
        "small_files": defaultdict(set),
        "helmet_without_person": set(),
        "vest_without_person": set(),
        "multiple_people_without_ppe": set(),
    }

    label_files = list(LABEL_DIR.glob("*.txt"))

    for label_path in label_files:
        annotations = []

        with label_path.open("r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()

                if len(parts) != 5:
                    continue

                class_id = int(parts[0])
                xc, yc, w, h = map(float, parts[1:])

                annotations.append((class_id, xc, yc, w, h))

        person_count = sum(a[0] == 0 for a in annotations)
        helmet_count = sum(a[0] == 1 for a in annotations)
        vest_count = sum(a[0] == 2 for a in annotations)

        if helmet_count > 0 and person_count == 0:
            stats["helmet_without_person"].add(label_path.name)

        if vest_count > 0 and person_count == 0:
            stats["vest_without_person"].add(label_path.name)

        if person_count >= 2 and helmet_count == 0 and vest_count == 0:
            stats["multiple_people_without_ppe"].add(label_path.name)

        for class_id, xc, yc, w, h in annotations:
            class_name = CLASS_NAMES[class_id]

            x1 = xc - w / 2
            y1 = yc - h / 2
            x2 = xc + w / 2
            y2 = yc + h / 2

            if (
                x1 <= BOUNDARY_EPSILON
                or y1 <= BOUNDARY_EPSILON
                or x2 >= 1 - BOUNDARY_EPSILON
                or y2 >= 1 - BOUNDARY_EPSILON
            ):
                stats["boundary"][class_name] += 1
                stats["boundary_files"][class_name].add(label_path.name)

            if w * h < MIN_BOX_AREA:
                stats["small"][class_name] += 1
                stats["small_files"][class_name].add(label_path.name)

    print("=" * 70)
    print("REFINED ANNOTATION QC")
    print("=" * 70)

    print("\nBOUNDARY CASES BY CLASS")
    for class_name in CLASS_NAMES.values():
        print(
            f"  {class_name}: "
            f"{stats['boundary'][class_name]} annotations in "
            f"{len(stats['boundary_files'][class_name])} images"
        )

    print("\nVERY SMALL BOXES BY CLASS")
    for class_name in CLASS_NAMES.values():
        print(
            f"  {class_name}: "
            f"{stats['small'][class_name]} annotations in "
            f"{len(stats['small_files'][class_name])} images"
        )

    print("\nSUSPICIOUS OBJECT/WORKER RELATIONSHIPS")
    print(
        f"  Helmet without Person: "
        f"{len(stats['helmet_without_person'])}"
    )
    print(
        f"  Vest without Person: "
        f"{len(stats['vest_without_person'])}"
    )
    print(
        f"  Multiple People without Helmet/Vest: "
        f"{len(stats['multiple_people_without_ppe'])}"
    )

    print("\nEXACT FILES FOR HELMET WITHOUT PERSON")
    for name in sorted(stats["helmet_without_person"]):
        print(f"  {name}")

    print("\nEXACT FILES FOR VEST WITHOUT PERSON")
    for name in sorted(stats["vest_without_person"]):
        print(f"  {name}")

    print("\nEXACT FILES FOR MULTIPLE PEOPLE WITHOUT PPE")
    for name in sorted(stats["multiple_people_without_ppe"]):
        print(f"  {name}")

    print("=" * 70)


if __name__ == "__main__":
    main()