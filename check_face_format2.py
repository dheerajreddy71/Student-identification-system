import cv2
from backend.models.face_detection import FaceDetector

print("Checking face detector output...")

detector = FaceDetector()
img = cv2.imread("trainset/AGRI/AG1/AG1_1.jpg")

faces = detector.detect_faces(img)
print(f"Type: {type(faces)}")
print(f"Keys: {faces.keys() if isinstance(faces, dict) else 'Not a dict'}")
print(f"Full output:\n{faces}")
