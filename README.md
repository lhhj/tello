# Tello Drone Controller

A comprehensive Python GUI application for controlling DJI Tello drones with video streaming, virtual joystick controls, and command shell interface.

## Features

- **Real-time Video Streaming**: Live video feed from the Tello drone's camera
- **Virtual Joystick Controls**: On-screen joysticks for intuitive drone movement
- **Physical Gamepad Support**: Compatible with Xbox/PlayStation controllers
- **Command Shell**: Direct command interface for advanced drone control
- **Flight Status Monitoring**: Real-time battery, height, temperature, and flight time
- **Basic Flight Controls**: Takeoff, land, and emergency stop buttons
- **Speed Control**: Adjustable flight speed via slider

## Requirements

- Python 3.7+
- DJI Tello drone
- WiFi connection to the Tello drone
- Optional: USB gamepad/controller

## Installation

1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. **Connect to Tello Drone WiFi**:
   - Turn on your Tello drone
   - Connect your computer to the Tello drone's WiFi network (usually named "TELLO-XXXXXX")
   - The drone creates its own WiFi network with IP address 192.168.10.1

2. **Test Connection** (Optional but Recommended):
   ```bash
   python test_connection.py
   ```
   Or for a quick check:
   ```bash
   python minimal_test.py
   ```

3. **Run the Application**:
   ```bash
   python tello_controller.py
   ```

## Usage

### Connection
1. Click "Connect" to establish connection with the drone
2. The status will show "Connected" and battery level when successful
3. Video stream will automatically start

### Flight Controls
- **Takeoff**: Click the "Takeoff" button to start flying
- **Land**: Click the "Land" button to land the drone
- **Emergency**: Click "Emergency" for immediate motor stop (use carefully!)

### Virtual Joysticks
- **Left Joystick**: Controls horizontal movement (forward/back, left/right)
- **Right Joystick**: Controls altitude (up/down) and rotation (yaw left/right)

### Gamepad Support
- Connect a USB gamepad before starting the application
- Left stick: Horizontal movement
- Right stick: Altitude and rotation
- The gamepad status will be displayed at the bottom left

### Command Shell
Type commands in the command input field. Supported commands include:

**Status Commands**:
- `battery?` - Get current battery level
- `speed?` - Get current speed setting
- `height?` - Get current height above ground

**Movement Commands**:
- `up [distance]` - Move up (20-500cm)
- `down [distance]` - Move down (20-500cm)
- `forward [distance]` - Move forward (20-500cm)
- `back [distance]` - Move backward (20-500cm)
- `left [distance]` - Move left (20-500cm)
- `right [distance]` - Move right (20-500cm)

**Rotation Commands**:
- `cw [degrees]` - Rotate clockwise (1-360°)
- `ccw [degrees]` - Rotate counter-clockwise (1-360°)

**Flip Commands**:
- `flip f` - Flip forward
- `flip b` - Flip backward
- `flip l` - Flip left
- `flip r` - Flip right

### Example Commands
```
battery?
height?
up 50
forward 100
cw 90
flip f
```

## Safety Notes

- Always fly in a safe, open area
- Keep the drone within line of sight
- Monitor battery level regularly
- Use the emergency stop only when necessary (it will cause the drone to fall)
- Be aware of local drone flying regulations

## Troubleshooting

**Connection Test**:
- Run `python test_connection.py` for comprehensive connection testing
- Run `python minimal_test.py` for quick connectivity check
- Use `test_connection.bat` on Windows for an interactive menu

**Connection Issues**:
- Ensure you're connected to the Tello WiFi network
- Check that the drone is powered on and in range
- Try restarting the drone and reconnecting

**Video Stream Issues**:
- Video may take a few seconds to appear after connection
- If video is choppy, ensure strong WiFi signal
- Close other applications using the camera

**Gamepad Issues**:
- Connect gamepad before starting the application
- Ensure gamepad is recognized by Windows
- Check pygame gamepad compatibility

## Dependencies

- **djitellopy**: Tello drone SDK wrapper
- **opencv-python**: Video processing and display
- **pygame**: Gamepad input handling
- **Pillow**: Image processing for GUI
- **numpy**: Numerical operations
- **tkinter**: GUI framework (included with Python)

## License

This project is for educational and hobbyist purposes. Please follow local regulations regarding drone usage.

## Contributing

Feel free to submit issues, suggestions, or pull requests to improve the application.