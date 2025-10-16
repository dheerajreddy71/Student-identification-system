#!/usr/bin/env python3
"""
Test the complete system end-to-end
"""
import requests
import base64
import cv2
import os
import json

def test_system():
    print("🧪 Testing Student Identification System")
    print("=" * 50)
    
    # Test 1: Check backend health
    print("1. Testing backend connectivity...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend")
        return
    
    # Test 2: Check authentication
    print("2. Testing authentication...")
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            data=login_data,
            timeout=10
        )
        if response.status_code == 200:
            token = response.json()['access_token']
            print("   ✅ Authentication successful")
        else:
            print("   ❌ Authentication failed")
            return
    except Exception as e:
        print(f"   ❌ Auth error: {e}")
        return
    
    # Test 3: Check database
    print("3. Testing database...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            "http://localhost:8000/api/students",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            students = response.json()
            print(f"   ✅ Database accessible ({len(students)} students)")
            if len(students) == 0:
                print("   ⚠️  No students registered yet")
        else:
            print("   ❌ Database access failed")
            return
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return
    
    # Test 4: Test identification (if students exist)
    if len(students) > 0:
        print("4. Testing identification...")
        # Find a test image
        test_image_path = None
        for root, dirs, files in os.walk("trainset"):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_image_path = os.path.join(root, file)
                    break
            if test_image_path:
                break
        
        if test_image_path:
            try:
                # Load and prepare image
                image = cv2.imread(test_image_path)
                _, buffer = cv2.imencode('.jpg', image)
                encoded_image = base64.b64encode(buffer).decode('utf-8')
                
                # Send identification request
                data = {
                    "image": encoded_image,
                    "format": "jpg"
                }
                response = requests.post(
                    "http://localhost:8000/api/students/identify",
                    json=data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('identified'):
                        print(f"   ✅ Identification successful: {result.get('student_id')}")
                        print(f"      Confidence: {result.get('confidence', 0):.3f}")
                    else:
                        print("   ⚠️  No match found (below threshold)")
                else:
                    print(f"   ❌ Identification failed: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Identification error: {e}")
        else:
            print("   ⚠️  No test images found")
    
    print("\n🎉 System test completed!")
    print("\n📖 Next Steps:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Login with admin/admin123")
    print("   3. Test the identification system!")

if __name__ == "__main__":
    test_system()