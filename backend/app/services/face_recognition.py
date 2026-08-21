import cv2
import numpy as np
from insightface.app import FaceAnalysis


class FaceRecognitionService:
    def __init__(self, model_name: str = "buffalo_l", ctx_id: int = -1):
        self.app = FaceAnalysis(name=model_name)
        self.app.prepare(
            ctx_id=ctx_id,
            det_size=(640, 640),
        )

    def generate_embedding(self, image: np.ndarray) -> dict:
        """
        Process one OpenCV image.

        Pipeline:
        BGR -> RGB -> InsightFace -> face detection -> embedding
        """

        if image is None or image.size == 0:
            return {
                "status": "INVALID_IMAGE_DATA",
                "embedding": None,
            }

        # OpenCV images are BGR.
        # Convert BGR to RGB before sending the image to InsightFace.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces and generate face information.
        faces = self.app.get(rgb_image)

        # No face detected.
        if len(faces) == 0:
            return {
                "status": "NO_FACE_DETECTED",
                "embedding": None,
            }

        # More than one face detected.
        if len(faces) > 1:
            return {
                "status": "MULTIPLE_FACES_DETECTED",
                "embedding": None,
            }

        # Exactly one face detected.
        embedding = faces[0].embedding.tolist()

        return {
            "status": "SUCCESS",
            "embedding": embedding,
        }

    def generate_embeddings(self, images: list[np.ndarray]) -> dict:
        """
        Process multiple images for one worker.

        Each image is processed independently using generate_embedding().
        """

        results = []

        for index, image in enumerate(images):
            result = self.generate_embedding(image)

            results.append({
                "image_index": index,
                "status": result["status"],
                "embedding": result["embedding"],
            })

        # Check whether all images produced valid embeddings.
        successful_results = [
            result
            for result in results
            if result["status"] == "SUCCESS"
        ]

        if len(successful_results) != len(images):
            return {
                "status": "ENROLLMENT_FAILED",
                "results": results,
            }

        return {
            "status": "SUCCESS",
            "embeddings": [
                result["embedding"]
                for result in successful_results
            ],
        }
