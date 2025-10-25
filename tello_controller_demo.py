#!/usr/bin/env python3
"""
Tello Drone Controller - Demo Mode
A demo version that can run without a real Tello drone for testing the GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import numpy as np
from PIL import Image, ImageTk
import pygame
import random

class VirtualJoystick:
    """Virtual joystick widget for drone control"""
    
    def __init__(self, parent, size=200, callback=None):
        self.size = size
        self.center = size // 2
        self.callback = callback
        
        self.canvas = tk.Canvas(parent, width=size, height=size, bg='black')
        self.canvas.pack(padx=5, pady=5)
        
        # Draw joystick background
        self.canvas.create_oval(10, 10, size-10, size-10, outline='white', width=2)
        self.canvas.create_oval(self.center-5, self.center-5, self.center+5, self.center+5, 
                               fill='red', outline='white', width=2, tags='stick')
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        
        self.x_pos = 0  # -100 to 100
        self.y_pos = 0  # -100 to 100
        
    def on_click(self, event):
        self.update_position(event.x, event.y)
        
    def on_drag(self, event):
        self.update_position(event.x, event.y)
        
    def on_release(self, event):
        # Return to center
        self.x_pos = 0
        self.y_pos = 0
        self.canvas.coords('stick', self.center-5, self.center-5, self.center+5, self.center+5)
        if self.callback:
            self.callback(0, 0)
            
    def update_position(self, x, y):
        # Calculate relative position
        rel_x = x - self.center
        rel_y = y - self.center
        
        # Limit to circle boundary
        distance = np.sqrt(rel_x**2 + rel_y**2)
        max_distance = self.center - 15
        
        if distance > max_distance:
            rel_x = rel_x * max_distance / distance
            rel_y = rel_y * max_distance / distance
            
        # Update stick position
        stick_x = self.center + rel_x
        stick_y = self.center + rel_y
        self.canvas.coords('stick', stick_x-5, stick_y-5, stick_x+5, stick_y+5)
        
        # Calculate percentage values (-100 to 100)
        self.x_pos = int((rel_x / max_distance) * 100)
        self.y_pos = int(-(rel_y / max_distance) * 100)  # Invert Y axis
        
        if self.callback:
            self.callback(self.x_pos, self.y_pos)

class TelloControllerDemo:
    """Demo version of Tello drone controller"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tello Drone Controller - Demo Mode")
        self.root.geometry("1200x800")
        
        # Demo state
        self.connected = False
        self.battery = 85
        self.height = 0
        self.flight_time = 0
        self.temperature = 25
        self.flying = False
        
        # Control values
        self.movement_commands = {
            'left_right': 0,
            'forward_back': 0,
            'up_down': 0,
            'yaw': 0
        }
        
        self.setup_ui()
        self.setup_pygame()
        
    def setup_pygame(self):
        """Initialize pygame for gamepad support"""
        try:
            pygame.init()
            pygame.joystick.init()
            self.check_gamepad()
        except Exception as e:
            print(f"Pygame initialization failed: {e}")
            
    def check_gamepad(self):
        """Check for connected gamepads"""
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            self.gamepad_name.set(f"Gamepad: {self.gamepad.get_name()}")
        else:
            self.gamepad_name.set("No gamepad detected")
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frames
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
        
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(left_frame, text="Connection")
        conn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(conn_frame, text="Connect (Demo)", command=self.connect_drone).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_drone).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.connection_status = tk.StringVar(value="Disconnected")
        ttk.Label(conn_frame, textvariable=self.connection_status).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(left_frame, text="Drone Status (Demo)")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.battery_level = tk.StringVar(value="Battery: --")
        self.flight_time_var = tk.StringVar(value="Flight Time: --")
        self.height_var = tk.StringVar(value="Height: --")
        self.temperature_var = tk.StringVar(value="Temp: --")
        
        ttk.Label(status_frame, textvariable=self.battery_level).pack(anchor=tk.W)
        ttk.Label(status_frame, textvariable=self.flight_time_var).pack(anchor=tk.W)
        ttk.Label(status_frame, textvariable=self.height_var).pack(anchor=tk.W)
        ttk.Label(status_frame, textvariable=self.temperature_var).pack(anchor=tk.W)
        
        # Control frame
        control_frame = ttk.LabelFrame(left_frame, text="Flight Controls")
        control_frame.pack(fill=tk.X, pady=5)
        
        # Basic flight buttons
        ttk.Button(control_frame, text="Takeoff", command=self.takeoff).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Land", command=self.land).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Emergency", command=self.emergency_stop).pack(fill=tk.X, pady=2)
            
        # Speed control
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=50)
        speed_scale = ttk.Scale(speed_frame, from_=10, to=100, variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(speed_frame, textvariable=self.speed_var).pack(side=tk.LEFT)
        
        # Virtual joysticks frame
        joystick_frame = ttk.LabelFrame(left_frame, text="Virtual Controls")
        joystick_frame.pack(fill=tk.X, pady=5)
        
        # Left joystick (movement)
        left_joy_frame = ttk.Frame(joystick_frame)
        left_joy_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(left_joy_frame, text="Movement").pack()
        self.left_joystick = VirtualJoystick(left_joy_frame, callback=self.on_movement_joystick)
        
        # Right joystick (rotation/altitude)
        right_joy_frame = ttk.Frame(joystick_frame)
        right_joy_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(right_joy_frame, text="Rotation/Altitude").pack()
        self.right_joystick = VirtualJoystick(right_joy_frame, callback=self.on_rotation_joystick)
        
        # Gamepad status
        gamepad_frame = ttk.Frame(left_frame)
        gamepad_frame.pack(fill=tk.X, pady=5)
        self.gamepad_name = tk.StringVar(value="No gamepad detected")
        ttk.Label(gamepad_frame, textvariable=self.gamepad_name).pack()
        
        # Video frame (demo)
        video_frame = ttk.LabelFrame(right_frame, text="Video Stream (Demo)")
        video_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.video_label = ttk.Label(video_frame, text="Demo Mode - No Real Video")
        self.video_label.pack(expand=True)
        
        # Command shell frame
        shell_frame = ttk.LabelFrame(right_frame, text="Command Shell (Demo)")
        shell_frame.pack(fill=tk.X, pady=5)
        
        # Command output
        self.command_output = scrolledtext.ScrolledText(shell_frame, height=8, width=50)
        self.command_output.pack(fill=tk.X, pady=2)
        
        # Command input
        cmd_input_frame = ttk.Frame(shell_frame)
        cmd_input_frame.pack(fill=tk.X, pady=2)
        
        self.command_entry = ttk.Entry(cmd_input_frame)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.command_entry.bind('<Return>', self.send_command)
        
        ttk.Button(cmd_input_frame, text="Send", command=self.send_command).pack(side=tk.RIGHT)
        
        # Add demo info
        self.log_message("=== Tello Command Shell - Demo Mode ===")
        self.log_message("This is a demo version that simulates drone responses")
        self.log_message("Try commands like: battery?, height?, up 50, flip f")
        
        # Start demo video
        self.start_demo_video()
        
    def on_movement_joystick(self, x, y):
        """Handle movement joystick input"""
        self.movement_commands['left_right'] = x
        self.movement_commands['forward_back'] = y
        self.log_message(f"Movement: L/R={x}, F/B={y}")
        
    def on_rotation_joystick(self, x, y):
        """Handle rotation/altitude joystick input"""
        self.movement_commands['yaw'] = x
        self.movement_commands['up_down'] = y
        self.log_message(f"Rotation/Alt: Yaw={x}, U/D={y}")
        
    def connect_drone(self):
        """Simulate drone connection"""
        self.connected = True
        self.connection_status.set("Connected (Demo)")
        self.log_message("Connected to simulated Tello drone")
        self.start_status_monitoring()
        
    def disconnect_drone(self):
        """Simulate drone disconnection"""
        self.connected = False
        self.flying = False
        self.connection_status.set("Disconnected")
        self.log_message("Disconnected from simulated drone")
        
    def start_demo_video(self):
        """Create a demo video pattern"""
        def create_demo_frame():
            # Create a colorful pattern
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Add some moving patterns
            t = time.time()
            for i in range(0, 640, 20):
                for j in range(0, 480, 20):
                    color_r = int(128 + 127 * np.sin(t + i * 0.01))
                    color_g = int(128 + 127 * np.sin(t + j * 0.01))
                    color_b = int(128 + 127 * np.sin(t + (i + j) * 0.005))
                    frame[j:j+10, i:i+10] = [color_r, color_g, color_b]
            
            # Add text overlay
            cv2_available = False
            try:
                import cv2
                cv2.putText(frame, "DEMO MODE", (250, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
                cv2_available = True
            except ImportError:
                pass
            
            return frame
            
        def video_loop():
            while True:
                try:
                    frame = create_demo_frame()
                    image = Image.fromarray(frame)
                    photo = ImageTk.PhotoImage(image)
                    
                    self.root.after(0, lambda: self.update_video_frame(photo))
                    time.sleep(0.033)  # ~30 FPS
                except Exception as e:
                    print(f"Demo video error: {e}")
                    time.sleep(0.1)
                    
        threading.Thread(target=video_loop, daemon=True).start()
        
    def update_video_frame(self, photo):
        """Update video frame in GUI"""
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo
        
    def start_status_monitoring(self):
        """Simulate status monitoring"""
        def status_loop():
            while self.connected:
                try:
                    # Simulate battery drain
                    if self.flying and self.battery > 0:
                        self.battery = max(0, self.battery - random.uniform(0.1, 0.3))
                        
                    # Simulate flight time
                    if self.flying:
                        self.flight_time += 2
                        
                    # Simulate height changes
                    if self.flying:
                        self.height += random.uniform(-2, 2)
                        self.height = max(0, min(500, self.height))
                        
                    # Simulate temperature
                    self.temperature += random.uniform(-0.5, 0.5)
                    self.temperature = max(15, min(35, self.temperature))
                    
                    self.root.after(0, lambda: self.update_status())
                    
                except Exception as e:
                    print(f"Status monitoring error: {e}")
                    
                time.sleep(2)
                
        threading.Thread(target=status_loop, daemon=True).start()
        
    def update_status(self):
        """Update status display"""
        self.battery_level.set(f"Battery: {self.battery:.1f}%")
        self.height_var.set(f"Height: {self.height:.1f}cm")
        self.flight_time_var.set(f"Flight Time: {self.flight_time}s")
        self.temperature_var.set(f"Temp: {self.temperature:.1f}°C")
        
    def takeoff(self):
        """Simulate takeoff"""
        if self.connected:
            self.flying = True
            self.height = 80 + random.uniform(-10, 10)
            self.log_message("Takeoff command sent (simulated)")
        
    def land(self):
        """Simulate landing"""
        if self.connected:
            self.flying = False
            self.height = 0
            self.log_message("Land command sent (simulated)")
        
    def emergency_stop(self):
        """Simulate emergency stop"""
        if self.connected:
            self.flying = False
            self.height = 0
            self.log_message("EMERGENCY STOP! (simulated)")
        
    def send_command(self, event=None):
        """Process demo commands"""
        command = self.command_entry.get().strip()
        if not command:
            return
            
        self.command_entry.delete(0, tk.END)
        self.log_message(f"> {command}")
        
        if not self.connected:
            self.log_message("Error: Not connected to drone")
            return
            
        # Parse command
        parts = command.lower().split()
        cmd = parts[0]
        
        if cmd == "battery?":
            self.log_message(f"Battery: {self.battery:.1f}%")
        elif cmd == "speed?":
            self.log_message(f"Speed: {self.speed_var.get()}")
        elif cmd == "height?":
            self.log_message(f"Height: {self.height:.1f}cm")
        elif cmd == "flip" and len(parts) > 1:
            direction = parts[1]
            if direction in ['f', 'b', 'l', 'r']:
                self.log_message(f"Flip {direction} executed (simulated)")
            else:
                self.log_message("Invalid flip direction")
        elif cmd in ["up", "down", "forward", "back", "left", "right", "cw", "ccw"]:
            if len(parts) > 1:
                try:
                    distance = int(parts[1])
                    if cmd in ["up", "down"]:
                        if cmd == "up":
                            self.height += distance
                        else:
                            self.height = max(0, self.height - distance)
                    self.log_message(f"Command executed (simulated): {command}")
                except ValueError:
                    self.log_message("Invalid distance value")
            else:
                self.log_message("Missing distance parameter")
        else:
            self.log_message(f"Unknown command: {command} (simulated response: OK)")
        
    def log_message(self, message):
        """Add message to command output"""
        self.command_output.insert(tk.END, f"{message}\n")
        self.command_output.see(tk.END)
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting Tello Controller Demo Mode...")
    print("This demo version works without a real Tello drone.")
    app = TelloControllerDemo()
    app.run()