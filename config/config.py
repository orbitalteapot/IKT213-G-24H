# config.py

# Camera configuration
CAMERA_RESOLUTION = (640,480)

# Siemens PLC OPC UA port
PLC_IP_ADDRESS = "192.168.0.10"
PLC_PORT = 4840


# Preprocessing Configuration
NOISE_THRESHOLD = 0.7
GAMMA = 1.4
CONTRAST_LEVEL = 1.5

# Depth Map Configuration
numDisparities = 128           # Default to 128 for a good balance between depth range and processing speed
blockSize = 7                 # Default to 15 for stable, low-noise output
minDisparity = 0               # Start at 0 to capture a wider depth range
textureThreshold = 10          # Set to 10 to filter out low-texture regions without losing important details
uniquenessRatio = 10           # Set to 10 for balanced filtering of incorrect matches
speckleWindowSize = 100        # Use 100 to filter out small noise regions
speckleRange = 32              # Set to 32 to handle disparity variations within noisy areas
disp12MaxDiff = 1              # Set to 1 to ensure left-right consistency while allowing minor disparity variations



