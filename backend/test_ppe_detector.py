import cv2

from app.vision.ppe_detector import YOLOPPEDetector


def main():
    detector = YOLOPPEDetector()

    image = cv2.imread("image.png")

    if image is None:
        raise FileNotFoundError(
            "img.png was not found."
        )

    detections = detector.detect(image)

    print(f"Found {len(detections)} detections")

    for detection in detections:
        print(
            f"class={detection.class_name}, "
            f"confidence={detection.confidence:.3f}, "
            f"bbox={detection.bbox}"
        )


if __name__ == "__main__":
    main()