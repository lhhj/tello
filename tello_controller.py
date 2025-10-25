#!/usr/bin/env python3
"""
Tello Drone Controller with GUI
A comprehensive Python application for controlling DJI Tello drone with:
- Video streaming
- Virtual joystick controls
- Command shell
- Real-time status monitoring
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import cv2
import numpy as np
from PIL import Image, ImageTk
import pygame
from djitellopy import Tello
import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class TelloController:
    """Main Tello drone controller application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tello Drone Controller")
        self.root.geometry("1200x800")
        
        # Tello drone instance
        self.tello = None
        self.connected = False
        self.video_thread = None
        self.command_thread = None
        self.stop_video = False
        
        # Control values
        self.speed = 50
        self.movement_commands = {
            'left_right': 0,  # -100 to 100 (left/right)
            'forward_back': 0,  # -100 to 100 (forward/back)
            'up_down': 0,     # -100 to 100 (up/down)
            'yaw': 0          # -100 to 100 (rotate left/right)
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
            logger.warning(f"Pygame initialization failed: {e}")
            
    def check_gamepad(self):
        """Check for connected gamepads"""
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            self.gamepad_name.set(f"Gamepad: {self.gamepad.get_name()}")
            self.start_gamepad_thread()
        else:
            self.gamepad_name.set("No gamepad detected")
            
    def start_gamepad_thread(self):
        """Start gamepad monitoring thread"""
        def gamepad_loop():
            while self.connected:
                try:
                    pygame.event.pump()
                    if hasattr(self, 'gamepad'):
                        # Read gamepad inputs
                        left_x = self.gamepad.get_axis(0) * 100
                        left_y = -self.gamepad.get_axis(1) * 100
                        right_x = self.gamepad.get_axis(3) * 100
                        right_y = -self.gamepad.get_axis(4) * 100
                        
                        # Update movement commands
                        self.movement_commands['left_right'] = int(left_x)
                        self.movement_commands['forward_back'] = int(left_y)
                        self.movement_commands['yaw'] = int(right_x)
                        self.movement_commands['up_down'] = int(right_y)
                        
                        # Send RC commands
                        if self.connected and self.tello:
                            self.send_rc_command()
                            
                    time.sleep(0.05)  # 20Hz update rate
                except Exception as e:
                    logger.error(f"Gamepad error: {e}")
                    time.sleep(0.1)
                    
        if hasattr(self, 'gamepad'):
            threading.Thread(target=gamepad_loop, daemon=True).start()
        
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
        
        ttk.Button(conn_frame, text="Connect", command=self.connect_drone).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_drone).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.connection_status = tk.StringVar(value="Disconnected")
        ttk.Label(conn_frame, textvariable=self.connection_status).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(left_frame, text="Drone Status")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.battery_level = tk.StringVar(value="Battery: --")
        self.flight_time = tk.StringVar(value="Flight Time: --")
        self.height = tk.StringVar(value="Height: --")
        self.temperature = tk.StringVar(value="Temp: --")
        
        ttk.Label(status_frame, textvariable=self.battery_level).pack(anchor=tk.W)
        ttk.Label(status_frame, textvariable=self.flight_time).pack(anchor=tk.W)
        ttk.Label(status_frame, textvariable=self.height).pack(anchor=tk.W)
        ttk.Label(status_frame, textvariable=self.temperature).pack(anchor=tk.W)
        
        # Control frame
        control_frame = ttk.LabelFrame(left_frame, text="Flight Controls")
        control_frame.pack(fill=tk.X, pady=5)
        
        # Basic flight buttons
        flight_buttons = [
            ("Takeoff", self.takeoff),
            ("Land", self.land),
            ("Emergency", self.emergency_stop)
        ]
        
        for text, command in flight_buttons:
            ttk.Button(control_frame, text=text, command=command).pack(fill=tk.X, pady=2)
            
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
        
        # Video frame
        video_frame = ttk.LabelFrame(right_frame, text="Video Stream")
        video_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.video_label = ttk.Label(video_frame, text="No video signal")
        self.video_label.pack(expand=True)
        
        # Command shell frame
        shell_frame = ttk.LabelFrame(right_frame, text="Command Shell")
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
        
        # Add some sample commands
        self.log_message("=== Tello Command Shell ===")
        self.log_message("Sample commands:")
        self.log_message("  battery? - Get battery level")
        self.log_message("  speed? - Get current speed")
        self.log_message("  height? - Get current height")
        self.log_message("  flip f - Flip forward")
        self.log_message("  flip b - Flip backward")
        self.log_message("  flip l - Flip left")
        self.log_message("  flip r - Flip right")
        self.log_message("  up 50 - Move up 50cm")
        self.log_message("  down 50 - Move down 50cm")
        self.log_message("  forward 50 - Move forward 50cm")
        self.log_message("  back 50 - Move backward 50cm")
        self.log_message("  left 50 - Move left 50cm")
        self.log_message("  right 50 - Move right 50cm")
        self.log_message("  cw 90 - Rotate clockwise 90 degrees")
        self.log_message("  ccw 90 - Rotate counter-clockwise 90 degrees")
        
    def on_movement_joystick(self, x, y):
        """Handle movement joystick input"""
        self.movement_commands['left_right'] = x
        self.movement_commands['forward_back'] = y
        if self.connected:
            self.send_rc_command()
            
    def on_rotation_joystick(self, x, y):
        """Handle rotation/altitude joystick input"""
        self.movement_commands['yaw'] = x
        self.movement_commands['up_down'] = y
        if self.connected:
            self.send_rc_command()
            
    def send_rc_command(self):
        """Send RC control command to drone"""
        try:
            if self.tello and self.connected:
                self.tello.send_rc_control(
                    self.movement_commands['left_right'],
                    self.movement_commands['forward_back'],
                    self.movement_commands['up_down'],
                    self.movement_commands['yaw']
                )
        except Exception as e:
            logger.error(f"RC command error: {e}")
            
    def connect_drone(self):
        """Connect to Tello drone"""
        try:
            self.connection_status.set("Connecting...")
            self.log_message("Attempting to connect to Tello drone...")
            
            self.tello = Tello()
            self.tello.connect()
            
            # Give drone time to initialize
            time.sleep(1)
            
            # Test connection with battery check
            try:
                battery = self.tello.get_battery()
                self.connected = True
                self.connection_status.set("Connected")
                
                self.log_message(f"Connected to Tello drone (Battery: {battery}%)")
                
                # Start video stream
                self.start_video_stream()
                
                # Start status monitoring
                self.start_status_monitoring()
                
                # Check for gamepad again
                self.check_gamepad()
                
            except Exception as battery_error:
                # Connection succeeded but battery check failed
                self.connected = True
                self.connection_status.set("Connected (Limited)")
                self.log_message("Connected to Tello drone (status monitoring limited)")
                self.log_message(f"Note: {battery_error}")
                
                # Still try to start video stream
                self.start_video_stream()
                
        except Exception as e:
            self.connected = False
            error_msg = str(e)
            if "state packet" in error_msg.lower():
                self.connection_status.set("Connected (No Status)")
                self.log_message("Connected but status monitoring unavailable")
                self.log_message("Basic flight controls should still work")
                self.connected = True
                # Try to start video stream anyway
                self.start_video_stream()
            else:
                self.connection_status.set("Connection Failed")
                self.log_message(f"Connection failed: {e}")
                messagebox.showerror("Connection Error", f"Failed to connect to Tello drone:\n{e}")
            
    def disconnect_drone(self):
        """Disconnect from Tello drone"""
        try:
            self.connected = False
            self.stop_video = True
            
            if self.tello:
                # Stop any movement
                self.tello.send_rc_control(0, 0, 0, 0)
                time.sleep(0.1)
                
            self.connection_status.set("Disconnected")
            self.log_message("Disconnected from Tello drone")
            
            # Clear video
            self.video_label.config(image='', text="No video signal")
            
        except Exception as e:
            self.log_message(f"Disconnect error: {e}")
            
    def start_video_stream(self):
        """Start video streaming thread with corrected UDP address"""
        if not self.tello:
            return
            
        try:
            self.tello.streamon()
            self.stop_video = False
            
            def video_loop():
                retry_count = 0
                max_retries = 5
                
                # Try different video stream approaches
                video_sources = [
                    f"udp://192.168.10.1:11111",  # Correct Tello IP
                    f"udp://@192.168.10.1:11111", # Alternative format
                    f"udp://0.0.0.0:11111"        # Library default (fallback)
                ]
                
                cap = None
                for video_url in video_sources:
                    try:
                        self.log_message(f"Trying video source: {video_url}")
                        cap = cv2.VideoCapture(video_url)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
                        
                        # Test if we can read a frame
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            self.log_message(f"✓ Video stream working: {video_url}")
                            break
                        else:
                            cap.release()
                            cap = None
                    except Exception as e:
                        self.log_message(f"Video source {video_url} failed: {e}")
                        if cap:
                            cap.release()
                        cap = None
                
                if cap is None:
                    self.log_message("All video sources failed. Using djitellopy default method.")
                    # Fallback to original djitellopy method
                    while not self.stop_video and self.connected and retry_count < max_retries:
                        try:
                            frame = self.tello.get_frame_read().frame
                            if frame is not None:
                                # Resize frame for display
                                frame = cv2.resize(frame, (640, 480))
                                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                
                                # Convert to PIL Image and then to PhotoImage
                                image = Image.fromarray(frame)
                                photo = ImageTk.PhotoImage(image)
                                
                                # Update GUI (must be done in main thread)
                                self.root.after(0, lambda: self.update_video_frame(photo))
                                retry_count = 0  # Reset retry count on success
                                
                        except Exception as e:
                            retry_count += 1
                            if retry_count <= 3:  # Only log first few errors
                                logger.error(f"Video stream error: {e}")
                            if retry_count >= max_retries:
                                logger.info("Video stream disabled due to repeated errors")
                                self.root.after(0, lambda: self.video_label.config(text="Video disabled (flight controls work)"))
                                break
                            time.sleep(0.1)
                else:
                    # Use direct OpenCV capture
                    self.log_message("Using direct OpenCV video capture")
                    while not self.stop_video and self.connected:
                        try:
                            ret, frame = cap.read()
                            if ret and frame is not None:
                                # Resize frame for display
                                frame = cv2.resize(frame, (640, 480))
                                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                
                                # Convert to PIL Image and then to PhotoImage
                                image = Image.fromarray(frame)
                                photo = ImageTk.PhotoImage(image)
                                
                                # Update GUI (must be done in main thread)
                                self.root.after(0, lambda: self.update_video_frame(photo))
                            else:
                                time.sleep(0.033)  # ~30 FPS
                        except Exception as e:
                            logger.error(f"OpenCV video error: {e}")
                            time.sleep(0.1)
                    
                    if cap:
                        cap.release()
                        
                if self.tello and self.connected:
                    try:
                        self.tello.streamoff()
                    except:
                        pass  # Ignore streamoff errors
                
            self.video_thread = threading.Thread(target=video_loop, daemon=True)
            self.video_thread.start()
            
        except Exception as e:
            self.log_message(f"Video stream error: {e}")
            self.log_message("Flight controls still work without video")
            
    def update_video_frame(self, photo):
        """Update video frame in GUI"""
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo  # Keep a reference
        
    def start_status_monitoring(self):
        """Start status monitoring thread"""
        def status_loop():
            while self.connected:
                try:
                    if self.tello:
                        battery = self.tello.get_battery()
                        height = self.tello.get_height()
                        flight_time = self.tello.get_flight_time()
                        temp = self.tello.get_temperature()
                        
                        # Update status in main thread
                        self.root.after(0, lambda: self.update_status(battery, height, flight_time, temp))
                        
                except Exception as e:
                    logger.error(f"Status monitoring error: {e}")
                    
                time.sleep(2)  # Update every 2 seconds
                
        threading.Thread(target=status_loop, daemon=True).start()
        
    def update_status(self, battery, height, flight_time, temp):
        """Update status display"""
        self.battery_level.set(f"Battery: {battery}%")
        self.height.set(f"Height: {height}cm")
        self.flight_time.set(f"Flight Time: {flight_time}s")
        self.temperature.set(f"Temp: {temp}°C")
        
    def takeoff(self):
        """Takeoff command"""
        try:
            if self.tello and self.connected:
                self.tello.takeoff()
                self.log_message("Takeoff command sent")
        except Exception as e:
            self.log_message(f"Takeoff error: {e}")
            
    def land(self):
        """Land command"""
        try:
            if self.tello and self.connected:
                self.tello.land()
                self.log_message("Land command sent")
        except Exception as e:
            self.log_message(f"Land error: {e}")
            
    def emergency_stop(self):
        """Emergency stop"""
        try:
            if self.tello and self.connected:
                self.tello.emergency()
                self.log_message("EMERGENCY STOP!")
        except Exception as e:
            self.log_message(f"Emergency stop error: {e}")
            
    def send_command(self, event=None):
        """Send custom command to drone"""
        command = self.command_entry.get().strip()
        if not command:
            return
            
        self.command_entry.delete(0, tk.END)
        self.log_message(f"> {command}")
        
        if not self.connected or not self.tello:
            self.log_message("Error: Not connected to drone")
            return
            
        try:
            # Parse and execute command
            parts = command.lower().split()
            cmd = parts[0]
            
            if cmd == "battery?":
                result = self.tello.get_battery()
                self.log_message(f"Battery: {result}%")
            elif cmd == "speed?":
                result = self.tello.get_speed()
                self.log_message(f"Speed: {result}")
            elif cmd == "height?":
                result = self.tello.get_height()
                self.log_message(f"Height: {result}cm")
            elif cmd == "flip" and len(parts) > 1:
                direction = parts[1]
                if direction in ['f', 'b', 'l', 'r']:
                    self.tello.flip(direction)
                    self.log_message(f"Flip {direction} executed")
                else:
                    self.log_message("Invalid flip direction (use f, b, l, r)")
            elif cmd in ["up", "down", "forward", "back", "left", "right", "cw", "ccw"]:
                if len(parts) > 1:
                    try:
                        distance = int(parts[1])
                        if cmd == "up":
                            self.tello.move_up(distance)
                        elif cmd == "down":
                            self.tello.move_down(distance)
                        elif cmd == "forward":
                            self.tello.move_forward(distance)
                        elif cmd == "back":
                            self.tello.move_back(distance)
                        elif cmd == "left":
                            self.tello.move_left(distance)
                        elif cmd == "right":
                            self.tello.move_right(distance)
                        elif cmd == "cw":
                            self.tello.rotate_clockwise(distance)
                        elif cmd == "ccw":
                            self.tello.rotate_counter_clockwise(distance)
                        self.log_message(f"Command executed: {command}")
                    except ValueError:
                        self.log_message("Invalid distance value")
                else:
                    self.log_message("Missing distance parameter")
            else:
                # Try to send raw command
                result = self.tello.send_control_command(command)
                self.log_message(f"Result: {result}")
                
        except Exception as e:
            self.log_message(f"Command error: {e}")
            
    def log_message(self, message):
        """Add message to command output"""
        self.command_output.insert(tk.END, f"{message}\n")
        self.command_output.see(tk.END)
        
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle application closing"""
        if self.connected:
            self.disconnect_drone()
        self.root.destroy()

if __name__ == "__main__":
    app = TelloController()
    app.run()