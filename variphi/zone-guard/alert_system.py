import tkinter as tk
from tkinter import messagebox
import threading
import time
import json
import queue
import os

class AlertSystem:
    def __init__(self):
        self.root = None
        self.alert_queue = queue.Queue()
        self.alert_thread = None
        self.is_running = False
        
        # Load config
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {"alert_enabled": True, "alert_type": "console"}
    
    def start(self):
        """Start the alert system with its own Tkinter root"""
        if not self.is_running:
            self.is_running = True
            self.alert_thread = threading.Thread(target=self._run_alert_loop, daemon=True)
            self.alert_thread.start()
    
    def _run_alert_loop(self):
        """Run the alert loop in a separate thread"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.root.title("Zone Guard Alerts")
        
        # Process alerts
        self._process_alerts()
        
        # Start the Tkinter main loop
        self.root.mainloop()
    
    def _process_alerts(self):
        """Process alerts from the queue"""
        try:
            while not self.alert_queue.empty():
                alert_data = self.alert_queue.get_nowait()
                self._show_alert_dialog(alert_data)
        except queue.Empty:
            pass
        
        # Schedule next check
        if self.is_running:
            self.root.after(100, self._process_alerts)
    
    def _show_alert_dialog(self, alert_data):
        """Show alert dialog in the main thread"""
        message = alert_data['message']
        alert_type = alert_data['type']
        
        if alert_type == "warning":
            messagebox.showwarning("Zone Intrusion Alert", message)
        elif alert_type == "info":
            messagebox.showinfo("Zone Guard Info", message)
        elif alert_type == "error":
            messagebox.showerror("Zone Guard Error", message)
    
    def show_alert(self, message, alert_type="warning"):
        """Queue an alert to be shown"""
        if not self.config.get("alert_enabled", True):
            return
        
        # Start the alert system if not running
        if not self.is_running:
            self.start()
        
        # Add alert to queue
        self.alert_queue.put({
            'message': message,
            'type': alert_type
        })
    
    def show_entry_alert(self, object_id, zone_name):
        """Show alert when object enters zone"""
        message = f"🚨 ALERT: Object {object_id} entered {zone_name}"
        self.show_alert(message, "warning")
    
    def show_exit_alert(self, object_id, zone_name):
        """Show alert when object exits zone"""
        message = f"ℹ️ Object {object_id} exited {zone_name}"
        self.show_alert(message, "info")
    
    def show_console_alert(self, message, alert_type="info"):
        """Show alert in console (fallback when GUI is not available)"""
        if not self.config.get("alert_enabled", True):
            return
        
        timestamp = time.strftime("%H:%M:%S")
        if alert_type == "warning":
            print(f"[{timestamp}] ⚠️  {message}")
        elif alert_type == "error":
            print(f"[{timestamp}] ❌ {message}")
        else:
            print(f"[{timestamp}] ℹ️  {message}")
    
    def cleanup(self):
        """Clean up the alert system"""
        self.is_running = False
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass

# Alternative alert system using console output (no threading issues)
class ConsoleAlertSystem:
    def __init__(self):
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {"alert_enabled": True, "alert_type": "console"}
    
    def show_alert(self, message, alert_type="warning"):
        """Show alert in console"""
        if not self.config.get("alert_enabled", True):
            return
        
        timestamp = time.strftime("%H:%M:%S")
        if alert_type == "warning":
            print(f"[{timestamp}] 🚨 ALERT: {message}")
        elif alert_type == "error":
            print(f"[{timestamp}] ❌ ERROR: {message}")
        else:
            print(f"[{timestamp}] ℹ️  INFO: {message}")
    
    def show_entry_alert(self, object_id, zone_name):
        """Show alert when object enters zone"""
        message = f"Object {object_id} entered {zone_name}"
        self.show_alert(message, "warning")
    
    def show_exit_alert(self, object_id, zone_name):
        """Show alert when object exits zone"""
        message = f"Object {object_id} exited {zone_name}"
        self.show_alert(message, "info")
    
    def cleanup(self):
        """Clean up (nothing to do for console alerts)"""
        pass

def create_alert_system():
    """Create the appropriate alert system based on configuration"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        alert_type = config.get("alert_type", "console")
    except FileNotFoundError:
        alert_type = "console"
    
    if alert_type == "gui":
        return AlertSystem()
    else:
        return ConsoleAlertSystem()

# Global alert system instance
alert_system = create_alert_system()
