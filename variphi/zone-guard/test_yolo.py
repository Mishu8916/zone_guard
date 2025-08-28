import cv2
import json
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import csv
import os
from alert_system import alert_system

# ----------------- Load Configuration -----------------
try:
    with open("config.json", "r") as f:
        config = json.load(f)
    video_source = config.get("video_source", "video2.mp4")
    model_path = config.get("model_path", "yolov8n.pt")
    confidence_threshold = config.get("confidence_threshold", 0.5)
    tracking_distance_threshold = config.get("tracking_distance_threshold", 50)
    log_file = config.get("log_file", "logs.csv")
    zones_file = config.get("zones_file", "zones.json")
    detection_classes = config.get("detection_classes", {})
    save_video = config.get("save_video", False)
    video_output = config.get("video_output", "output.mp4")
except FileNotFoundError:
    print("Config file not found, using default settings")
    video_source = "video2.mp4"
    model_path = "yolov8n.pt"
    confidence_threshold = 0.5
    tracking_distance_threshold = 50
    log_file = "logs.csv"
    zones_file = "zones.json"
    detection_classes = {"person": 0, "car": 2, "motorcycle": 3, "bus": 5, "truck": 7}
    save_video = False
    video_output = "output.mp4"

# ----------------- Load Zones -----------------
try:
    with open(zones_file, "r") as f:
        zones_data = json.load(f)
        if isinstance(zones_data, dict):
            zones = zones_data.get("zones", [])
            zone_labels = zones_data.get("labels", [])
        else:
            zones = zones_data
            zone_labels = [f"Zone {i+1}" for i in range(len(zones))]
    print(f"Loaded {len(zones)} zones: {zone_labels}")
except FileNotFoundError:
    print(f"Warning: {zones_file} not found. No zones will be monitored.")
    zones = []
    zone_labels = []

# ----------------- Video Setup -----------------
cap = cv2.VideoCapture(video_source)
if not cap.isOpened():
    print(f"Error: Could not open video source: {video_source}")
    exit()

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Setup video writer if saving is enabled
video_writer = None
if save_video:
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(video_output, fourcc, fps, (width, height))

# ----------------- YOLO Model -----------------
try:
    model = YOLO(model_path)
    print(f"Loaded YOLO model: {model_path}")
except Exception as e:
    print(f"Error loading model {model_path}: {e}")
    exit()

# ----------------- Tracker Setup -----------------
object_centroids = {}      # id: (cx, cy)
object_id_count = 0
object_zone_status = {}    # id: zone_index
object_classes = {}        # id: class_name

# ----------------- CSV Logging -----------------
log_file_path = log_file
csv_writer = None
log_file_handle = None

def setup_logging():
    global csv_writer, log_file_handle
    log_file_handle = open(log_file_path, "w", newline="")
    csv_writer = csv.writer(log_file_handle)
    csv_writer.writerow(["Timestamp", "ObjectID", "Zone", "Event", "Class", "Confidence"])

def close_logging():
    if log_file_handle:
        log_file_handle.close()

setup_logging()

