# Zone Guard - Surveillance System

A comprehensive surveillance system that allows users to define restricted zones and monitor object intrusions using computer vision and machine learning.

## Features

- 🎨 **Interactive Zone Drawing**: Draw polygonal zones on video frames with labels
- 🤖 **AI-Powered Detection**: YOLOv8 object detection for people and vehicles
- 📍 **Real-time Tracking**: Centroid-based object tracking across frames
- 🚨 **Intrusion Alerts**: Popup notifications for zone entries and exits
- 📊 **Event Logging**: Comprehensive CSV logging with timestamps
- 🖥️ **User-Friendly GUI**: Integrated main application with status monitoring
- ⚙️ **Configurable Settings**: JSON-based configuration system

## Requirements

- Python 3.7+
- OpenCV
- Ultralytics (YOLOv8)
- Tkinter (usually included with Python)
- Pandas
- NumPy

## Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download YOLOv8 model** (if not included):
   ```bash
   # The yolov8n.pt file should be in the project directory
   # If missing, it will be downloaded automatically on first run
   ```

## Quick Start

1. **Run the main application**:
   ```bash
   python main.py
   ```

2. **Draw zones**:
   - Click "🎨 Draw Zones" button
   - Left-click to add polygon points
   - Right-click to finish a zone
   - Enter a label for each zone
   - Press 'q' to quit and save

3. **Start detection**:
   - Click "🎥 Start Detection" button
   - Watch for intrusion alerts
   - View real-time tracking

4. **Check logs**:
   - Click "📊 View Logs" to see recent events
   - Logs are saved to `logs.csv`

## File Structure

```
zone-guard/
├── main.py              # Main GUI application
├── draw_zones.py        # Zone drawing interface
├── test_yolo.py         # Detection and tracking system
├── alert_system.py      # Alert notification system
├── config.json          # Configuration settings
├── zones.json           # Saved zone definitions
├── logs.csv             # Event logs
├── yolov8n.pt           # YOLOv8 model file
├── video2.mp4           # Sample video file
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Configuration

Edit `config.json` to customize settings:

```json
{
    "video_source": "video2.mp4",
    "model_path": "yolov8n.pt",
    "confidence_threshold": 0.5,
    "tracking_distance_threshold": 50,
    "log_file": "logs.csv",
    "zones_file": "zones.json",
    "detection_classes": {
        "person": 0,
        "car": 2,
        "motorcycle": 3,
        "bus": 5,
        "truck": 7
    },
    "alert_enabled": true,
    "save_video": false,
    "video_output": "output.mp4"
}
```

### Configuration Options

- **video_source**: Path to input video file
- **model_path**: Path to YOLOv8 model file
- **confidence_threshold**: Minimum confidence for detections (0.0-1.0)
- **tracking_distance_threshold**: Distance threshold for object tracking
- **detection_classes**: Object classes to monitor
- **alert_enabled**: Enable/disable alerts
- **alert_type**: Alert system type ("console" or "gui")
- **save_video**: Save processed video with annotations

## Usage Instructions

### Zone Drawing

1. **Start zone drawing**:
   ```bash
   python draw_zones.py
   ```

2. **Controls**:
   - **Left Click**: Add point to current zone
   - **Right Click**: Finish current zone (minimum 3 points)
   - **'q'**: Quit and save zones
   - **'c'**: Clear current zone
   - **'r'**: Reset all zones

3. **Zone labeling**: Each zone will prompt for a label (e.g., "Restricted Area 1")

### Detection and Monitoring

1. **Start detection**:
   ```bash
   python test_yolo.py
   ```

2. **Features**:
   - Real-time object detection and tracking
   - Zone intrusion detection
   - Popup alerts for entries/exits
   - Live video display with annotations
   - Automatic CSV logging

3. **Controls**:
   - **'q'**: Quit detection

### Main Application

1. **Launch GUI**:
   ```bash
   python main.py
   ```

2. **Features**:
   - Integrated zone drawing and detection
   - Real-time status monitoring
   - Live log viewing
   - System health checks
   - Easy file management

## Log Format

Events are logged to `logs.csv` with the following columns:

- **Timestamp**: Event time (YYYY-MM-DD HH:MM:SS)
- **ObjectID**: Unique object identifier
- **Zone**: Zone name where event occurred
- **Event**: Event type (Entered/Exited/Moved)
- **Class**: Object class (person/car/etc.)
- **Confidence**: Detection confidence score

## Troubleshooting

### Common Issues

1. **"Video file not found"**:
   - Ensure video file exists in project directory
   - Check `config.json` video_source path

2. **"Model file not found"**:
   - Download YOLOv8 model: `yolov8n.pt`
   - Check `config.json` model_path

3. **"No zones defined"**:
   - Run zone drawing first: `python draw_zones.py`
   - Ensure `zones.json` exists

4. **Performance issues**:
   - Lower confidence threshold in config
   - Use smaller video files
   - Reduce tracking distance threshold

### System Requirements

- **CPU**: Multi-core processor recommended
- **RAM**: 4GB+ for smooth operation
- **GPU**: Optional, CUDA-compatible for acceleration
- **Storage**: 1GB+ free space for logs and videos

## Advanced Features

### Custom Object Classes

Modify `config.json` to detect different objects:

```json
{
    "detection_classes": {
        "person": 0,
        "bicycle": 1,
        "car": 2,
        "motorcycle": 3,
        "airplane": 4,
        "bus": 5,
        "train": 6,
        "truck": 7
    }
}
```

### Video Recording

Enable video recording in `config.json`:

```json
{
    "save_video": true,
    "video_output": "output.mp4"
}
```

### Alert Customization

Configure alerts in `config.json`:
```json
{
    "alert_enabled": true,
    "alert_type": "console"
}
```

**Alert Types:**
- **"console"**: Show alerts in terminal (recommended, no threading issues)
- **"gui"**: Show popup dialogs (may cause threading issues)

Modify `alert_system.py` to customize alert behavior:
- Change alert messages
- Add sound notifications
- Integrate with external systems

## Development

### Adding New Features

1. **New detection models**: Modify `test_yolo.py`
2. **Enhanced tracking**: Implement SORT/DeepSORT
3. **Database logging**: Replace CSV with SQLite/PostgreSQL
4. **Web interface**: Add Flask/FastAPI backend
5. **Mobile alerts**: Integrate push notifications

### Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Test thoroughly
5. Submit pull request

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues and questions:
1. Check troubleshooting section
2. Review configuration settings
3. Ensure all dependencies are installed
4. Check system requirements

## Version History

- **v1.0**: Initial release with basic functionality
- **v1.1**: Added GUI, alerts, and configuration system
- **v1.2**: Enhanced zone labeling and status monitoring
