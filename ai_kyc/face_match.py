from typing import Dict, Any, Optional

import numpy as np
import cv2
from deepface import DeepFace


def _read_image_from_bytes(image_bytes: bytes) -> np.ndarray:

    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image from bytes")
    return img


def verify_faces(
    id_image_bytes: bytes,
    selfie_image_bytes: bytes,
    model_name: str = "Facenet",
    distance_metric: str = "cosine",
    threshold: float = 0.6,
) -> Dict[str, Any]:
    # Default "safe fail" response
    default_result: Dict[str, Any] = {
        "face_verified": False,
        "face_score": 0.0,
        "liveness_passed": False,
        "error": None,
    }

    # 1) Decode images
    try:
        id_img = _read_image_from_bytes(id_image_bytes)
        selfie_img = _read_image_from_bytes(selfie_image_bytes)
    except Exception as e:
        default_result["error"] = f"Image decode error: {e}"
        return default_result

    # 2) Run DeepFace verification
    try:
        # DeepFace supports numpy arrays as img1_path / img2_path
        raw_result = DeepFace.verify(
            img1_path=id_img,
            img2_path=selfie_img,
            model_name=model_name,
            distance_metric=distance_metric,
            enforce_detection=False,  # do NOT crash if no face detected
        )
    except Exception as e:
        # This catches "Exception while processing img2_path" and all others
        default_result["error"] = f"DeepFace error: {e}"
        return default_result

    # 3) Interpret result safely
    try:
        # For cosine distance: 0 = identical, larger = more different.
        # We'll convert it into a 0–1 "similarity score" where 1 = best.
        distance = float(raw_result.get("distance", 1.0))
        # Clamp distance between 0 and 1.5 just to avoid weird values
        distance = max(0.0, min(distance, 1.5))
        score = 1.0 - (distance / 1.5)  # map to ~[0,1]
        score = max(0.0, min(score, 1.0))

        deepface_verified = bool(raw_result.get("verified", False))
        face_verified = deepface_verified and score >= threshold

        liveness_passed = face_verified

        result: Dict[str, Any] = {
            "face_verified": face_verified,
            "face_score": float(round(score, 6)),
            "liveness_passed": bool(liveness_passed),
            "error": None,
        }
        return result

    except Exception as e:
        default_result["error"] = f"Post-processing error: {e}"
        return default_result


if __name__ == "__main__":
    import sys
    import json
    from pathlib import Path

    if len(sys.argv) != 3:
        print("Usage: python face_match.py <id_image> <selfie_image>")
        sys.exit(1)

    id_path = Path(sys.argv[1])
    selfie_path = Path(sys.argv[2])

    if not id_path.is_file() or not selfie_path.is_file():
        print("Error: one or both image paths are invalid.")
        sys.exit(1)

    with id_path.open("rb") as f:
        id_bytes = f.read()
    with selfie_path.open("rb") as f:
        selfie_bytes = f.read()

    out = verify_faces(id_bytes, selfie_bytes)
    print(json.dumps(out, indent=2))
