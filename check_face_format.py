import cv2
from backend.models.face_detection import FaceDetector

print("Checking face detector output format...")

detector = FaceDetector()
img = cv2.imread("trainset/AGRI/AG1/AG1_1.jpg")

faces = detector.detect_faces(img)
print(f"Faces detected: {len(faces)}")
print(f"Type: {type(faces)}")
print(f"First face: {faces[0] if faces else 'None'}")
print(f"First face type: {type(faces[0]) if faces else 'None'}")

if faces:
    face = faces[0]
    print(f"\nFace structure:")
    if isinstance(face, dict):
        for key, value in face.items():
            print(f"  {key}: {value}")
    else:
        print(f"  Face is not a dict, it's: {type(face)}")
        print(f"  Value: {face}")
