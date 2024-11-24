# main.py
import math
from time import sleep

import cv2 as cv
import numpy as np
import threading
import schedule
import asyncio

from config import config
from modules.depth_map import Preprocessor, DepthMapProcessorSGBM
from modules.camera import CameraInterface
from modules.edge_detection.calibration import Rectification
from modules.opc_server import OpcuaServer

# Constants
CAMERA_RESOLUTION = config.CAMERA_RESOLUTION
OPCUA_SERVER_URL = "opc.tcp://0.0.0.0:4840/cablelay/server/"
OPCUA_NAMESPACE = "http://cablelay.com"


# To PLC
async def send_to_plc(opcua_server, name, value):
    if not math.isnan(value):
        opcua_server.update_variable(name, value)


# Callback function for subscription notifications
def opc_callback(name, value):
    if "height" not in name:
        print(f"Callback triggered for node {name}, new value: {value}")


def run_opcua_server(opcua_server):
    opcua_server.run()


async def main():
    # Initialize camera interface
    camera = CameraInterface(CAMERA_RESOLUTION)
    vid_left, vid_right = camera.getcamera()

    # Initialize processors
    preprocessor = Preprocessor()
    rectification = Rectification()
    depth_map_processor = DepthMapProcessorSGBM()

    # Initialize OPC UA server
    opcua_server = OpcuaServer(OPCUA_SERVER_URL, OPCUA_NAMESPACE, callback=opc_callback)

    # Run OPC UA server in a separate thread
    opcua_thread = threading.Thread(target=run_opcua_server, args=(opcua_server,), daemon=True)
    opcua_thread.start()

    try:
        while True:
            # Capture frames from left and right cameras
            ret_left, frame_left = vid_left.read()
            ret_right, frame_right = vid_right.read()

            if not ret_left or not ret_right:
                print("Error capturing frames. Exiting.")
                break

            # Convert frames to grayscale
            gray_left = cv.cvtColor(frame_left, cv.COLOR_BGR2GRAY)
            gray_right = cv.cvtColor(frame_right, cv.COLOR_BGR2GRAY)

            # Rectify images
            gray_left, gray_right = rectification.undistortrectify(gray_left, gray_right)

            # Preprocess images
            preprocessed_left = preprocessor.preprocess(gray_left)
            preprocessed_right = preprocessor.preprocess(gray_right)

            # Display preprocessed images side by side
            combined_preprocessed = np.hstack((preprocessed_left, preprocessed_right))
            cv.imshow(preprocessor.window_name, combined_preprocessed)

            # Compute depth map
            depth_map, height1, height2, height3 = depth_map_processor.compute_disparity_map(preprocessed_left,
                preprocessed_right)
            cv.imshow(depth_map_processor.window_name, depth_map)

            # Update OPC UA variables
            await send_to_plc(opcua_server, "height1", height1)
            await send_to_plc(opcua_server, "height2", height2)
            await send_to_plc(opcua_server, "height3", height3)

            # Handle key press events
            key = cv.waitKey(1) & 0xFF
            if key == ord('s'):
                preprocessor.save_parameters()
                depth_map_processor.save_parameters()
                print("Parameters saved.")
            elif key == 27:  # ESC key
                print("Exiting without saving changes.")
                break

    finally:
        # Release resources
        vid_left.release()
        vid_right.release()
        cv.destroyAllWindows()
        opcua_server.stop()


if __name__ == "__main__":
    asyncio.run(main())
