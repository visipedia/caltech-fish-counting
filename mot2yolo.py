'''
file_split.py
@author oskarastrom

Splits the joint annotation file into frame-matching labels for Yolov5
Input: 
    - label_dir: input directory of where the labels are (default: current_working_directory/frames/annotation/ )


Example command: 
python mot2yolo.py --dir ../dataset/annotation
'''

import argparse
import glob
import os
import cv2
from tqdm import tqdm

def do_split(in_dir, out_dir, image_dir):

    # Get MOT file    
    file = glob.glob(in_dir + "/gt*.txt")
    if (len(file) == 0): return

    # Get image size to convert to normalized coordinates
    (h, w, c) = cv2.imread(image_dir + '/0.jpg', cv2.IMREAD_COLOR).shape

    # Read MOT file
    f = open(file[0])
    lines = f.readlines()
    label_dict = {}
    min_frame = float("inf")
    for line in lines:
        args = line.split(",")
        frame = int(args[0])
        if (frame < min_frame): min_frame = frame
        if (not frame in label_dict): label_dict[frame] = []

        # Assert that normalized bboxes are on [0,1] range
        if (float(args[2])/w + float(args[4])/w > 1):
            print(frame)
            print(image_dir)
            print(float(args[2])/w + float(args[4])/w)
            print(w, h)
            print(args)
        if (float(args[3])/h + float(args[5])/h > 1):
            print(frame)
            print(image_dir)
            print(float(args[3])/h + float(args[5])/h)
            print(w, h)
            print(args)

        # Create annotation row
        args[1] = "0"
        args[2] = str(float(args[2])/w)
        args[3] = str(float(args[3])/h)
        args[4] = str(float(args[4])/w)
        args[5] = str(float(args[5])/h)

        label_dict[frame].append(" ".join(args[1:6]))

    # Create annotation list and sort by frame
    label_list = []
    for frame in label_dict:
        label_list.append((frame, label_dict[frame]))
    sorted(label_list, key=lambda x : x[0])

    # Write Yolo file
    for i in range(len(label_list)):
        label =  "\n".join(label_list[i][1])
        path = os.path.join(out_dir, f'{i}.txt')
        with open(path, "w") as f2:
            f2.write(label)
    



def file_split(in_dir, out_dir, image_dir):
    for location in os.listdir(in_dir):

        # Define location folders
        in_loc_dir = os.path.join(in_dir, location)
        out_loc_dir = os.path.join(out_dir, location)
        image_loc_dir = os.path.join(image_dir, location)

        # Check that location exists in input folders
        if location.startswith(".") or not os.path.isdir(in_loc_dir): continue
        if location.startswith(".") or not os.path.isdir(image_loc_dir): continue
        print("Converting frames for", location)
        
        for seq in tqdm(os.listdir(in_loc_dir)):

            # Define Sequence folders
            label_seq_dir = os.path.join(in_loc_dir, seq)
            out_seq_dir = os.path.join(out_loc_dir, seq)
            image_seq_dir = os.path.join(image_loc_dir, seq)

            # Check that sequence exists in input folders
            if seq.startswith(".") or not os.path.isdir(label_seq_dir): continue
            if seq.startswith(".") or not os.path.isdir(image_seq_dir): continue

            # Create sequence output folder
            if not os.path.isdir(out_seq_dir):  
                os.makedirs(out_seq_dir, exist_ok=True)

            # Generate Yolo files
            do_split(label_seq_dir, out_seq_dir, image_seq_dir)


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", default="../frames/annotation/", help="Location of frames base directory.")
    parser.add_argument("--out_dir", default="../frames/labels/", help="Location of frames base directory.")
    parser.add_argument("--image_dir", default="../frames/raw/", help="Location of frames base directory.")
    return parser

if __name__ == "__main__":
    args = argument_parser().parse_args()
    file_split(args.in_dir, args.out_dir, args.image_dir)