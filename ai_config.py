# AI Tello Controller Configuration

# Hugging Face API Configuration
# Get your token from: https://huggingface.co/settings/tokens
HUGGINGFACE_API_TOKEN = ""

# StreamVLM Model Configuration
# Available models:
# - microsoft/StreamVLM (default)
# - microsoft/kosmos-2
# - Salesforce/blip2-opt-2.7b
STREAMVLM_MODEL = "microsoft/StreamVLM"

# AI Analysis Settings
AUTO_ANALYSIS_INTERVAL = 5  # seconds between automatic analyses
MAX_ANALYSIS_HISTORY = 10   # number of analyses to keep in memory

# Flight Safety Settings
MAX_MOVEMENT_DISTANCE = 500  # cm
MAX_ROTATION_ANGLE = 360     # degrees
DEFAULT_MOVEMENT_SPEED = 50  # cm/s
DEFAULT_ROTATION_SPEED = 90  # degrees/s

# Video Stream Settings
VIDEO_DISPLAY_WIDTH = 640
VIDEO_DISPLAY_HEIGHT = 480
VIDEO_QUALITY = 85  # JPEG quality for API transmission

# Natural Language Processing
# Keywords for movement detection
MOVEMENT_KEYWORDS = {
    "forward": ["forward", "ahead", "move forward", "go forward"],
    "back": ["back", "backward", "retreat", "go back"],
    "left": ["left", "go left", "move left"],
    "right": ["right", "go right", "move right"],
    "up": ["up", "higher", "rise", "ascend", "go up"],
    "down": ["down", "lower", "descend", "go down"],
    "turn_left": ["turn left", "rotate left", "spin left"],
    "turn_right": ["turn right", "rotate right", "spin right"],
    "takeoff": ["takeoff", "take off", "launch", "fly"],
    "land": ["land", "landing", "come down"],
    "stop": ["stop", "halt", "freeze", "emergency"],
    "flip": ["flip", "do a flip", "barrel roll"]
}

# Context-aware command keywords
CONTEXT_KEYWORDS = {
    "follow": ["follow", "track", "chase", "pursue"],
    "avoid": ["avoid", "dodge", "evade", "stay away"],
    "explore": ["explore", "look around", "search", "patrol"],
    "inspect": ["inspect", "examine", "check", "investigate"],
    "return": ["return", "go back", "come back", "home"]
}

# Safety boundaries (prevent dangerous commands)
SAFETY_BOUNDARIES = {
    "min_distance": 20,    # minimum movement distance (cm)
    "max_distance": 500,   # maximum movement distance (cm)
    "min_angle": 1,        # minimum rotation angle (degrees)
    "max_angle": 360,      # maximum rotation angle (degrees)
    "max_altitude": 300,   # maximum altitude (cm)
    "emergency_words": ["emergency", "stop", "halt", "abort", "cancel"]
}