'''
file_split.py
@author oskarastrom

Splits the joint annotation file into frame-matching labels for Yolov5
Input: 
    - dir: input directory of where the labels are (default: current_working_directory/frames/annotation/ )


Example command: 
python file_split.py --dir ../dataset/annotation
'''

import argparse
import glob
import os
import cv2
from tqdm import tqdm

def do_split(label_dir, image_dir):    
    file = glob.glob(label_dir + "/gt*.txt")
    if (len(file) == 0): return

    # Get image size to convert to normalized coordinates
    (h, w, c) = cv2.imread(image_dir + '/0.jpg', cv2.IMREAD_COLOR).shape
    #print(image_dir, w, h)

    f = open(file[0])
    lines = f.readlines()
    label_dict = {}
    min_frame = float("inf")
    for line in lines:
        args = line.split(",")
        frame = int(args[0])
        if (frame < min_frame): min_frame = frame
        if (not frame in label_dict): label_dict[frame] = []
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

        args[1] = "0"
        args[2] = str(float(args[2])/w)
        args[3] = str(float(args[3])/h)
        args[4] = str(float(args[4])/w)
        args[5] = str(float(args[5])/h)

        label_dict[frame].append(" ".join(args[1:6]))

    label_list = []
    for frame in label_dict:
        label_list.append((frame, label_dict[frame]))
    sorted(label_list, key=lambda x : x[0])

    for i in range(len(label_list)):
        label =  "\n".join(label_list[i][1])
        path = os.path.join(label_dir, f'{i}.txt')
        with open(path, "w") as f2:
            f2.write(label)
    



def file_split(label_dir, image_dir):
    for location in os.listdir(label_dir):
        label_loc_dir = os.path.join(label_dir, location)
        image_loc_dir = os.path.join(image_dir, location)
        if location.startswith(".") or not os.path.isdir(label_loc_dir): continue
        if location.startswith(".") or not os.path.isdir(image_loc_dir): continue
        print("Converting frames for", location)
        
        for seq in tqdm(os.listdir(label_loc_dir)):
            label_seq_dir = os.path.join(label_loc_dir, seq)
            image_seq_dir = os.path.join(image_loc_dir, seq)
            if seq.startswith(".") or not os.path.isdir(label_seq_dir): continue
            if seq.startswith(".") or not os.path.isdir(image_seq_dir): continue
            do_split(label_seq_dir, image_seq_dir)


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label_dir", default="frames/annotation/", help="Location of frames base directory.")
    parser.add_argument("--image_dir", default="frames/raw/", help="Location of frames base directory.")
    return parser

if __name__ == "__main__":
    args = argument_parser().parse_args()
    file_split(args.label_dir, args.image_dir)