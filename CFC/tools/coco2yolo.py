'''
label_maker.py
@author oskarastrom

Converts a directory of coco annotations to it's Yolov5 label version.
Input: 
    - in_dir: input directory of where the coco annotations are (default: ../frames/coco_formatted_annotations/ )
    - out_dir: output directory of where you want the Yolov5 labels (default: ../frames/labels/ )


Example command: 
python coco2yolo.py --in_dir ..frames/coco_style_annotations --out_dir ../frames/labels
'''

import argparse
import os
import json

def extract_labels (data, loc_out_dir): 

    # add annotations to each image
    annotations = data['annotations']
    images = data['images']
    for ann in annotations:
        image_id = ann['image_id']
        image = images[image_id]
        if not ('annotation' in image): image['annotation'] = []
        
        # create annotation
        w = image['width']
        h = image['height']
        bb = ann['bbox']
        x_min = (bb[0]-1)/w
        y_min = (bb[1]-1)/h
        bb_w = bb[2]/w
        bb_h = bb[3]/h
        x_center = x_min + bb_w/2
        y_center = y_min + bb_h/2

        # Assert bbox is normalized between [0,1]
        if (x_min + bb_w > 1 or y_min + bb_h > 1 ):
            print("")
            print("Error")
            print(image)
            print(ann)
            print(x_min + bb_w, y_min + bb_h)
            print(x_min, bb_w, y_min, bb_h)

        label = " ".join(["0", str(x_center), str(y_center), str(bb_w), str(bb_h)])
        image['annotation'].append(label)
    
    # save annotations for each image
    for image in images:
        if (not 'annotation' in image): continue
        annotation = "\n".join(image['annotation'])

        # get output directory
        dir_name = image['dir_name']

        seq_out_dir = os.path.join(loc_out_dir, dir_name)
        if not os.path.isdir(seq_out_dir):
            os.makedirs(seq_out_dir, exist_ok=True)
        
        file_nbr = int(image['file_name'].replace(".jpg", "")) - 1
        file_name = str(file_nbr) + ".txt"

        file_path = os.path.join(seq_out_dir, file_name)
        f = open(file_path, "w")
        f.write(annotation)
        f.close()

def file_split(in_dir, out_dir):
    for location in os.listdir(in_dir):
        loc_dir = os.path.join(in_dir, location)
        loc_out_dir = os.path.join(out_dir, location)
        if location.startswith(".") or not os.path.isdir(loc_dir): continue
        print("Converting labels for", location)

        f = open(loc_dir + "/coco.json")
        data = json.load(f)
        extract_labels(data, loc_out_dir)
        f.close()


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", default="../frames/coco_formatted_annotations/", help="Location of Coco annotation directory.")
    parser.add_argument("--out_dir", default="../frames/labels/", help="Output location for Yolov5 labels.")
    return parser

if __name__ == "__main__":
    args = argument_parser().parse_args()
    file_split(args.in_dir, args.out_dir)