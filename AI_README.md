# AI-Powered Tello Drone Controller with StreamVLM Integration

This project extends the basic Tello drone controller with AI-powered computer vision and natural language processing capabilities using Hugging Face's StreamVLM model.

## 🚀 Features

### Core AI Features
- **Visual Understanding**: Real-time analysis of drone camera feed using StreamVLM
- **Natural Language Control**: Text-based flight instructions that get parsed into drone commands
- **Context-Aware Navigation**: AI-powered obstacle detection and avoidance suggestions
- **Automated Analysis**: Continuous visual monitoring with customizable analysis intervals

### Flight Control Features
- **Voice Commands**: Natural language instructions like "move forward 50cm" or "avoid obstacles"
- **Smart Parsing**: Extracts distances, angles, and directions from conversational text
- **Safety Boundaries**: Built-in limits to prevent dangerous commands
- **Multi-Modal Control**: Combines AI instructions with manual joystick and gamepad control

### Advanced Capabilities
- **Object Tracking**: "Follow person" or "track object" commands
- **Exploration Modes**: "Explore area" or "patrol route" automated sequences
- **Dynamic Responses**: AI adapts commands based on what it sees in the camera feed
- **Historical Analysis**: Keeps track of recent visual analyses for context

## 🏗️ Architecture

### Components

1. **ai_tello_controller.py** - Full AI-enabled controller with StreamVLM integration
2. **ai_tello_demo.py** - Lightweight demo version with simulated AI features
3. **ai_config.py** - Configuration settings for AI models and safety parameters
4. **StreamVLMClient** - Handles communication with Hugging Face API
5. **Natural Language Parser** - Converts text commands to drone instructions

### AI Integration Flow

```
Video Feed → StreamVLM Model → Visual Analysis → Context
     ↓                                              ↓
User Command → NLP Parser → Flight Commands → Drone Execution
```

## 📦 Installation

### Option 1: Demo Version (Recommended for Testing)
```bash
# Run the lightweight demo without AI dependencies
./run_ai_demo.bat
```

### Option 2: Full AI Version
```bash
# Install AI dependencies (this will take some time)
./install_ai_deps.bat

# Get Hugging Face API token from: https://huggingface.co/settings/tokens
# Edit ai_config.py and add your token

# Run the full AI controller
./run_ai_tello.bat
```

### Manual Installation
```bash
# Activate virtual environment
.\.venv\Scripts\activate.bat

# Install basic requirements
pip install djitellopy opencv-python pygame pillow numpy requests

# For full AI features (optional)
pip install torch torchvision transformers scikit-image nltk
```

## 🎮 Usage

### Basic Natural Language Commands

#### Movement Commands
- "Move forward 50cm"
- "Go back 2 meters" 
- "Turn left 90 degrees"
- "Fly up 1 meter"
- "Rotate right 45 degrees"

#### Flight Control
- "Take off"
- "Land now"
- "Emergency stop"
- "Do a forward flip"

#### AI-Powered Commands
- "Look for people and follow them"
- "Avoid obstacles ahead"
- "Explore the area safely"
- "Patrol this room"
- "Find the exit"

#### Custom Analysis
- "What do you see in front?"
- "Are there any obstacles?"
- "Describe the room layout"
- "Look for people in the area"

### GUI Controls

#### Video Analysis Panel
- **Analyze Current View**: Get AI description of current camera view
- **Auto Analysis**: Enable continuous visual monitoring
- **Custom Analysis**: Enter specific questions about what the drone sees

#### Flight Instruction Panel
- **Voice Command**: Enter natural language flight instructions
- **Quick Commands**: Pre-defined AI-powered actions
- **Manual Override**: Direct drone command input for precise control

### Configuration

Edit `ai_config.py` to customize:

```python
# API Configuration
HUGGINGFACE_API_TOKEN = "your_token_here"
STREAMVLM_MODEL = "microsoft/StreamVLM"

# Safety Settings
MAX_MOVEMENT_DISTANCE = 500  # cm
MAX_ROTATION_ANGLE = 360     # degrees

# AI Settings
AUTO_ANALYSIS_INTERVAL = 5   # seconds
MAX_ANALYSIS_HISTORY = 10    # analyses to keep
```

## 🤖 AI Models Supported

### Primary Model
- **microsoft/StreamVLM**: Optimized for real-time video understanding

### Alternative Models
- **microsoft/kosmos-2**: General vision-language model
- **Salesforce/blip2-opt-2.7b**: Image captioning and QA

### Model Selection
Change the model in `ai_config.py`:
```python
STREAMVLM_MODEL = "microsoft/StreamVLM"  # or your preferred model
```

