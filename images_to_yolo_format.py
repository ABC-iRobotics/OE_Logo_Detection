import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


def parse_args():

    import argparse

    parser = argparse.ArgumentParser(
        description = 'Create YOLO format from masks')
    parser.add_argument(
        '-dir', dest='directory',
        help='Relative path to the directory containing the images',
        default='imgs', type=str)

    args = parser.parse_args()
    return args


def main(args):
    annotations_path = args.directory

    if 'yolo_data' not in os.listdir(annotations_path):
        os.makedirs(os.path.join(annotations_path,'yolo_data'))

    render_results = os.listdir(annotations_path)
    annotations = [filename for filename in render_results if 'annotation' in filename]
    annotations.sort()

    PATHS = [os.path.join(annotations_path, filename) for filename in annotations]
    img_res = (1080,1920, 3)

    for PATH in PATHS:
        print(PATH)
        mask = np.array(Image.open(PATH).getdata())
        colors = np.unique(mask, axis=0)

        fig, ax = plt.subplots()

        bounding_boxes = []

        with open(os.path.join(annotations_path, 'yolo_data', PATH.split(os.sep)[-1].replace('_annotation.png', '.txt')), 'w') as f:
            for color in colors:
                if color[0:3].any():
                    x_min = (np.where(np.all(mask==color, axis=1))[0]%1920).min()
                    x_max = (np.where(np.all(mask==color, axis=1))[0]%1920).max()
                    y_min = (np.where(np.all(mask==color, axis=1))[0]//1920).min()
                    y_max = (np.where(np.all(mask==color, axis=1))[0]//1920).max()


                    width = x_max-x_min
                    height = y_max-y_min

                    x_center = x_min + width/2
                    y_center = y_min + height/2

                    yolo_format = [str(val) for val in [0,x_center/img_res[1],y_center/img_res[0],width/img_res[1],height/img_res[0]]]
                    

                    bounding_boxes.append((x_min, x_max, y_min, y_max))
                    f.write(' '.join(yolo_format)+'\n')

        ax.imshow(np.reshape(np.array(Image.open(PATH.replace('_annotation', '')).getdata())[:,0:3],img_res))

        for bounding_box in bounding_boxes:
            rect = patches.Rectangle((bounding_box[0], bounding_box[2]), bounding_box[1]-bounding_box[0], bounding_box[3]-bounding_box[2], linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

        plt.axis('off')
        plt.savefig(os.path.join(annotations_path, 'yolo_data', PATH.split(os.sep)[-1]))

if __name__ == "__main__":
    args = parse_args()
    main(args)