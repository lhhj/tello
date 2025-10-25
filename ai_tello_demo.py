#!/usr/bin/env python3
"""
AI Tello Controller Demo - Lightweight Version
Demonstrates AI-powered drone control concepts without requiring heavy ML dependencies.
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
import logging
import json
import random
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockVLMClient:
    """Mock VLM client for demonstration purposes"""
    
    def __init__(self):
        self.last_analysis = None
        self.analysis_history = []
        
        # Simulated responses based on random scenarios
        self.scenarios = [
            "I can see an open indoor space with good lighting. The area appears clear with no immediate obstacles.",
            "There's a wall visible in the distance. I recommend maintaining safe distance from obstacles.",
            "I detect what appears to be furniture or objects in the room. Navigate carefully around them.",
            "The view shows a clear path ahead with plenty of space for maneuvering.",
            "I can see some people in the background. Maintain safe distance and fly responsibly.",
            "The lighting conditions are good for flight. The area appears suitable for drone operations.",
            "I notice some ceiling features above. Be mindful of altitude limits indoors.",
            "The floor appears to have a clear pattern. This could be useful for navigation reference."
        ]
        
    def analyze_frame(self, frame, instruction="Describe what you see"):
        """Simulate AI analysis of video frame"""
        # Simulate processing time
        time.sleep(0.5)
        
        # Generate contextual response based on instruction
        if "obstacle" in instruction.lower():
            responses = [
                "I can see the room layout. There appear to be some objects that could be obstacles on the sides.",
                "The view shows a relatively clear central area with potential obstacles near the edges.",
                "I detect some vertical structures that could be obstacles. Recommend cautious navigation."
            ]
        elif "person" in instruction.lower() or "people" in instruction.lower():
            responses = [
                "I can detect what may be people in the background. Maintaining safe distance is recommended.",
                "There appear to be some human figures in the view. Flying responsibly around people.",
                "I notice some movement that could be people. Exercise caution during flight operations."
            ]
        elif "explore" in instruction.lower():
            responses = [
                "The area looks suitable for exploration. I recommend starting with gentle movements.",
                "Good visibility for exploration. The space appears to have multiple interesting areas to investigate.",
                "This environment seems safe for exploration flights with appropriate caution."
            ]
        else:
            responses = self.scenarios
            
        analysis = random.choice(responses)
        
        # Store analysis
        self.last_analysis = {
            'timestamp': datetime.now(),
            'instruction': instruction,
            'analysis': analysis
        }
        self.analysis_history.append(self.last_analysis)
        
        # Keep only last 10 analyses
        if len(self.analysis_history) > 10:
            self.analysis_history.pop(0)
            
        return analysis
    
    def parse_flight_instruction(self, analysis_text, user_instruction):
        """Parse natural language instruction into flight commands"""
        instruction_lower = user_instruction.lower()
        analysis_lower = analysis_text.lower() if analysis_text else ""
        
        commands = []
        
        # Basic movement commands
        if any(word in instruction_lower for word in ['forward', 'ahead', 'move forward']):
            distance = self.extract_distance(instruction_lower, default=50)
            commands.append(f"forward {distance}")
            
        elif any(word in instruction_lower for word in ['back', 'backward', 'retreat']):
            distance = self.extract_distance(instruction_lower, default=50)
            commands.append(f"back {distance}")
            
        elif any(word in instruction_lower for word in ['left']):
            distance = self.extract_distance(instruction_lower, default=50)
            commands.append(f"left {distance}")
            
        elif any(word in instruction_lower for word in ['right']):
            distance = self.extract_distance(instruction_lower, default=50)
            commands.append(f"right {distance}")
            
        elif any(word in instruction_lower for word in ['up', 'higher', 'rise']):
            distance = self.extract_distance(instruction_lower, default=50)
            commands.append(f"up {distance}")
            
        elif any(word in instruction_lower for word in ['down', 'lower', 'descend']):
            distance = self.extract_distance(instruction_lower, default=50)
            commands.append(f"down {distance}")
        
        # Rotation commands
        elif any(word in instruction_lower for word in ['turn left', 'rotate left']):
            angle = self.extract_angle(instruction_lower, default=90)
            commands.append(f"ccw {angle}")
            
        elif any(word in instruction_lower for word in ['turn right', 'rotate right']):
            angle = self.extract_angle(instruction_lower, default=90)
            commands.append(f"cw {angle}")
            
        elif any(word in instruction_lower for word in ['spin', 'turn around']):
            commands.append("cw 180")
        
        # Flight control commands
        elif any(word in instruction_lower for word in ['takeoff', 'take off', 'launch']):
            commands.append("takeoff")
            
        elif any(word in instruction_lower for word in ['land', 'landing']):
            commands.append("land")
            
        elif any(word in instruction_lower for word in ['flip']):
            if 'forward' in instruction_lower:
                commands.append("flip f")
            elif 'back' in instruction_lower:
                commands.append("flip b")
            elif 'left' in instruction_lower:
                commands.append("flip l")
            elif 'right' in instruction_lower:
                commands.append("flip r")
            else:
                commands.append("flip f")  # Default forward flip
        
        # Context-aware commands based on "vision"
        elif any(word in instruction_lower for word in ['follow', 'track', 'chase']):
            commands.append("# Following detected target")
            commands.append("forward 30")
            
        elif any(word in instruction_lower for word in ['avoid', 'dodge']):
            commands.append("# Avoiding detected obstacle")
            commands.append("back 50")
        
        elif any(word in instruction_lower for word in ['explore', 'look around']):
            commands.extend([
                "# Exploration sequence",
                "cw 90",
                "forward 30",
                "cw 90",
                "forward 30"
            ])
        
        elif any(word in instruction_lower for word in ['patrol']):
            commands.extend([
                "# Patrol pattern",
                "forward 50",
                "cw 90",
                "forward 50",
                "cw 90"
            ])
        
        return commands
    
    def extract_distance(self, text, default=50):
        """Extract distance from text (in cm)"""
        import re
        
        # Look for numbers followed by distance units
        patterns = [
            r'(\d+)\s*(?:cm|centimeter|centimetre)',
            r'(\d+)\s*(?:m|meter|metre)',
            r'(\d+)\s*(?:ft|foot|feet)',
            r'(\d+)\s*(?:unit|step)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                distance = int(match.group(1))
                if 'm' in pattern or 'meter' in pattern:
                    distance *= 100  # Convert meters to cm
                elif 'ft' in pattern or 'foot' in pattern or 'feet' in pattern:
                    distance *= 30   # Convert feet to cm (approximate)
                return min(max(distance, 20), 500)  # Clamp to Tello limits
        
        # Look for just numbers
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            distance = int(numbers[0])
            return min(max(distance, 20), 500)
        
        return default
    
    def extract_angle(self, text, default=90):
        """Extract angle from text (in degrees)"""
        import re
        
        # Look for numbers followed by angle units
        patterns = [
            r'(\d+)\s*(?:degree|degrees|deg|°)',
            r'(\d+)\s*(?:turn|rotation)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                angle = int(match.group(1))
                return min(max(angle, 1), 360)  # Clamp to valid range
        
        # Look for just numbers
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            angle = int(numbers[0])
            return min(max(angle, 1), 360)
        
        return default

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

class AITelloDemoController:
    """AI-Powered Tello drone controller demonstration"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Tello Controller Demo - StreamVLM Simulation")
        self.root.geometry("1400x900")
        
        # Tello drone instance
        self.tello = None
        self.connected = False
        self.demo_mode = True  # Start in demo mode
        self.video_thread = None
        self.ai_thread = None
        self.stop_video = False
        self.current_frame = None
        
        # Mock VLM client
        self.vlm_client = MockVLMClient()
        self.auto_analysis = False
        self.analysis_interval = 3  # seconds
        
        # Control values
        self.movement_commands = {
            'left_right': 0,
            'forward_back': 0,
            'up_down': 0,
            'yaw': 0
        }
        
        # Demo video feed
        self.demo_frame_counter = 0
        
        self.setup_ui()
        self.setup_pygame()
        
        # Start demo video immediately
        self.start_demo_video()
        
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
        else:
            self.gamepad_name.set("No gamepad detected")
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create main frames
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Left side - Controls
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Right side - Video and AI
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.setup_control_panel(left_frame)
        self.setup_video_and_ai_panel(right_frame)
        self.setup_command_panel(bottom_frame)
        
    def setup_control_panel(self, parent):
        """Setup the left control panel"""
        # Demo mode indicator
        demo_frame = ttk.LabelFrame(parent, text="Demo Mode")
        demo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(demo_frame, text="🎮 SIMULATION MODE", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Label(demo_frame, text="AI features simulated", foreground="blue").pack()
        
        mode_buttons = ttk.Frame(demo_frame)
        mode_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(mode_buttons, text="Real Drone", command=self.switch_to_real_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(mode_buttons, text="Demo Mode", command=self.switch_to_demo_mode).pack(side=tk.RIGHT, padx=2)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(parent, text="Connection")
        conn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(conn_frame, text="Connect", command=self.connect_drone).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_drone).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.connection_status = tk.StringVar(value="Demo Mode")
        ttk.Label(conn_frame, textvariable=self.connection_status).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(parent, text="Drone Status")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.battery_level = tk.StringVar(value="Battery: 85%")
        self.flight_time = tk.StringVar(value="Flight Time: 45s")
        self.height = tk.StringVar(value="Height: 120cm")
        self.temperature = tk.StringVar(value="Temp: 28°C")
        
        ttk.Label(status_frame, textvariable=self.battery_level).pack(anchor=tk.W)
        ttk.Label(status_frame, textvariable=self.flight_time).pack(anchor=tk.W)
        ttk.Label(status_frame, textvariable=self.height).pack(anchor=tk.W)
        ttk.Label(status_frame, textvariable=self.temperature).pack(anchor=tk.W)
        
        # Flight controls
        flight_frame = ttk.LabelFrame(parent, text="Flight Controls")
        flight_frame.pack(fill=tk.X, pady=5)
        
        flight_buttons = [
            ("Takeoff", self.takeoff),
            ("Land", self.land),
            ("Emergency", self.emergency_stop)
        ]
        
        for text, command in flight_buttons:
            ttk.Button(flight_frame, text=text, command=command).pack(fill=tk.X, pady=2)
        
        # Speed control
        speed_frame = ttk.Frame(flight_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=50)
        speed_scale = ttk.Scale(speed_frame, from_=10, to=100, variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(speed_frame, textvariable=self.speed_var).pack(side=tk.LEFT)
        
        # Virtual joysticks
        joystick_frame = ttk.LabelFrame(parent, text="Manual Controls")
        joystick_frame.pack(fill=tk.X, pady=5)
        
        # Left joystick (movement)
        left_joy_frame = ttk.Frame(joystick_frame)
        left_joy_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(left_joy_frame, text="Movement").pack()
        self.left_joystick = VirtualJoystick(left_joy_frame, callback=self.on_movement_joystick)
        
        # Right joystick (rotation/altitude)
        right_joy_frame = ttk.Frame(joystick_frame)
        right_joy_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(right_joy_frame, text="Rotation/Alt").pack()
        self.right_joystick = VirtualJoystick(right_joy_frame, callback=self.on_rotation_joystick)
        
        # Gamepad status
        gamepad_frame = ttk.Frame(parent)
        gamepad_frame.pack(fill=tk.X, pady=5)
        self.gamepad_name = tk.StringVar(value="No gamepad detected")
        ttk.Label(gamepad_frame, textvariable=self.gamepad_name).pack()
        
    def setup_video_and_ai_panel(self, parent):
        """Setup the right panel with video and AI analysis"""
        # Video frame
        video_frame = ttk.LabelFrame(parent, text="Live Video Feed (Simulated)")
        video_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.video_label = ttk.Label(video_frame, text="Starting demo video...")
        self.video_label.pack(expand=True)
        
        # AI Analysis frame
        ai_frame = ttk.LabelFrame(parent, text="AI Vision Analysis (Mock StreamVLM)")
        ai_frame.pack(fill=tk.X, pady=5, ipady=10)
        
        # AI controls
        ai_controls = ttk.Frame(ai_frame)
        ai_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(ai_controls, text="Analyze Current View", command=self.analyze_current_frame).pack(side=tk.LEFT, padx=5)
        
        self.auto_analysis_var = tk.BooleanVar()
        auto_check = ttk.Checkbutton(ai_controls, text="Auto Analysis", variable=self.auto_analysis_var, command=self.toggle_auto_analysis)
        auto_check.pack(side=tk.LEFT, padx=5)
        
        # Analysis display
        self.ai_analysis = scrolledtext.ScrolledText(ai_frame, height=6, width=60)
        self.ai_analysis.pack(fill=tk.X, pady=5)
        
        # AI instruction frame
        instruction_frame = ttk.LabelFrame(parent, text="AI Flight Instructions")
        instruction_frame.pack(fill=tk.X, pady=5)
        
        # Custom instruction input
        custom_frame = ttk.Frame(instruction_frame)
        custom_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(custom_frame, text="Custom Analysis:").pack(side=tk.LEFT)
        self.custom_instruction = ttk.Entry(custom_frame, width=40)
        self.custom_instruction.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.custom_instruction.insert(0, "What do you see? Describe any obstacles or interesting features.")
        ttk.Button(custom_frame, text="Analyze", command=self.analyze_with_custom_instruction).pack(side=tk.RIGHT)
        
        # Natural language command input
        nl_frame = ttk.Frame(instruction_frame)
        nl_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(nl_frame, text="Voice Command:").pack(side=tk.LEFT)
        self.nl_command = ttk.Entry(nl_frame, width=40)
        self.nl_command.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.nl_command.insert(0, "Move forward 50cm")
        self.nl_command.bind('<Return>', self.execute_natural_language_command)
        ttk.Button(nl_frame, text="Execute", command=self.execute_natural_language_command).pack(side=tk.RIGHT)
        
        # Quick command buttons
        quick_frame = ttk.Frame(instruction_frame)
        quick_frame.pack(fill=tk.X, pady=5)
        
        quick_commands = [
            ("Explore Area", "look around and explore"),
            ("Find Person", "look for people and follow them"),
            ("Avoid Obstacles", "identify obstacles and avoid them"),
            ("Patrol Route", "patrol the area systematically")
        ]
        
        for i, (text, command) in enumerate(quick_commands):
            btn = ttk.Button(quick_frame, text=text, command=lambda cmd=command: self.execute_quick_command(cmd))
            btn.grid(row=i//2, column=i%2, padx=2, pady=2, sticky='ew')
        
        quick_frame.columnconfigure(0, weight=1)
        quick_frame.columnconfigure(1, weight=1)
        
    def setup_command_panel(self, parent):
        """Setup the bottom command panel"""
        # Command shell frame
        shell_frame = ttk.LabelFrame(parent, text="Command Log & Manual Control")
        shell_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        shell_container = ttk.Frame(shell_frame)
        shell_container.pack(fill=tk.BOTH, expand=True)
        
        # Command output
        self.command_output = scrolledtext.ScrolledText(shell_container, height=10, width=80)
        self.command_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Manual command input
        manual_frame = ttk.Frame(shell_container)
        manual_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(manual_frame, text="Manual Commands:").pack(anchor=tk.W)
        
        cmd_input_frame = ttk.Frame(manual_frame)
        cmd_input_frame.pack(fill=tk.X, pady=2)
        
        self.command_entry = ttk.Entry(cmd_input_frame, width=30)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind('<Return>', self.send_manual_command)
        
        ttk.Button(cmd_input_frame, text="Send", command=self.send_manual_command).pack(side=tk.RIGHT, padx=(5,0))
        
        # Sample commands
        ttk.Label(manual_frame, text="Sample Commands:").pack(anchor=tk.W, pady=(10,5))
        samples = ["battery?", "height?", "up 50", "forward 100", "cw 90", "flip f"]
        for cmd in samples:
            btn = ttk.Button(manual_frame, text=cmd, command=lambda c=cmd: self.send_sample_command(c))
            btn.pack(fill=tk.X, pady=1)
        
        # Add welcome message
        self.log_message("=== AI Tello Controller Demo with StreamVLM Simulation ===")
        self.log_message("🎮 Currently in DEMO MODE - AI features are simulated")
        self.log_message("")
        self.log_message("Features demonstrated:")
        self.log_message("• Natural language flight commands")
        self.log_message("• AI-powered visual analysis (simulated)")
        self.log_message("• Automatic obstacle detection concepts")
        self.log_message("• Real-time video streaming simulation")
        self.log_message("")
        self.log_message("Try commands like:")
        self.log_message("• 'Move forward 50cm'")
        self.log_message("• 'Turn left 90 degrees'")
        self.log_message("• 'Explore the area'")
        self.log_message("• 'Look for obstacles'")
        self.log_message("")
        
    def start_demo_video(self):
        """Start simulated video feed"""
        def demo_video_loop():
            while self.demo_mode and not self.stop_video:
                try:
                    # Generate a simple animated demo frame
                    frame = self.generate_demo_frame()
                    self.current_frame = frame.copy()
                    self.display_frame(frame)
                    time.sleep(0.033)  # ~30 FPS
                except Exception as e:
                    logger.error(f"Demo video error: {e}")
                    time.sleep(0.1)
                    
        self.video_thread = threading.Thread(target=demo_video_loop, daemon=True)
        self.video_thread.start()
        
    def generate_demo_frame(self):
        """Generate a simulated camera frame"""
        # Create a 640x480 frame with a simple scene
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Background gradient
        for y in range(480):
            intensity = int(50 + (y / 480) * 100)
            frame[y, :] = [intensity, intensity, intensity]
        
        # Add some "room" features
        # Floor line
        cv2.line(frame, (0, 400), (640, 400), (100, 100, 100), 2)
        
        # Some "walls" or objects
        self.demo_frame_counter += 1
        offset = int(10 * np.sin(self.demo_frame_counter * 0.05))
        
        # Moving objects to simulate camera movement
        cv2.rectangle(frame, (100 + offset, 200), (150 + offset, 400), (80, 80, 120), -1)
        cv2.rectangle(frame, (500 - offset, 150), (550 - offset, 400), (120, 80, 80), -1)
        
        # Add some text overlay
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "DEMO: Simulated Drone View", (20, 30), font, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Frame: {self.demo_frame_counter}", (20, 460), font, 0.5, (200, 200, 200), 1)
        
        # Simulate battery and status overlay
        cv2.putText(frame, "Battery: 85%", (500, 30), font, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, "Height: 120cm", (500, 50), font, 0.5, (255, 255, 0), 1)
        
        return frame
        
    def switch_to_real_mode(self):
        """Switch to real drone mode"""
        self.demo_mode = False
        self.stop_video = True
        self.connection_status.set("Real Mode - Disconnected")
        self.video_label.config(text="Real mode - Connect to drone for video")
        self.log_message("Switched to REAL DRONE mode")
        
    def switch_to_demo_mode(self):
        """Switch to demo mode"""
        self.demo_mode = True
        self.connected = False
        self.connection_status.set("Demo Mode")
        self.start_demo_video()
        self.log_message("Switched to DEMO mode")
        
    def on_movement_joystick(self, x, y):
        """Handle movement joystick input"""
        self.movement_commands['left_right'] = x
        self.movement_commands['forward_back'] = y
        if self.connected:
            self.send_rc_command()
        elif self.demo_mode:
            self.log_message(f"Demo: Movement joystick - LR:{x}, FB:{y}")
            
    def on_rotation_joystick(self, x, y):
        """Handle rotation/altitude joystick input"""
        self.movement_commands['yaw'] = x
        self.movement_commands['up_down'] = y
        if self.connected:
            self.send_rc_command()
        elif self.demo_mode:
            self.log_message(f"Demo: Rotation joystick - Yaw:{x}, Alt:{y}")
            
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
        if self.demo_mode:
            self.connection_status.set("Demo Mode - Simulated")
            self.log_message("Demo mode: Simulating drone connection...")
            return
            
        try:
            self.connection_status.set("Connecting...")
            self.log_message("Attempting to connect to Tello drone...")
            
            self.tello = Tello()
            self.tello.connect()
            
            time.sleep(1)
            
            try:
                battery = self.tello.get_battery()
                self.connected = True
                self.connection_status.set("Connected")
                
                self.log_message(f"✓ Connected to Tello drone (Battery: {battery}%)")
                
                # Start video stream
                self.start_real_video_stream()
                
                # Start status monitoring
                self.start_status_monitoring()
                
            except Exception as battery_error:
                self.connected = True
                self.connection_status.set("Connected (Limited)")
                self.log_message("✓ Connected to Tello drone (status monitoring limited)")
                self.start_real_video_stream()
                
        except Exception as e:
            self.connected = False
            self.connection_status.set("Connection Failed")
            self.log_message(f"✗ Connection failed: {e}")
            messagebox.showerror("Connection Error", f"Failed to connect to Tello drone:\n{e}")
            
    def start_real_video_stream(self):
        """Start real video streaming"""
        if not self.tello:
            return
            
        try:
            self.tello.streamon()
            self.stop_video = False
            
            def video_loop():
                video_sources = [
                    f"udp://192.168.10.1:11111",
                    f"udp://@192.168.10.1:11111", 
                    f"udp://0.0.0.0:11111"
                ]
                
                cap = None
                for video_url in video_sources:
                    try:
                        self.log_message(f"Trying video source: {video_url}")
                        cap = cv2.VideoCapture(video_url)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            self.log_message(f"✓ Video stream working: {video_url}")
                            break
                        else:
                            cap.release()
                            cap = None
                    except Exception as e:
                        if cap:
                            cap.release()
                        cap = None
                
                if cap is None:
                    self.log_message("Using djitellopy fallback method...")
                    while not self.stop_video and self.connected:
                        try:
                            frame = self.tello.get_frame_read().frame
                            if frame is not None:
                                self.current_frame = frame.copy()
                                self.display_frame(frame)
                        except Exception as e:
                            self.log_message(f"Video error: {e}")
                            time.sleep(0.1)
                else:
                    self.log_message("Using direct OpenCV video capture")
                    while not self.stop_video and self.connected:
                        try:
                            ret, frame = cap.read()
                            if ret and frame is not None:
                                self.current_frame = frame.copy()
                                self.display_frame(frame)
                            else:
                                time.sleep(0.033)
                        except Exception as e:
                            self.log_message(f"OpenCV video error: {e}")
                            time.sleep(0.1)
                    
                    if cap:
                        cap.release()
                        
            self.video_thread = threading.Thread(target=video_loop, daemon=True)
            self.video_thread.start()
            
        except Exception as e:
            self.log_message(f"Video stream error: {e}")
            
    def disconnect_drone(self):
        """Disconnect from Tello drone"""
        try:
            self.connected = False
            self.stop_video = True
            self.auto_analysis = False
            
            if self.demo_mode:
                self.connection_status.set("Demo Mode")
                self.log_message("Demo mode: Simulated disconnect")
                return
            
            if self.tello:
                self.tello.send_rc_control(0, 0, 0, 0)
                time.sleep(0.1)
                
            self.connection_status.set("Disconnected")
            self.log_message("Disconnected from Tello drone")
            
            # Clear video
            self.video_label.config(image='', text="No video signal")
            
        except Exception as e:
            self.log_message(f"Disconnect error: {e}")
            
    def display_frame(self, frame):
        """Display video frame in GUI"""
        try:
            # Resize frame for display
            frame_display = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image and then to PhotoImage
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            # Update GUI (must be done in main thread)
            self.root.after(0, lambda: self.update_video_frame(photo))
            
        except Exception as e:
            logger.error(f"Display frame error: {e}")
            
    def update_video_frame(self, photo):
        """Update video frame in GUI"""
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo
        
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
                        
                        self.root.after(0, lambda: self.update_status(battery, height, flight_time, temp))
                        
                except Exception as e:
                    logger.error(f"Status monitoring error: {e}")
                    
                time.sleep(2)
                
        threading.Thread(target=status_loop, daemon=True).start()
        
    def update_status(self, battery, height, flight_time, temp):
        """Update status display"""
        self.battery_level.set(f"Battery: {battery}%")
        self.height.set(f"Height: {height}cm")
        self.flight_time.set(f"Flight Time: {flight_time}s")
        self.temperature.set(f"Temp: {temp}°C")
        
    def analyze_current_frame(self):
        """Analyze the current video frame"""
        if self.current_frame is None:
            self.log_message("No video frame available for analysis")
            return
            
        self.log_message("Analyzing current frame with Mock StreamVLM...")
        
        def analyze():
            instruction = "Describe what you see in this drone camera view. Identify any people, objects, obstacles, or interesting features."
            analysis = self.vlm_client.analyze_frame(self.current_frame, instruction)
            
            if analysis:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.root.after(0, lambda: self.display_analysis(f"[{timestamp}] {analysis}"))
            else:
                self.root.after(0, lambda: self.log_message("Analysis failed"))
        
        threading.Thread(target=analyze, daemon=True).start()
        
    def analyze_with_custom_instruction(self):
        """Analyze frame with custom instruction"""
        if self.current_frame is None:
            self.log_message("No video frame available for analysis")
            return
            
        instruction = self.custom_instruction.get().strip()
        if not instruction:
            self.log_message("Please enter a custom instruction")
            return
            
        self.log_message(f"Analyzing with instruction: {instruction}")
        
        def analyze():
            analysis = self.vlm_client.analyze_frame(self.current_frame, instruction)
            
            if analysis:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.root.after(0, lambda: self.display_analysis(f"[{timestamp}] Custom: {analysis}"))
            else:
                self.root.after(0, lambda: self.log_message("Analysis failed"))
        
        threading.Thread(target=analyze, daemon=True).start()
        
    def execute_natural_language_command(self, event=None):
        """Execute natural language flight command"""
        command_text = self.nl_command.get().strip()
        if not command_text:
            return
            
        self.log_message(f"Executing NL command: '{command_text}'")
        
        # If we have recent analysis, use it for context
        analysis_context = ""
        if self.vlm_client.last_analysis:
            analysis_context = self.vlm_client.last_analysis['analysis']
        
        # Parse command
        commands = self.vlm_client.parse_flight_instruction(analysis_context, command_text)
        
        if commands:
            self.log_message(f"Parsed commands: {commands}")
            for cmd in commands:
                if cmd.startswith("#"):
                    self.log_message(cmd)
                else:
                    self.execute_drone_command(cmd)
                    time.sleep(0.5)  # Small delay between commands
        else:
            self.log_message("Could not parse natural language command")
            
    def execute_quick_command(self, command):
        """Execute a quick command"""
        self.nl_command.delete(0, tk.END)
        self.nl_command.insert(0, command)
        self.execute_natural_language_command()
        
    def execute_drone_command(self, command):
        """Execute a single drone command"""
        if self.demo_mode:
            self.log_message(f"Demo: Would execute '{command}'")
            return
            
        if not self.connected or not self.tello:
            self.log_message("Not connected to drone")
            return
            
        try:
            parts = command.lower().split()
            if not parts:
                return
                
            cmd = parts[0]
            
            if cmd == "takeoff":
                self.tello.takeoff()
                self.log_message("✓ Takeoff executed")
            elif cmd == "land":
                self.tello.land()
                self.log_message("✓ Land executed")
            elif cmd in ["up", "down", "forward", "back", "left", "right"] and len(parts) > 1:
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
                self.log_message(f"✓ {cmd} {distance}cm executed")
            elif cmd in ["cw", "ccw"] and len(parts) > 1:
                angle = int(parts[1])
                if cmd == "cw":
                    self.tello.rotate_clockwise(angle)
                elif cmd == "ccw":
                    self.tello.rotate_counter_clockwise(angle)
                self.log_message(f"✓ {cmd} {angle}° executed")
            elif cmd == "flip" and len(parts) > 1:
                direction = parts[1]
                if direction in ['f', 'b', 'l', 'r']:
                    self.tello.flip(direction)
                    self.log_message(f"✓ Flip {direction} executed")
            else:
                self.log_message(f"Unknown command: {command}")
                
        except Exception as e:
            self.log_message(f"Command execution error: {e}")
            
    def toggle_auto_analysis(self):
        """Toggle automatic analysis"""
        self.auto_analysis = self.auto_analysis_var.get()
        
        if self.auto_analysis:
            self.log_message("Auto analysis enabled (simulated)")
            self.start_auto_analysis()
        else:
            self.log_message("Auto analysis disabled")
            
    def start_auto_analysis(self):
        """Start automatic analysis thread"""
        def auto_analysis_loop():
            while self.auto_analysis and (self.connected or self.demo_mode):
                try:
                    if self.current_frame is not None:
                        instruction = "Describe the current view. Are there any obstacles, people, or interesting features to note?"
                        analysis = self.vlm_client.analyze_frame(self.current_frame, instruction)
                        
                        if analysis:
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            self.root.after(0, lambda: self.display_analysis(f"[{timestamp}] Auto: {analysis}"))
                    
                    time.sleep(self.analysis_interval)
                    
                except Exception as e:
                    self.log_message(f"Auto analysis error: {e}")
                    time.sleep(1)
                    
        if self.auto_analysis:
            threading.Thread(target=auto_analysis_loop, daemon=True).start()
            
    def display_analysis(self, analysis_text):
        """Display AI analysis in the text area"""
        self.ai_analysis.insert(tk.END, f"{analysis_text}\n\n")
        self.ai_analysis.see(tk.END)
        
    def send_manual_command(self, event=None):
        """Send manual command"""
        command = self.command_entry.get().strip()
        if not command:
            return
            
        self.command_entry.delete(0, tk.END)
        self.log_message(f"> {command}")
        
        if self.demo_mode:
            self.log_message(f"Demo: Would send '{command}'")
            return
            
        if not self.connected or not self.tello:
            self.log_message("Error: Not connected to drone")
            return
            
        try:
            parts = command.lower().split()
            cmd = parts[0]
            
            if cmd == "battery?":
                result = self.tello.get_battery()
                self.log_message(f"Battery: {result}%")
            elif cmd == "height?":
                result = self.tello.get_height()
                self.log_message(f"Height: {result}cm")
            else:
                self.execute_drone_command(command)
                
        except Exception as e:
            self.log_message(f"Command error: {e}")
            
    def send_sample_command(self, command):
        """Send a sample command"""
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, command)
        self.send_manual_command()
        
    def takeoff(self):
        """Takeoff command"""
        if self.demo_mode:
            self.log_message("Demo: Takeoff command sent")
            return
            
        try:
            if self.tello and self.connected:
                self.tello.takeoff()
                self.log_message("Takeoff command sent")
        except Exception as e:
            self.log_message(f"Takeoff error: {e}")
            
    def land(self):
        """Land command"""
        if self.demo_mode:
            self.log_message("Demo: Land command sent")
            return
            
        try:
            if self.tello and self.connected:
                self.tello.land()
                self.log_message("Land command sent")
        except Exception as e:
            self.log_message(f"Land error: {e}")
            
    def emergency_stop(self):
        """Emergency stop"""
        if self.demo_mode:
            self.log_message("Demo: EMERGENCY STOP!")
            return
            
        try:
            if self.tello and self.connected:
                self.tello.emergency()
                self.log_message("EMERGENCY STOP!")
        except Exception as e:
            self.log_message(f"Emergency stop error: {e}")
            
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
    print("Starting AI-Powered Tello Controller Demo...")
    print("This demo shows AI drone control concepts without requiring heavy ML dependencies.")
    print()
    
    app = AITelloDemoController()
    app.run()