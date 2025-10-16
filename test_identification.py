#!/usr/bin/env python3
"""
Test the identification API
"""
import requests
import cv2
import base64
import json
import os

def test_identification():
    # Find a test image from trainset
    test_image = None
    test_student_id = None
    
    for root, dirs, files in os.walk("trainset"):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_image = os.path.join(root, file)
                # Extract student ID from path
                test_student_id = os.path.basename(root).split('_')[0]
                break
        if test_image:
            break
    
    if not test_image:
        print("No test image found!")
        return
    
    print(f"Testing with image: {test_image}")
    print(f"Expected student: {test_student_id}")
    
    # Load and encode image
    image = cv2.imread(test_image)
    _, buffer = cv2.imencode('.jpg', image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    
    # Prepare API request
    url = "http://localhost:8000/identify"
    headers = {"Content-Type": "application/json"}
    data = {
        "image": encoded_image,
        "format": "jpg"
    }
    
    try:
        print("Sending identification request...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Identification successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get('identified'):
                identified_id = result.get('student_id')
                confidence = result.get('confidence', 0)
                print(f"\nResult: Student {identified_id} (confidence: {confidence:.3f})")
                
                if identified_id == test_student_id:
                    print("✓ Correct identification!")
                else:
                    print(f"✗ Incorrect identification (expected {test_student_id})")
            else:
                print("✗ Student not identified")
        else:
            print(f"✗ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_identification()