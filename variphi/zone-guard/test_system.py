import unittest
import json
import os
import sys
import cv2
import numpy as np
from datetime import datetime

class TestZoneGuard(unittest.TestCase):
    """Test suite for Zone Guard system components"""
    
    def setUp(self):
        """Set up test environment"""
        self.config_file = "config.json"
        self.zones_file = "zones.json"
        self.log_file = "logs.csv"
        self.model_file = "yolov8n.pt"
        self.video_file = "video2.mp4"
    
    def test_config_file_exists(self):
        """Test if configuration file exists and is valid JSON"""
        self.assertTrue(os.path.exists(self.config_file), 
                       f"Config file {self.config_file} not found")
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            self.assertIsInstance(config, dict, "Config should be a dictionary")
            
            # Check required keys
            required_keys = ['video_source', 'model_path', 'confidence_threshold']
            for key in required_keys:
                self.assertIn(key, config, f"Config missing required key: {key}")
                
        except json.JSONDecodeError as e:
            self.fail(f"Config file is not valid JSON: {e}")
    
    def test_zones_file_format(self):
        """Test zones file format"""
        if os.path.exists(self.zones_file):
            try:
                with open(self.zones_file, 'r') as f:
                    zones_data = json.load(f)
                
                # Check if it's the new format (dict) or old format (list)
                if isinstance(zones_data, dict):
                    self.assertIn('zones', zones_data, "Zones data should have 'zones' key")
                    self.assertIn('labels', zones_data, "Zones data should have 'labels' key")
                    zones = zones_data['zones']
                    labels = zones_data['labels']
                else:
                    zones = zones_data
                    labels = [f"Zone {i+1}" for i in range(len(zones))]
                
                self.assertIsInstance(zones, list, "Zones should be a list")
                self.assertIsInstance(labels, list, "Labels should be a list")
                self.assertEqual(len(zones), len(labels), 
                               "Number of zones and labels should match")
                
                # Test zone format
                for i, zone in enumerate(zones):
                    self.assertIsInstance(zone, list, f"Zone {i} should be a list")
                    self.assertGreaterEqual(len(zone), 3, 
                                          f"Zone {i} should have at least 3 points")
                    for point in zone:
                        self.assertIsInstance(point, list, 
                                           f"Points in zone {i} should be lists")
                        self.assertEqual(len(point), 2, 
                                       f"Points in zone {i} should have 2 coordinates")
                        
            except json.JSONDecodeError as e:
                self.fail(f"Zones file is not valid JSON: {e}")
    
    def test_model_file_exists(self):
        """Test if YOLO model file exists"""
        self.assertTrue(os.path.exists(self.model_file), 
                       f"Model file {self.model_file} not found")
        
        # Check file size (should be several MB)
        file_size = os.path.getsize(self.model_file)
        self.assertGreater(file_size, 1000000, 
                          f"Model file seems too small: {file_size} bytes")
    
    def test_video_file_exists(self):
        """Test if video file exists and is readable"""
        self.assertTrue(os.path.exists(self.video_file), 
                       f"Video file {self.video_file} not found")
        
        # Test if video can be opened
        cap = cv2.VideoCapture(self.video_file)
        self.assertTrue(cap.isOpened(), f"Could not open video file {self.video_file}")
        
        # Test if we can read at least one frame
        ret, frame = cap.read()
        self.assertTrue(ret, f"Could not read frame from {self.video_file}")
        self.assertIsInstance(frame, np.ndarray, "Frame should be numpy array")
        
        cap.release()
    
    def test_required_python_files(self):
        """Test if all required Python files exist"""
        required_files = [
            "main.py",
            "draw_zones.py", 
            "test_yolo.py",
            "alert_system.py"
        ]
        
        for file in required_files:
            self.assertTrue(os.path.exists(file), f"Required file {file} not found")
    
    def test_imports(self):
        """Test if all required modules can be imported"""
        try:
            import cv2
            import numpy as np
            import json
            import pandas as pd
            from ultralytics import YOLO
            import tkinter as tk
        except ImportError as e:
            self.fail(f"Failed to import required module: {e}")
    
    def test_config_values(self):
        """Test configuration values are reasonable"""
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Test confidence threshold
        confidence = config.get('confidence_threshold', 0.5)
        self.assertGreaterEqual(confidence, 0.0, "Confidence threshold should be >= 0")
        self.assertLessEqual(confidence, 1.0, "Confidence threshold should be <= 1")
        
        # Test tracking distance threshold
        tracking_dist = config.get('tracking_distance_threshold', 50)
        self.assertGreater(tracking_dist, 0, "Tracking distance should be > 0")
        self.assertLess(tracking_dist, 1000, "Tracking distance should be reasonable")
        
        # Test detection classes
        detection_classes = config.get('detection_classes', {})
        self.assertIsInstance(detection_classes, dict, "Detection classes should be dict")
        self.assertGreater(len(detection_classes), 0, "Should have at least one detection class")
    
    def test_log_file_format(self):
        """Test log file format if it exists"""
        if os.path.exists(self.log_file):
            try:
                import pandas as pd
                df = pd.read_csv(self.log_file)
                
                # Check required columns
                required_columns = ['Timestamp', 'ObjectID', 'Zone', 'Event']
                for col in required_columns:
                    self.assertIn(col, df.columns, f"Log file missing column: {col}")
                
                # Check timestamp format
                if len(df) > 0:
                    timestamp = df['Timestamp'].iloc[0]
                    try:
                        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        self.fail(f"Invalid timestamp format: {timestamp}")
                        
            except Exception as e:
                self.fail(f"Could not read log file: {e}")
    
    def test_zone_drawing_functionality(self):
        """Test zone drawing basic functionality"""
        # Test if draw_zones.py can be imported
        try:
            # This is a basic test - in a real scenario you'd want to test the GUI
            # For now, just check if the file can be parsed
            with open("draw_zones.py", 'r') as f:
                content = f.read()
            self.assertIn("def click_event", content, "draw_zones.py should have click_event function")
            self.assertIn("cv2.setMouseCallback", content, "draw_zones.py should use mouse callback")
        except Exception as e:
            self.fail(f"Could not test draw_zones.py: {e}")
    
    def test_detection_functionality(self):
        """Test detection basic functionality"""
        try:
            with open("test_yolo.py", 'r') as f:
                content = f.read()
            self.assertIn("YOLO", content, "test_yolo.py should use YOLO")
            self.assertIn("cv2.pointPolygonTest", content, "test_yolo.py should use polygon test")
        except Exception as e:
            self.fail(f"Could not test test_yolo.py: {e}")

