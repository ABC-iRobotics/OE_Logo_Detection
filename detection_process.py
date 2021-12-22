import sys
import os
import pyrealsense2 as rs
import numpy as np
import cv2
import matplotlib.pyplot as plt
import logging
import argparse

from yaml import parse

## Parse command line
#
#  This function parses the command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description = 'Detection module')
    parser.add_argument(
        '-debug', dest='debug',
        help='Boolean swith to switch debug mode on and off. Default is: false (off)',
        default=False, action='store_true')
    parser.add_argument(
        '-cam_conf', dest='cam_conf',
        help='Name of the config folder storing camera calibration results, default is: "calibration_results"',
        default = 'calibration_results')
    parser.add_argument(
        '-weights', dest='weights',
        help='Name of the .pt weights file containing the weights of the trained YOLO model, default is: "best.pt"',
        default = 'best.pt')
    parser.add_argument(
        '-rob_conf', dest='rob_conf',
        help='Name of the config .yaml file containing poses, velocities and accelerations, default is: "config.yaml"',
        default = 'config.yaml')
    args = parser.parse_args()
    return args

def main(args):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Realsense_calibration'))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OE_Logo_Inference'))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OE_Logo_Robot_Control'))

    from realsense_control import RealsenseController
    from calibrate_camera import CameraCalibration
    from predict import YOLO_v5_OE
    from robot_control import URController

    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING

    # Create and initialize camera controller
    cam_contoroller = RealsenseController()
    cam_contoroller.initialize(1920, 1080, 30)

    # Create camera calibration class, load camera matrix and set logging level
    cam_calibration = CameraCalibration(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Realsense_calibration', args.cam_conf))
    cam_calibration.set_loglevel(loglevel)

    # Create the YOLO model according to trained weights
    model = YOLO_v5_OE(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OE_Logo_Inference', 'models', args.weights))
    model.set_loglevel(loglevel)

    try:
        # Create robot controller and set logging level
        robot_controller = URController(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OE_Logo_Robot_Control', 'Configs', args.rob_conf))
        robot_controller.set_loglevel(loglevel)

        # Move the robot to photo pose
        robot_controller.move_to_photo_pose()
        # Take photo to prediction
        img, _ = cam_contoroller.get_frames()
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Predict the object u,v coordinates with YOLO model
        preds = model.predict(img_bgr, return_raw_prediction=True)

        if not preds is None:
            poses = []
            # This loop calculate the poses, where the camera is above the detected objects
            for pred in preds:
                # Center of bounding box
                u = int(pred[2][0] + pred[2][2]/2)
                v = int(pred[2][1] + pred[2][3]/2)
                # Deproject 2D points to 3D
                pose_in_camera_frame = list(cam_calibration.deproject_2d_to_3d([[u,v]], robot_controller.get_camera_height())[0])

                if not pose_in_camera_frame is None:
                    # Calculates the robot tcp x,y,z position and orientation where the camera is above the object
                    pose = robot_controller.calc_above_point_for_camera(pose_in_camera_frame)
                    poses.append(pose)

            # This loop moves the camera above the earlier localized objects, detect again and pick it up
            for pose in poses:
                # Move the camera above the object
                robot_controller.go_to_pose(pose, robot_controller.above_cam_acc, robot_controller.above_cam_vel)
                # Take photo to secound prediction
                img, _ = cam_contoroller.get_frames()
                img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                # Predict the object u,v coordinates with YOLO model
                pred = model.predict(img_bgr, 1)
                if not pred is None:
                    u, v = pred
                    # Deproject 2D points to 3D 
                    pose_in_camera_frame = list(cam_calibration.deproject_2d_to_3d([[u,v]], robot_controller.get_camera_height())[0])
                    # Move the camera above the object
                    robot_controller.go_above_point_with_gripper(pose_in_camera_frame)
                    # Pick up the object
                    robot_controller.pick()
                    # Move the robot to place pose
                    robot_controller.move_to_place_pose()
                    # Place the object
                    robot_controller.place()

        # Close the connection with robot
        robot_controller.disconnect()
    except Exception as e:
        if 'robot_controller' in locals():
            # Disconnect from robot in case of error
            robot_controller.disconnect()
            logging.exception(str(e))

if __name__ == "__main__":
    args = parse_args()
    main(args)
