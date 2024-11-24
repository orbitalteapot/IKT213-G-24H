import numpy as np
import cv2 as cv
import glob
import re
import os

# Chessboard parameters
chessboardSize = (8, 5)  # Number of internal corners on the chessboard
square_size = 0.03  # Size of a square in meters (30mm)
frameSize = (640, 480)  # Image resolution

# Termination criteria for corner refinement
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points for the chessboard
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboardSize[0], 0:chessboardSize[1]].T.reshape(-1, 2)
objp *= square_size

# Storage for 3D points and image points
objpoints = []  # Real-world 3D points
imgpointsL = []  # Image points from the left camera
imgpointsR = []  # Image points from the right camera

# Load and sort stereo images
imagesLeft = sorted(glob.glob('RectificationImages/stereoLeft/*.png'),
                    key=lambda x: int(re.findall(r'\d+', x.split('/')[-1])[-1]))
imagesRight = sorted(glob.glob('RectificationImages/stereoRight/*.png'),
                     key=lambda x: int(re.findall(r'\d+', x.split('/')[-1])[-1]))

if not imagesLeft or not imagesRight:
    print("No images found. Check your file paths.")
    exit(1)

if len(imagesLeft) != len(imagesRight):
    print("Error: Left and right image sets do not have the same number of images.")
    exit(1)

# Process images
for imgLeft, imgRight in zip(imagesLeft, imagesRight):
    imgL = cv.imread(imgLeft)
    imgR = cv.imread(imgRight)

    if imgL is None or imgR is None:
        print(f"Failed to load images {imgLeft} or {imgRight}")
        continue

    grayL = cv.cvtColor(imgL, cv.COLOR_BGR2GRAY)
    grayR = cv.cvtColor(imgR, cv.COLOR_BGR2GRAY)

    # Find chessboard corners
    retL, cornersL = cv.findChessboardCorners(grayL, chessboardSize, None)
    retR, cornersR = cv.findChessboardCorners(grayR, chessboardSize, None)

    if retL and retR:
        objpoints.append(objp)

        # Refine corners
        cornersL = cv.cornerSubPix(grayL, cornersL, (11, 11), (-1, -1), criteria)
        cornersR = cv.cornerSubPix(grayR, cornersR, (11, 11), (-1, -1), criteria)

        imgpointsL.append(cornersL)
        imgpointsR.append(cornersR)

        # Display detected corners (optional)
        cv.drawChessboardCorners(imgL, chessboardSize, cornersL, retL)
        cv.imshow('Left Image Corners', imgL)
        cv.drawChessboardCorners(imgR, chessboardSize, cornersR, retR)
        cv.imshow('Right Image Corners', imgR)
        cv.waitKey(300)
    else:
        print(f"Chessboard corners not found in {imgLeft} or {imgRight}")

cv.destroyAllWindows()

# Calibration
if not objpoints or not imgpointsL or not imgpointsR:
    print("Not enough data for calibration. Ensure chessboard corners were detected.")
else:
    print("Calibrating...")

    # Intrinsic calibration for each camera
    retL, cameraMatrixL, distL, _, _ = cv.calibrateCamera(objpoints, imgpointsL, frameSize, None, None)
    retR, cameraMatrixR, distR, _, _ = cv.calibrateCamera(objpoints, imgpointsR, frameSize, None, None)

    # Stereo calibration
    criteria_stereo = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    flags = 0  # cv.CALIB_FIX_INTRINSIC  # Keep intrinsic parameters fixed
    retStereo, _, _, _, _, R, T, E, F = cv.stereoCalibrate(objpoints, imgpointsL, imgpointsR, cameraMatrixL, distL,
        cameraMatrixR, distR, frameSize, criteria_stereo, flags)

    if retStereo > 1.0:  # Adjust threshold as needed
        print(f"Warning: High RMS error {retStereo}. Calibration may be inaccurate.")

    # Stereo rectification
    rectifyScale = 1  # 1 for all pixels, 0 for valid pixels only
    R1, R2, P1, P2, Q, _, _ = cv.stereoRectify(cameraMatrixL, distL, cameraMatrixR, distR, frameSize, R, T,
        alpha=rectifyScale)

    # Generate stereo maps for remapping
    stereoMapL = cv.initUndistortRectifyMap(cameraMatrixL, distL, R1, P1, frameSize, cv.CV_16SC2)
    stereoMapR = cv.initUndistortRectifyMap(cameraMatrixR, distR, R2, P2, frameSize, cv.CV_16SC2)

    # Save parameters to files
    output_dir = "../../../"  # Adjust this as needed
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save stereo maps
    stereo_map_file = os.path.join(output_dir, "stereoMap.xml")
    print(f"Saving stereo map to: {stereo_map_file}")
    cv_file = cv.FileStorage(stereo_map_file, cv.FILE_STORAGE_WRITE)
    cv_file.write('stereoMapL_x', stereoMapL[0])
    cv_file.write('stereoMapL_y', stereoMapL[1])
    cv_file.write('stereoMapR_x', stereoMapR[0])
    cv_file.write('stereoMapR_y', stereoMapR[1])
    cv_file.release()

    # Save Q matrix
    q_file = os.path.join(output_dir, "Q.xml")
    print(f"Saving Q matrix to: {q_file}")
    cv_file = cv.FileStorage(q_file, cv.FILE_STORAGE_WRITE)
    cv_file.write('Q', Q)
    cv_file.release()

    print("Calibration complete. Parameters saved.")
