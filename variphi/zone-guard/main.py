import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys
import os
import json
import threading
import pandas as pd
from datetime import datetime

class ZoneGuardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Guard - Surveillance System")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Load config
        self.load_config()
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create title
        title_label = ttk.Label(self.main_frame, text="Zone Guard Surveillance System", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill='x', pady=10)
        
        # Create buttons
        self.create_buttons()
        
        # Create status frame
        self.status_frame = ttk.LabelFrame(self.main_frame, text="System Status")
        self.status_frame.pack(fill='x', pady=10)
        
        # Create status labels
        self.create_status_labels()
        
        # Create logs frame
        self.logs_frame = ttk.LabelFrame(self.main_frame, text="Recent Events")
        self.logs_frame.pack(fill='both', expand=True, pady=10)
        
        # Create logs display
        self.create_logs_display()
        
        # Update status
        self.update_status()
        
        # Start periodic updates
        self.root.after(5000, self.periodic_update)
        
    def load_config(self):
        """Load configuration file"""
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
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
                "alert_enabled": True,
                "save_video": False,
                "video_output": "output.mp4"
            }
    
    def create_buttons(self):
        """Create main action buttons"""
        # First row
        row1 = ttk.Frame(self.buttons_frame)
        row1.pack(fill='x', pady=5)
        
        ttk.Button(row1, text="🎨 Draw Zones", command=self.draw_zones, 
                  style='Action.TButton').pack(side='left', padx=5)
        ttk.Button(row1, text="🎥 Start Detection", command=self.start_detection, 
                  style='Action.TButton').pack(side='left', padx=5)
        ttk.Button(row1, text="📊 View Logs", command=self.view_logs, 
                  style='Action.TButton').pack(side='left', padx=5)
        
        # Second row
        row2 = ttk.Frame(self.buttons_frame)
        row2.pack(fill='x', pady=5)
        
        ttk.Button(row2, text="⚙️ Settings", command=self.open_settings, 
                  style='Action.TButton').pack(side='left', padx=5)
        ttk.Button(row2, text="📁 Open Logs Folder", command=self.open_logs_folder, 
                  style='Action.TButton').pack(side='left', padx=5)
        ttk.Button(row2, text="❓ Help", command=self.show_help, 
                  style='Action.TButton').pack(side='left', padx=5)
        
        # Configure button styles
        style = ttk.Style()
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
    
    def create_status_labels(self):
        """Create status information labels"""
        status_grid = ttk.Frame(self.status_frame)
        status_grid.pack(fill='x', padx=10, pady=10)
        
        # Zone status
        ttk.Label(status_grid, text="Zones:").grid(row=0, column=0, sticky='w', padx=5)
        self.zones_label = ttk.Label(status_grid, text="Loading...", foreground='blue')
        self.zones_label.grid(row=0, column=1, sticky='w', padx=5)
        
        # Video status
        ttk.Label(status_grid, text="Video Source:").grid(row=0, column=2, sticky='w', padx=5)
        self.video_label = ttk.Label(status_grid, text=self.config.get("video_source", "Not set"))
        self.video_label.grid(row=0, column=3, sticky='w', padx=5)
        
        # Model status
        ttk.Label(status_grid, text="Model:").grid(row=1, column=0, sticky='w', padx=5)
        self.model_label = ttk.Label(status_grid, text=self.config.get("model_path", "Not set"))
        self.model_label.grid(row=1, column=1, sticky='w', padx=5)
        
        # Log file status
        ttk.Label(status_grid, text="Log File:").grid(row=1, column=2, sticky='w', padx=5)
        self.log_label = ttk.Label(status_grid, text=self.config.get("log_file", "Not set"))
        self.log_label.grid(row=1, column=3, sticky='w', padx=5)
    
    def create_logs_display(self):
        """Create logs display area"""
        # Create treeview for logs
        columns = ('Timestamp', 'ObjectID', 'Zone', 'Event', 'Class')
        self.logs_tree = ttk.Treeview(self.logs_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        for col in columns:
            self.logs_tree.heading(col, text=col)
            self.logs_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.logs_frame, orient='vertical', command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.logs_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Add refresh button
        refresh_frame = ttk.Frame(self.logs_frame)
        refresh_frame.pack(fill='x', pady=5)
        ttk.Button(refresh_frame, text="🔄 Refresh Logs", command=self.refresh_logs).pack(side='right')
    
    def update_status(self):
        """Update status information"""
        # Check zones
        try:
            with open(self.config.get("zones_file", "zones.json"), "r") as f:
                zones_data = json.load(f)
                if isinstance(zones_data, dict):
                    zones_count = len(zones_data.get("zones", []))
                    zones_labels = zones_data.get("labels", [])
                else:
                    zones_count = len(zones_data)
                    zones_labels = [f"Zone {i+1}" for i in range(zones_count)]
            
            self.zones_label.config(text=f"{zones_count} zones: {', '.join(zones_labels[:3])}{'...' if len(zones_labels) > 3 else ''}")
        except FileNotFoundError:
            self.zones_label.config(text="No zones defined", foreground='red')
        
        # Check video file
        video_file = self.config.get("video_source", "video2.mp4")
        if os.path.exists(video_file):
            self.video_label.config(text=video_file, foreground='green')
        else:
            self.video_label.config(text=f"{video_file} (not found)", foreground='red')
        
        # Check model file
        model_file = self.config.get("model_path", "yolov8n.pt")
        if os.path.exists(model_file):
            self.model_label.config(text=model_file, foreground='green')
        else:
            self.model_label.config(text=f"{model_file} (not found)", foreground='red')
        
        # Check log file
        log_file = self.config.get("log_file", "logs.csv")
        if os.path.exists(log_file):
            self.log_label.config(text=log_file, foreground='green')
        else:
            self.log_label.config(text=f"{log_file} (not created yet)", foreground='orange')
    
    def refresh_logs(self):
        """Refresh the logs display"""
        # Clear existing items
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        # Load and display logs
        log_file = self.config.get("log_file", "logs.csv")
        if os.path.exists(log_file):
            try:
                df = pd.read_csv(log_file)
                # Display last 50 entries
                for _, row in df.tail(50).iterrows():
                    self.logs_tree.insert('', 'end', values=(
                        row.get('Timestamp', ''),
                        row.get('ObjectID', ''),
                        row.get('Zone', ''),
                        row.get('Event', ''),
                        row.get('Class', '')
                    ))
            except Exception as e:
                messagebox.showerror("Error", f"Could not load logs: {e}")
    
    def periodic_update(self):
        """Periodically update status and logs"""
        self.update_status()
        self.refresh_logs()
        self.root.after(10000, self.periodic_update)  # Update every 10 seconds
    
    def draw_zones(self):
        """Open zone drawing interface"""
        try:
            subprocess.run([sys.executable, "draw_zones.py"], check=True)
            self.update_status()
            messagebox.showinfo("Success", "Zone drawing completed!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to start zone drawing: {e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "draw_zones.py not found!")
    
    def start_detection(self):
        """Start the detection process"""
        # Check if zones exist
        if not os.path.exists(self.config.get("zones_file", "zones.json")):
            result = messagebox.askyesno("No Zones", 
                                       "No zones have been defined. Would you like to draw zones first?")
            if result:
                self.draw_zones()
                return
        
        # Check if video file exists
        video_file = self.config.get("video_source", "video2.mp4")
        if not os.path.exists(video_file):
            messagebox.showerror("Error", f"Video file not found: {video_file}")
            return
        
        try:
            subprocess.run([sys.executable, "test_yolo.py"], check=True)
            self.refresh_logs()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Detection process failed: {e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "test_yolo.py not found!")
    
    def view_logs(self):
        """Open logs file in default application"""
        log_file = self.config.get("log_file", "logs.csv")
        if os.path.exists(log_file):
            try:
                os.startfile(log_file)
            except AttributeError:
                # For non-Windows systems
                subprocess.run(['xdg-open', log_file])
        else:
            messagebox.showinfo("Info", "No log file found yet. Run detection first.")
    
    def open_logs_folder(self):
        """Open the logs folder"""
        try:
            os.startfile(".")
        except AttributeError:
            # For non-Windows systems
            subprocess.run(['xdg-open', "."])
    
    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings configuration will be implemented in a future version.")
    
    def show_help(self):
        """Show help information"""
        help_text = """
Zone Guard - Surveillance System

Instructions:
1. Draw Zones: Define restricted areas on your video
2. Start Detection: Begin monitoring for intrusions
3. View Logs: Check recorded events

Controls:
- Left Click: Add zone points
- Right Click: Finish zone
- Q: Quit zone drawing
- C: Clear current zone
- R: Reset all zones

Features:
- Real-time object detection
- Zone intrusion alerts
- Event logging
- Video recording (optional)

For more help, check the README file.
        """
        messagebox.showinfo("Help", help_text)

def main():
    root = tk.Tk()
    app = ZoneGuardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