# ----------------- Video Processing -----------------
print("Starting video processing...")
print(f"Monitoring classes: {list(detection_classes.keys())}")
print(f"Confidence threshold: {confidence_threshold}")
print("Press 'q' to quit")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    
    # Run YOLO detection
    results = model.predict(source=frame, save=False, verbose=False)
    
    new_centroids = []

    # Process detections
    for result in results:
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()

            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box.astype(int)
                label = int(class_ids[i])
                confidence = confidences[i]
                
                # Filter by class and confidence
                if label in detection_classes.values() and confidence >= confidence_threshold:
                    cx, cy = int((x1 + x2) // 2), int((y1 + y2) // 2)
                    class_name = [k for k, v in detection_classes.items() if v == label][0]
                    new_centroids.append((cx, cy, label, (x1, y1, x2, y2), confidence, class_name))

    # ----------------- Assign IDs (Simple Centroid Tracker) -----------------
    updated_centroids = {}
    updated_classes = {}
    
    for cx, cy, label, bbox, confidence, class_name in new_centroids:
        assigned = False
        for oid, (ocx, ocy) in object_centroids.items():
            if np.hypot(cx - ocx, cy - ocy) < tracking_distance_threshold:
                updated_centroids[oid] = (cx, cy)
                updated_classes[oid] = class_name
                assigned = True
                break
        if not assigned:
            object_id_count += 1
            updated_centroids[object_id_count] = (cx, cy)
            updated_classes[object_id_count] = class_name
    
    object_centroids = updated_centroids
    object_classes = updated_classes

    # ----------------- Zone Check -----------------
    for oid, (cx, cy) in object_centroids.items():
        inside_zone = None
        for idx, poly in enumerate(zones):
            polygon_np = np.array(poly, dtype=np.int32).reshape((-1, 1, 2))
            if cv2.pointPolygonTest(polygon_np, (cx, cy), False) >= 0:
                inside_zone = idx
                break

        prev_zone = object_zone_status.get(oid)
        if prev_zone != inside_zone:
            event_type = ""
            zone_name = ""
            
            if prev_zone is None and inside_zone is not None:
                event_type = "Entered"
                zone_name = zone_labels[inside_zone] if inside_zone < len(zone_labels) else f"Zone {inside_zone}"
                # Show alert for entry
                alert_system.show_entry_alert(oid, zone_name)
                
            elif prev_zone is not None and inside_zone is None:
                event_type = "Exited"
                zone_name = zone_labels[prev_zone] if prev_zone < len(zone_labels) else f"Zone {prev_zone}"
                # Show alert for exit
                alert_system.show_exit_alert(oid, zone_name)
                
            elif prev_zone != inside_zone:
                event_type = "Moved"
                zone_name = zone_labels[inside_zone] if inside_zone < len(zone_labels) else f"Zone {inside_zone}"

            if event_type:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                class_name = object_classes.get(oid, "Unknown")
                csv_writer.writerow([timestamp, oid, zone_name, event_type, class_name, confidence])
                print(f"[{timestamp}] Object {oid} ({class_name}) {event_type} {zone_name}")

        object_zone_status[oid] = inside_zone

    # ----------------- Draw -----------------
    # Draw objects
    for oid, (cx, cy) in object_centroids.items():
        class_name = object_classes.get(oid, "Unknown")
        color = (0, 255, 0) if object_zone_status.get(oid) is None else (0, 0, 255)
        
        cv2.circle(frame, (cx, cy), 5, color, -1)
        cv2.putText(frame, f"ID {oid} ({class_name})", (cx + 5, cy - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # Draw zones
    for i, (poly, label) in enumerate(zip(zones, zone_labels)):
        polygon_np = np.array(poly, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [polygon_np], True, (255, 0, 0), 2)
        
        # Add zone label
        if len(poly) > 0:
            center_x = sum(p[0] for p in poly) // len(poly)
            center_y = sum(p[1] for p in poly) // len(poly)
            cv2.putText(frame, label, (center_x-20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Add status information
    cv2.putText(frame, f"Frame: {frame_count} | Objects: {len(object_centroids)} | Zones: {len(zones)}", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Press 'q' to quit", 
               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Write frame if saving video
    if video_writer:
        video_writer.write(frame)

    cv2.imshow("Zone Guard - Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ----------------- Cleanup -----------------
cap.release()
if video_writer:
    video_writer.release()
cv2.destroyAllWindows()
close_logging()
alert_system.cleanup()

print(f"\nProcessing complete!")
print(f"Processed {frame_count} frames")
print(f"Tracked {object_id_count} objects")
print(f"Logs saved to: {log_file_path}")
if save_video:
    print(f"Video saved to: {video_output}")
