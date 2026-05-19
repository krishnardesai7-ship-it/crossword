import base64
import time
from pathlib import Path

import cv2
import numpy as np
try:
    import face_recognition
except ModuleNotFoundError:
    face_recognition = None

from core.settings import BASE_DIR


def close_cv_windows():
    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass


class FaceRecognition:
    def __init__(self):
        self.encoding_dir = Path(BASE_DIR) / "media" / "encodings"
        self.encoding_dir.mkdir(parents=True, exist_ok=True)

    def _load_known_faces(self):
        known_ids = []
        known_encodings = []

        for file_path in self.encoding_dir.glob("*.npy"):
            try:
                user_id = int(file_path.stem)
                encoding = np.load(file_path)
                known_ids.append(user_id)
                known_encodings.append(encoding)
            except Exception:
                continue

        return known_ids, known_encodings

    def enroll_face(self, user_id, required_samples=5, timeout_seconds=25):
        if face_recognition is None:
            return False, "face_library_missing"

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            return False, "Unable to open camera."

        samples = []
        start = time.time()

        while True:
            ret, frame = cam.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, locations)

            for (top, right, bottom, left), encoding in zip(locations, encodings):
                cv2.rectangle(frame, (left, top),
                              (right, bottom), (0, 255, 0), 2)
                if len(samples) < required_samples:
                    samples.append(encoding)

            cv2.putText(
                frame,
                f"Samples: {len(samples)}/{required_samples} (ESC to cancel)",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )
            cv2.imshow("Face Registration", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                cam.release()
                close_cv_windows()
                return False, "Face registration canceled."

            if len(samples) >= required_samples:
                avg_encoding = np.mean(np.array(samples), axis=0)
                np.save(self.encoding_dir / f"{user_id}.npy", avg_encoding)
                cam.release()
                close_cv_windows()
                return True, "Face registered successfully."

            if (time.time() - start) > timeout_seconds:
                cam.release()
                close_cv_windows()
                return False, "Face registration timed out."

    def enroll_face_from_image(self, user_id, b64_image_string):
        """
        Enroll a face from a base64-encoded image captured by the browser webcam.
        Returns (success: bool, message: str)
        """
        if face_recognition is None:
            return False, "face_library_missing"

        try:
            # Strip the data-URL prefix if present (e.g. "data:image/jpeg;base64,...")
            if "," in b64_image_string:
                b64_image_string = b64_image_string.split(",", 1)[1]

            img_bytes = base64.b64decode(b64_image_string)
            np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                return False, "Could not decode image."

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, locations)

            if not encodings:
                return False, "No face detected in the image. Please try again."

            # Use the first (largest) face found
            encoding = encodings[0]
            np.save(self.encoding_dir / f"{user_id}.npy", encoding)
            return True, "Face registered successfully."

        except Exception as exc:
            return False, f"Face enrollment error: {exc}"

    def recognize_face(self, tolerance=0.45, timeout_seconds=20):
        if face_recognition is None:
            return None, "face_library_missing"

        known_ids, known_encodings = self._load_known_faces()
        if not known_ids:
            return None, "no_known_faces"

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            return None, "camera_error"

        # Warm up camera auto exposure/focus for more stable first frames.
        for _ in range(10):
            cam.read()

        start = time.time()
        matched_user_id = None
        saw_any_face = False

        while True:
            ret, frame = cam.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, locations)

            for (top, right, bottom, left), face_encoding in zip(locations, encodings):
                saw_any_face = True
                distances = face_recognition.face_distance(
                    known_encodings, face_encoding)
                best_index = int(np.argmin(distances))
                best_distance = float(distances[best_index])

                if best_distance <= tolerance:
                    matched_user_id = known_ids[best_index]
                    label = f"Matched: {matched_user_id}"
                    color = (0, 255, 0)
                else:
                    label = "Unknown"
                    color = (0, 0, 255)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(
                    frame,
                    f"{label} ({best_distance:.2f})",
                    (left, max(20, top - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )

                if matched_user_id is not None:
                    cam.release()
                    close_cv_windows()
                    return matched_user_id, "matched"

            cv2.imshow("Face Login", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                cam.release()
                close_cv_windows()
                return None, "canceled"

            if (time.time() - start) > timeout_seconds:
                cam.release()
                close_cv_windows()
                if saw_any_face:
                    return None, "face_not_matched"
                break

        cam.release()
        close_cv_windows()
        return None, "no_face_detected"
