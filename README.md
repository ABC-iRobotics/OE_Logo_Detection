# OE Logo Detection
Repository for collecting code related to the OE logo detection project.

## Usage
 - Use OE_Logo_BAT submodule to generate synthetic data
 - Use the yolov5 sumbodule to train YOLO model on the synthetic data
 - Use OE_Logo_Inference submodule to make predictions with the trained YOLO model
 - Use Realsense_calibration submodule to calibrate and control the RealSense camera
 - Use python-urx and OE_Logo_Robot_Control submodules to control the UR robot

The python module detection_process.py performes the picking process with the real robot using the trained YOLO model.