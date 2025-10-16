import cv2
from backend.models.face_detection import FaceDetector
from backend.models.adaface_model import AdaFaceModel

print("Testing single image processing...")
print("-" * 50)

# Load detector
print("Loading face detector...")
detector = FaceDetector()
print("OK")

# Load AdaFace
print("Loading AdaFace model...")
adaface = AdaFaceModel(model_path="./models/adaface_ir101_webface12m.ckpt", device='cpu')
print("OK\n")

# Test image
img_path = "trainset/AGRI/AG1/AG1_1.jpg"
print(f"Testing image: {img_path}")

# Load image
img = cv2.imread(img_path)
if img is None:
    print("ERROR: Could not load image!")
    exit(1)

print(f"Image loaded: shape={img.shape}")

# Detect faces
faces = detector.detect_faces(img)
print(f"Faces detected: {len(faces)}")

if not faces:
    print("ERROR: No faces detected!")
    exit(1)

# Get largest face
face = max(faces, key=lambda f: f['box'][2] * f['box'][3])
x, y, w, h = face['box']
print(f"Face box: x={x}, y={y}, w={w}, h={h}")

# Extract face
face_img = img[y:y+h, x:x+w]
print(f"Face extracted: shape={face_img.shape}")

# Resize
face_resized = cv2.resize(face_img, (112, 112))
print(f"Face resized: shape={face_resized.shape}")

# Extract embedding
emb = adaface.extract_embedding(face_resized)
print(f"Embedding extracted: shape={emb.shape if emb is not None else None}")

if emb is not None and emb.shape[0] == 512:
    print("\n✓ SUCCESS! Image processed correctly.")
else:
    print("\n✗ FAILED! Embedding extraction failed.")
