#!/usr/bin/env python3
"""
Test face recognition system with held-out test images
Uses real images that were NOT used during registration
"""
import os
import json
import cv2
import numpy as np
import sys
from pathlib import Path
from datetime import datetime
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models.face_detection import FaceDetector
from backend.models.adaface_model import AdaFaceModel
from backend.models.vector_db import FAISSVectorDB
from backend.database.operations import StudentDB
from backend.config import get_db
from backend.utils.failure_reason import classify_failure, print_failure_breakdown

# Configuration
TEST_DIR = "test_dataset"
FAISS_INDEX_PATH = "data/faiss_index.bin"
FAISS_METADATA_PATH = "data/faiss_metadata.json"
SIMILARITY_THRESHOLD = 0.45
RESULTS_DIR = "test_results"

class HoldoutTester:
    def __init__(self):
        print("=" * 70)
        print("🧪 HOLDOUT TEST - REAL UNSEEN IMAGES")
        print("=" * 70)
        
        print("\n🔧 Initializing models...")
        
        # Initialize face detector
        self.detector = FaceDetector(device='cpu')
        print("   ✅ Face detector loaded")
        
        # Initialize AdaFace model
        self.adaface = AdaFaceModel(
            model_path="./models/adaface_ir101_webface12m.ckpt",
            device='cpu'
        )
        print("   ✅ AdaFace model loaded")
        
        # Load FAISS index
        self.vector_db = FAISSVectorDB(
            embedding_dim=512,
            index_path=FAISS_INDEX_PATH,
            metadata_path=FAISS_METADATA_PATH,
            metric='cosine'
        )
        
        if self.vector_db.index.ntotal == 0:
            print("\n❌ ERROR: No embeddings in FAISS index!")
            print("Please run: python scripts/register_students.py --data_dir trainset")
            sys.exit(1)
        
        print(f"   ✅ FAISS index loaded ({self.vector_db.index.ntotal} embeddings)")
        
        # Load student database mapping
        self.load_student_mapping()
        
        # Load test split info
        self.load_test_split_info()
        
        self.results = {
            'test_date': datetime.now().isoformat(),
            'threshold': SIMILARITY_THRESHOLD,
            'total_students_tested': 0,
            'total_test_images': 0,
            'correct_rank1': 0,
            'correct_rank5': 0,
            'not_identified': 0,
            'wrong_identification': 0,
            'per_image_results': [],
            'per_student_results': {}
        }
    
    def load_student_mapping(self):
        """Load student ID to details mapping from database"""
        print("\n📂 Loading student database...")
        db = next(get_db())
        students = StudentDB.get_all_students(db, limit=10000)  # Load ALL students
        
        self.student_map = {}
        for student in students:
            self.student_map[student.student_id] = {
                'name': student.name,
                'department': student.department,
                'faiss_index': student.faiss_index
            }
        
        print(f"   ✅ Loaded {len(self.student_map)} registered students")
    
    def load_test_split_info(self):
        """Load information about test split"""
        if os.path.exists('test_split_info.json'):
            with open('test_split_info.json', 'r') as f:
                self.split_info = json.load(f)
            print(f"   ✅ Test split info loaded ({self.split_info['total_test_images']} test images)")
        else:
            print("   ⚠️  No test_split_info.json found")
            self.split_info = None
    
    def identify_face(self, image_path):
        """
        Identify face from image with detailed failure classification
        Returns: student_id, similarity, top_5_matches, processing_time, failure_info
        """
        start_time = time.time()
        
        # Initialize tracking variables
        face_detected = False
        face_info = None
        embedding = None
        similarity = 0.0
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            failure_info = classify_failure(False, None, None, None, SIMILARITY_THRESHOLD)
            return None, 0.0, [], time.time() - start_time, failure_info
        
        # Detect face
        aligned_face, face_info = self.detector.detect_and_align(image)
        face_detected = aligned_face is not None
        
        if aligned_face is None:
            failure_info = classify_failure(face_detected, face_info, None, None, SIMILARITY_THRESHOLD)
            return None, 0.0, [], time.time() - start_time, failure_info
        
        # Extract embedding
        embedding = self.adaface.extract_embedding(aligned_face, normalize=True)
        if embedding is None:
            failure_info = classify_failure(face_detected, face_info, embedding, None, SIMILARITY_THRESHOLD)
            return None, 0.0, [], time.time() - start_time, failure_info
        
        # Search in FAISS
        matches = self.vector_db.search_with_threshold(
            embedding,
            threshold=SIMILARITY_THRESHOLD,
            k=5
        )
        
        proc_time = time.time() - start_time
        
        if not matches:
            failure_info = classify_failure(face_detected, face_info, embedding, 0.0, SIMILARITY_THRESHOLD)
            return None, 0.0, [], proc_time, failure_info
        
        # Get top match
        top_match = matches[0]
        student_id = top_match['student_id']
        similarity = top_match['similarity']
        
        # Success case - no failure
        failure_info = None
        
        return student_id, similarity, matches, proc_time, failure_info
    
    def test_all_holdout_images(self):
        """Test all images in test_dataset"""
        print("\n" + "=" * 70)
        print("🧪 TESTING PHASE - HOLDOUT TEST SET")
        print("=" * 70)
        
        if not os.path.exists(TEST_DIR):
            print(f"\n❌ ERROR: Test directory '{TEST_DIR}' not found!")
            print("Please run: python prepare_test_split.py first")
            sys.exit(1)
        
        test_images = []
        
        # Collect all test images
        for dept in os.listdir(TEST_DIR):
            dept_path = os.path.join(TEST_DIR, dept)
            if not os.path.isdir(dept_path):
                continue
            
            for student_id in os.listdir(dept_path):
                student_path = os.path.join(dept_path, student_id)
                if not os.path.isdir(student_path):
                    continue
                
                # Check if student is registered
                if student_id not in self.student_map:
                    print(f"   ⚠️  {student_id} not in registered students - skipping")
                    continue
                
                # Get all test images for this student
                images = [f for f in os.listdir(student_path)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                
                for img_file in images:
                    test_images.append({
                        'path': os.path.join(student_path, img_file),
                        'true_id': student_id,
                        'department': dept,
                        'filename': img_file
                    })
        
        if not test_images:
            print("\n❌ ERROR: No test images found!")
            sys.exit(1)
        
        print(f"\n✅ Found {len(test_images)} test images from {len(set(t['true_id'] for t in test_images))} students")
        print(f"\n🔬 Starting identification tests...\n")
        
        self.results['total_test_images'] = len(test_images)
        self.results['total_students_tested'] = len(set(t['true_id'] for t in test_images))
        
        # Test each image
        for idx, test_item in enumerate(test_images, 1):
            true_id = test_item['true_id']
            image_path = test_item['path']
            
            # Show progress
            if idx % 20 == 0 or idx == 1:
                print(f"Progress: {idx}/{len(test_images)}")
            
            # Identify (now returns failure_info too)
            pred_id, similarity, top_5, proc_time, failure_info = self.identify_face(image_path)
            
            # Evaluate
            if pred_id is None:
                result_type = 'not_identified'
                self.results['not_identified'] += 1
                is_correct = False
            elif pred_id == true_id:
                result_type = 'correct_rank1'
                self.results['correct_rank1'] += 1
                self.results['correct_rank5'] += 1
                is_correct = True
            else:
                # Check if in top 5
                top_5_ids = [m['student_id'] for m in top_5]
                if true_id in top_5_ids:
                    result_type = 'correct_rank5'
                    self.results['correct_rank5'] += 1
                else:
                    result_type = 'wrong'
                self.results['wrong_identification'] += 1
                is_correct = False
            
            # Store per-image result with failure information
            result_entry = {
                'true_id': true_id,
                'predicted_id': pred_id,
                'similarity': similarity,
                'result': result_type,
                'processing_time': proc_time,
                'filename': test_item['filename'],
                'department': test_item['department']
            }
            
            # Add failure classification if identification failed
            if failure_info:
                result_entry['failure_reason'] = failure_info['reason']
                result_entry['failure_advice'] = failure_info['advice']
                result_entry['failure_status'] = failure_info['status']
            
            self.results['per_image_results'].append(result_entry)
            
            # Aggregate per-student results
            if true_id not in self.results['per_student_results']:
                self.results['per_student_results'][true_id] = {
                    'total': 0,
                    'correct': 0,
                    'wrong': 0,
                    'not_identified': 0,
                    'department': test_item['department']
                }
            
            self.results['per_student_results'][true_id]['total'] += 1
            if is_correct:
                self.results['per_student_results'][true_id]['correct'] += 1
            elif pred_id is None:
                self.results['per_student_results'][true_id]['not_identified'] += 1
            else:
                self.results['per_student_results'][true_id]['wrong'] += 1
        
        # Calculate metrics
        self.calculate_metrics()
        
        # Save results
        self.save_results()
        
        # Print report
        self.print_report()
    
    def calculate_metrics(self):
        """Calculate accuracy metrics"""
        total = self.results['total_test_images']
        
        if total > 0:
            self.results['rank1_accuracy'] = (self.results['correct_rank1'] / total) * 100
            self.results['rank5_accuracy'] = (self.results['correct_rank5'] / total) * 100
            self.results['identification_rate'] = ((total - self.results['not_identified']) / total) * 100
        else:
            self.results['rank1_accuracy'] = 0
            self.results['rank5_accuracy'] = 0
            self.results['identification_rate'] = 0
        
        # Calculate per-student accuracy
        student_accuracies = []
        for student_id, stats in self.results['per_student_results'].items():
            if stats['total'] > 0:
                accuracy = (stats['correct'] / stats['total']) * 100
                student_accuracies.append(accuracy)
                stats['accuracy'] = accuracy
        
        if student_accuracies:
            self.results['avg_student_accuracy'] = np.mean(student_accuracies)
            self.results['min_student_accuracy'] = np.min(student_accuracies)
            self.results['max_student_accuracy'] = np.max(student_accuracies)
    
    def save_results(self):
        """Save results to JSON"""
        os.makedirs(RESULTS_DIR, exist_ok=True)
        output_file = os.path.join(RESULTS_DIR, 'holdout_test_results.json')
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
    
    def print_report(self):
        """Print comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 HOLDOUT TEST RESULTS - FINAL REPORT")
        print("=" * 70)
        
        print(f"\n📅 Test Date: {self.results['test_date']}")
        print(f"🎯 Similarity Threshold: {self.results['threshold']}")
        print(f"👥 Students Tested: {self.results['total_students_tested']}")
        print(f"🖼️  Total Test Images: {self.results['total_test_images']}")
        
        print("\n" + "-" * 70)
        print("ACCURACY METRICS")
        print("-" * 70)
        
        print(f"\n📈 Rank-1 Accuracy (Top Match Correct):")
        print(f"   {self.results['rank1_accuracy']:.2f}% ({self.results['correct_rank1']}/{self.results['total_test_images']})")
        
        print(f"\n📈 Rank-5 Accuracy (Correct in Top 5):")
        print(f"   {self.results['rank5_accuracy']:.2f}% ({self.results['correct_rank5']}/{self.results['total_test_images']})")
        
        print(f"\n📈 Identification Rate (Face Detected & Matched):")
        print(f"   {self.results['identification_rate']:.2f}%")
        
        print("\n" + "-" * 70)
        print("DETAILED BREAKDOWN")
        print("-" * 70)
        
        print(f"\n✅ Correct Identifications (Rank-1): {self.results['correct_rank1']}")
        print(f"❌ Wrong Identifications: {self.results['wrong_identification']}")
        print(f"⚠️  Not Identified (Below Threshold): {self.results['not_identified']}")
        
        print("\n" + "-" * 70)
        print("PER-STUDENT ANALYSIS")
        print("-" * 70)
        
        print(f"\n📊 Average Accuracy Per Student: {self.results['avg_student_accuracy']:.2f}%")
        print(f"📊 Best Student Accuracy: {self.results['max_student_accuracy']:.2f}%")
        print(f"📊 Worst Student Accuracy: {self.results['min_student_accuracy']:.2f}%")
        
        # Show students with 100% accuracy
        perfect_students = [
            (sid, stats) for sid, stats in self.results['per_student_results'].items()
            if stats['accuracy'] == 100.0
        ]
        
        if perfect_students:
            print(f"\n✨ Students with 100% Accuracy: {len(perfect_students)}")
        
        # Show students with issues
        problem_students = [
            (sid, stats) for sid, stats in self.results['per_student_results'].items()
            if stats['accuracy'] < 50.0
        ]
        
        if problem_students:
            print(f"\n⚠️  Students with <50% Accuracy: {len(problem_students)}")
            print("\n   Problem Cases:")
            for sid, stats in sorted(problem_students, key=lambda x: x[1]['accuracy'])[:10]:
                student_name = self.student_map.get(sid, {}).get('name', 'Unknown')
                print(f"      {sid} ({student_name}): {stats['accuracy']:.1f}% "
                      f"({stats['correct']}/{stats['total']} correct)")
        
        # Show failure breakdown by reason
        print_failure_breakdown(self.results['per_image_results'])
        
        print("\n" + "=" * 70)
        print("✅ TESTING COMPLETE!")
        print("=" * 70)
        
        print(f"\n📄 Detailed results saved to: {RESULTS_DIR}/holdout_test_results.json")
        print("\n" + "=" * 70)


if __name__ == "__main__":
    tester = HoldoutTester()
    tester.test_all_holdout_images()
