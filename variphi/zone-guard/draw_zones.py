import cv2
import json
import numpy as np
import tkinter as tk
from tkinter import simpledialog

# Load config
try:
    with open("config.json", "r") as f:
        config = json.load(f)
    video_source = config.get("video_source", "video2.mp4")
except FileNotFoundError:
    video_source = "video2.mp4"

zones = []
zone_labels = []
current_zone = []

def get_zone_label():
    """Get zone label from user via dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    label = simpledialog.askstring("Zone Label", "Enter zone label (e.g., 'Restricted Area 1'):")
    root.destroy()
    return label if label else f"Zone {len(zones) + 1}"

def click_event(event, x, y, flags, param):
    global current_zone, zones, zone_labels
    if event == cv2.EVENT_LBUTTONDOWN:
        current_zone.append([x, y])
        print(f"Added point: ({x}, {y})")
    elif event == cv2.EVENT_RBUTTONDOWN:  # Right click to finish polygon
        if len(current_zone) >= 3:  # Minimum 3 points for polygon
            label = get_zone_label()
            if label:  # Only add if user provided a label
                zones.append(current_zone.copy())
                zone_labels.append(label)
                print(f"Zone '{label}' created with {len(current_zone)} points")
                current_zone = []
        else:
            print("Need at least 3 points to create a zone")

def load_existing_zones():
    """Load existing zones if available"""
    global zones, zone_labels
    try:
        with open("zones.json", "r") as f:
            zones_data = json.load(f)
            if isinstance(zones_data, dict):
                zones = zones_data.get("zones", [])
                zone_labels = zones_data.get("labels", [])
            else:
                zones = zones_data
                zone_labels = [f"Zone {i+1}" for i in range(len(zones))]
        print(f"Loaded {len(zones)} existing zones")
    except FileNotFoundError:
        print("No existing zones found. Starting fresh.")

def main():
    global zones, zone_labels, current_zone
    
    # Load existing zones
    load_existing_zones()
    
    # Load video frame
    cap = cv2.VideoCapture(video_source)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"Error: Could not read video from {video_source}")
        return
    
    cv2.namedWindow("Draw Zones - Zone Guard")
    cv2.setMouseCallback("Draw Zones - Zone Guard", click_event)
    
    print("=== Zone Drawing Instructions ===")
    print("Left Click: Add point to current zone")
    print("Right Click: Finish current zone (min 3 points)")
    print("'q': Quit and save zones")
    print("'c': Clear current zone")
    print("'r': Reset all zones")
    print("================================")
    
    while True:
        temp_frame = frame.copy()
        
        # Draw completed zones
        for i, (poly, label) in enumerate(zip(zones, zone_labels)):
            pts = np.array(poly, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(temp_frame, [pts], True, (255, 0, 0), 2)
            
            # Add zone label
            if len(poly) > 0:
                center_x = sum(p[0] for p in poly) // len(poly)
                center_y = sum(p[1] for p in poly) // len(poly)
                cv2.putText(temp_frame, label, (center_x-20, center_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Draw current zone being created
        if current_zone:
            pts = np.array(current_zone, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(temp_frame, [pts], False, (0, 255, 0), 2)
            
            # Draw points
            for point in current_zone:
                cv2.circle(temp_frame, tuple(point), 3, (0, 255, 0), -1)
        
        # Add instructions to frame
        cv2.putText(temp_frame, "Left Click: Add Point | Right Click: Finish Zone | Q: Quit", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(temp_frame, f"Zones: {len(zones)} | Current Points: {len(current_zone)}", 
                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("Draw Zones - Zone Guard", temp_frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("q"):  # Press 'q' to quit and save zones
            break
        elif key == ord("c"):  # Clear current zone
            current_zone = []
            print("Current zone cleared")
        elif key == ord("r"):  # Reset all zones
            zones = []
            zone_labels = []
            current_zone = []
            print("All zones reset")

    cv2.destroyAllWindows()

    # Save zones to JSON
    zones_data = {
        "zones": zones,
        "labels": zone_labels
    }
    
    with open("zones.json", "w") as f:
        json.dump(zones_data, f, indent=4)

    print(f"\n=== Zone Drawing Complete ===")
    print(f"{len(zones)} zones saved to zones.json")
    for i, label in enumerate(zone_labels):
        print(f"Zone {i+1}: {label} ({len(zones[i])} points)")

if __name__ == "__main__":
    main()
