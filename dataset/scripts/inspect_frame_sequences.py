from pathlib import Path
import re
from collections import defaultdict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_ROOT / "dataset" / "annotated" / "images"


def main():
    groups = defaultdict(list)

    pattern = re.compile(
        r"^(source_[ab])_(train|valid|test)_frame_(\d+)_"
    )

    for image_path in IMAGE_DIR.iterdir():
        if not image_path.is_file():
            continue

        match = pattern.match(image_path.name)

        if not match:
            continue

        source = match.group(1)
        frame_number = int(match.group(3))

        groups[source].append((frame_number, image_path.name))

    print("=" * 70)
    print("SOURCE / FRAME SEQUENCE INSPECTION")
    print("=" * 70)

    for source, frames in sorted(groups.items()):
        frames.sort()

        print(f"\n{source}")
        print(f"Images identified: {len(frames)}")

        print("First 30 frame numbers:")
        print([frame for frame, _ in frames[:30]])

        print("Last 10 frame numbers:")
        print([frame for frame, _ in frames[-10:]])

        # Detect gaps
        gaps = []

        for i in range(1, len(frames)):
            previous = frames[i - 1][0]
            current = frames[i][0]

            if current - previous > 1:
                gaps.append((previous, current))

        print(f"Sequence gaps: {len(gaps)}")

        if gaps:
            print("First 20 gaps:")
            for previous, current in gaps[:20]:
                print(f"  {previous} -> {current}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()