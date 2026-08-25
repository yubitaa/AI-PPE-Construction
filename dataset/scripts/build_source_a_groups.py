from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_ROOT / "dataset" / "annotated" / "images"

pattern = re.compile(r"^source_a_(train|valid|test)_frame_(\d+)_")


def main():
    frames = []

    for image_path in IMAGE_DIR.iterdir():
        match = pattern.match(image_path.name)

        if match:
            frame_number = int(match.group(2))
            original_split = match.group(1)
            frames.append((frame_number, original_split, image_path.name))

    frames.sort()

    groups = []
    current = [frames[0]]

    for item in frames[1:]:
        previous_frame = current[-1][0]

        if item[0] == previous_frame + 1:
            current.append(item)
        else:
            groups.append(current)
            current = [item]

    groups.append(current)

    print("=" * 70)
    print("SOURCE A CONTIGUOUS FRAME GROUPS")
    print("=" * 70)
    print(f"Total selected frames: {len(frames)}")
    print(f"Contiguous groups:     {len(groups)}")

    for index, group in enumerate(groups, start=1):
        start = group[0][0]
        end = group[-1][0]

        original_splits = {}

        for _, split, _ in group:
            original_splits[split] = original_splits.get(split, 0) + 1

        print(
            f"Group {index:03d}: "
            f"frames {start:04d}-{end:04d} | "
            f"count={len(group)} | "
            f"Roboflow splits={original_splits}"
        )


if __name__ == "__main__":
    main()