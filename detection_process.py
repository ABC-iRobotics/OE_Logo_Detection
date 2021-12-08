import sys
import os
import pyrealsense2 as rs
import numpy as np
import cv2
import matplotlib.pyplot as plt
import logging

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Realsense_calibration'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OE_Logo_Inference'))

from realsense_control import RealsenseController
from calibrate_camera import CameraCalibration
from predict import YOLO_v5_OE

cam_contoroller = RealsenseController()
cam_contoroller.initialize(1280, 720, 30)
img, _ = cam_contoroller.get_frames()

img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
plt.imshow(img_bgr)
plt.show()

model = YOLO_v5_OE(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OE_Logo_Inference', 'models', 'best.pt'))
model.set_loglevel(logging.DEBUG)

pred = model.predict(img_bgr)
if not pred is None:
    u, v = pred

    cam_calibration = CameraCalibration(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Realsense_calibration', 'calibration_results'))
    cam_calibration.set_loglevel(logging.WARNING)

    # Deproject 2D points to 3D
    print(cam_calibration.deproject_2d_to_3d([[u,v]], 200))



