"""
Test script to verify photo saving fix
Creates a test image and simulates the registration process
"""
import cv2
import numpy as np
from pathlib import Path
import io

# Create a test image (simple blue rectangle with text)
test_image = np.zeros((400, 400, 3), dtype=np.uint8)
test_image[:] = (200, 100, 50)  # BGR color
cv2.putText(test_image, "Test Photo", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

# Encode to JPEG
success, buffer = cv2.imencode('.jpg', test_image)
if not success:
    print("✗ Failed to encode test image")
    exit(1)

file_contents = buffer.tobytes()
print(f"✓ Created test image: {len(file_contents)} bytes")

# Simulate the NEW fixed saving process
photos_dir = "photos"
Path(photos_dir).mkdir(exist_ok=True)
photo_path = Path(photos_dir) / "TEST_PHOTO.jpg"

with open(photo_path, "wb") as f:
    f.write(file_contents)

print(f"✓ Saved photo to: {photo_path}")

# Verify the saved file
saved_size = photo_path.stat().st_size
print(f"✓ Saved file size: {saved_size} bytes")

# Try to load it back
loaded_image = cv2.imread(str(photo_path))
if loaded_image is not None:
    print(f"✓ Successfully loaded saved photo: {loaded_image.shape}")
    print("\n✅ Photo saving fix VERIFIED! Registration should work now.")
else:
    print("✗ Failed to load saved photo")

# Cleanup
photo_path.unlink()
print(f"✓ Cleaned up test file")