## 🛡️ Safety Features

### Built-in Safety Boundaries
- **Distance Limits**: 20cm minimum, 500cm maximum movement
- **Angle Limits**: 1° minimum, 360° maximum rotation
- **Altitude Limits**: Maximum indoor flight height
- **Emergency Keywords**: "emergency", "stop", "halt", "abort" trigger immediate stop

### Context-Aware Safety
- **Obstacle Detection**: AI analyzes video feed for potential obstacles
- **Person Detection**: Maintains safe distance when people are detected
- **Environment Assessment**: Evaluates space suitability before complex maneuvers

## 🔧 Troubleshooting

### Common Issues

#### "No API Token" Error
```bash
# Get token from: https://huggingface.co/settings/tokens
# Edit ai_config.py and add: HUGGINGFACE_API_TOKEN = "your_token"
```

#### Video Stream Not Working
```bash
# Try the demo version first
python ai_tello_demo.py

# For real drone, ensure WiFi connection to Tello network
# Check video fix in tello_controller.py is applied
```

#### AI Analysis Fails
```bash
# Check internet connection (required for Hugging Face API)
# Verify API token is valid
# Try with demo mode first to test interface
```

#### Heavy Resource Usage
```bash
# Use demo version for development/testing
# Full AI version requires significant CPU/memory for ML models
# Consider using lighter models or reducing analysis frequency
```

### Performance Optimization

#### For Low-End Hardware
- Use `ai_tello_demo.py` instead of full AI version
- Increase `AUTO_ANALYSIS_INTERVAL` to reduce API calls
- Use smaller/faster models like `microsoft/kosmos-2`

#### For Better Performance
- Ensure good internet connection for API calls
- Use SSD storage for faster model loading
- Close unnecessary applications to free up memory

## 🎯 Example Scenarios

### Scenario 1: Room Exploration
```
User: "Explore this room safely"
AI Analysis: "I see a room with furniture on the sides and clear center space"
Generated Commands: 
- forward 50
- cw 90  
- forward 50
- cw 90
```

### Scenario 2: Person Following
```
User: "Look for people and follow them"
AI Analysis: "I detect a person in the center-left of the view"
Generated Commands:
- # Following person detected in view
- left 30
- forward 40
```

### Scenario 3: Obstacle Avoidance
```
User: "There's something in front, avoid it"
AI Analysis: "I see what appears to be a large obstacle ahead"
Generated Commands:
- # Avoiding detected obstacle
- back 50
- cw 90
```

## 🔮 Future Enhancements

### Planned Features
- **Real-time Object Recognition**: Identify specific objects and navigate around them
- **Advanced Path Planning**: AI-generated optimal flight paths
- **Voice Recognition**: Spoken commands instead of text input
- **Multi-Drone Coordination**: AI-powered swarm intelligence
- **Augmented Reality**: Overlay AI analysis on video feed

### Model Improvements
- **Custom Fine-tuning**: Train models specifically for drone navigation
- **Edge Computing**: Run lightweight models locally for reduced latency
- **Sensor Fusion**: Combine camera data with other drone sensors

## 📚 API Reference

### StreamVLMClient Class

#### Methods
- `analyze_frame(frame, instruction)`: Analyze video frame with custom instruction
- `parse_flight_instruction(analysis, command)`: Convert natural language to flight commands
- `extract_distance(text, default)`: Extract distance values from text
- `extract_angle(text, default)`: Extract angle values from text

### AITelloController Class

#### Key Methods
- `execute_natural_language_command()`: Process and execute text commands
- `analyze_current_frame()`: Trigger AI analysis of current video
- `execute_drone_command(command)`: Execute single parsed command
- `toggle_auto_analysis()`: Enable/disable continuous analysis

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b ai-feature-name`
3. **Test with demo version first**: `python ai_tello_demo.py`
4. **Add real drone testing**: Ensure commands work with actual hardware
5. **Submit pull request**: Include demo videos if possible

### Development Guidelines
- Always test in demo mode before real drone testing
- Include safety checks for new AI commands
- Document new natural language patterns
- Test with different AI models when possible

## 📄 License

MIT License - feel free to use and modify for your projects!

## 🆘 Support

- **Issues**: Create GitHub issue with detailed description
- **Discussions**: Use GitHub discussions for questions
- **Demo**: Always try demo version first for faster troubleshooting

---

**⚠️ Safety Reminder**: Always fly responsibly and in accordance with local drone regulations. The AI features are experimental and should not be relied upon for critical flight operations.