def run_system_check():
    """Run a comprehensive system check"""
    print("=== Zone Guard System Check ===")
    
    # Check files
    files_to_check = [
        ("config.json", "Configuration file"),
        ("zones.json", "Zones definition file"),
        ("yolov8n.pt", "YOLO model file"),
        ("video2.mp4", "Video file"),
        ("main.py", "Main application"),
        ("draw_zones.py", "Zone drawing script"),
        ("test_yolo.py", "Detection script"),
        ("alert_system.py", "Alert system"),
        ("requirements.txt", "Dependencies file")
    ]
    
    print("\n📁 File Check:")
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"  ✅ {description}: {filename}")
        else:
            print(f"  ❌ {description}: {filename} (MISSING)")
    
    # Check Python modules
    print("\n🐍 Module Check:")
    modules_to_check = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("ultralytics", "Ultralytics (YOLOv8)"),
        ("tkinter", "Tkinter"),
        ("json", "JSON"),
        ("datetime", "DateTime")
    ]
    
    for module_name, description in modules_to_check:
        try:
            __import__(module_name)
            print(f"  ✅ {description}: {module_name}")
        except ImportError:
            print(f"  ❌ {description}: {module_name} (MISSING)")
    
    # Check configuration
    print("\n⚙️ Configuration Check:")
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        print(f"  ✅ Config loaded successfully")
        print(f"  📹 Video source: {config.get('video_source', 'Not set')}")
        print(f"  🤖 Model path: {config.get('model_path', 'Not set')}")
        print(f"  🎯 Confidence threshold: {config.get('confidence_threshold', 'Not set')}")
        print(f"  📊 Detection classes: {list(config.get('detection_classes', {}).keys())}")
    except Exception as e:
        print(f"  ❌ Config error: {e}")
    
    # Check zones
    print("\n🎨 Zones Check:")
    try:
        with open("zones.json", 'r') as f:
            zones_data = json.load(f)
        if isinstance(zones_data, dict):
            zones_count = len(zones_data.get("zones", []))
            labels = zones_data.get("labels", [])
        else:
            zones_count = len(zones_data)
            labels = [f"Zone {i+1}" for i in range(zones_count)]
        print(f"  ✅ Zones loaded: {zones_count} zones")
        print(f"  🏷️ Zone labels: {labels}")
    except Exception as e:
        print(f"  ❌ Zones error: {e}")
    
    print("\n=== System Check Complete ===")

if __name__ == "__main__":
    # Run system check
    run_system_check()
    
    # Run unit tests
    print("\n🧪 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
