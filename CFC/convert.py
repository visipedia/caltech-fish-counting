'''
convert.py
@author justinkay

Converts a clip (sequence of frames) to its 3-channel Baseline++ version.
The three channels will be: (1) The raw image, (2) A background-subtracted version, (3) Frame-to-frame difference

Input: 
    - in_dir: input directory of where the frames are (default: current_working_directory/frames/raw/ )
    - out_dir: output directory of where you want the background-subtracted frames to live (default: current_working_directory/frames/3-channel/ )


Example command: 
python convert.py --in_dir Elwha_2018_OM_ARIS_2018_07_19_2018-07-19_080000_14_214/ --out_dir elwha_bckground_sub
'''

import argparse
import glob
import os
import numpy as np
import cv2
from PIL import Image
from tqdm import tqdm


def get_frame_idx(path):
    return int(os.path.basename(path).replace(".jpg",""))

def has_subdirectories(path):
    '''
    Returns true if the specified path has subdirectories, 
    and false otherwise
    '''
    list_dir = os.listdir(path)
    for f in list_dir:
        if os.path.isdir(os.path.join(path, f)):
            return True
    return False

def background_subtract_frames(frames, seq_out_dir):    
    frame_data = []
    for frame in frames:
        frame = cv2.imread(frame, cv2.IMREAD_GRAYSCALE)#[...,0] # grayscale; take just one channel
        frame_data.append(frame)
    frames = np.stack(frame_data)
    
    blurred_frames = frames.astype(np.float32)
    for i in range(frames.shape[0]):
        blurred_frames[i] = cv2.GaussianBlur(
            blurred_frames[i],
            (5,5),
            0
        )
    mean_blurred_frame = blurred_frames.mean(axis=0)
    blurred_frames -= mean_blurred_frame
    mean_normalization_value = np.max(np.abs(blurred_frames))
    blurred_frames /= mean_normalization_value
    blurred_frames += 1
    blurred_frames /= 2

    # Because of the frame difference channel, we only go to end_frame - 1
    for i, frame_offset in enumerate(range(len(frames) - 1)):
        frame_image = np.dstack([
                    frames[i] / 255,
                    blurred_frames[i],
                    np.abs(blurred_frames[i+1] - blurred_frames[i])
                    ]).astype(np.float32)
        frame_image = (frame_image * 255).astype(np.uint8)
        out_fp = os.path.join(seq_out_dir, f'{i}.jpg')
        Image.fromarray(frame_image).save(out_fp, quality=95)

def convert(in_dir, out_dir):
    if ( has_subdirectories ( in_dir ) ):
        for location in os.listdir(in_dir):
            loc_dir = os.path.join(in_dir, location)
            if location.startswith(".") or not os.path.isdir(loc_dir): continue
            print("Converting frames for", location)
            
            for seq in tqdm(os.listdir(loc_dir)):
                seq_dir = os.path.join(loc_dir, seq)
                if seq.startswith(".") or not os.path.isdir(seq_dir): continue
                frames = sorted(glob.glob(seq_dir + "/*.jpg"), key=get_frame_idx)
    
                seq_out_dir = os.path.join(out_dir, location, seq)
                os.makedirs(seq_out_dir, exist_ok=True)

                background_subtract_frames (frames, seq_out_dir)
    else:
        frames = sorted(glob.glob(in_dir + "/*.jpg"), key=get_frame_idx)
        os.makedirs(out_dir, exist_ok=True)
        background_subtract_frames (frames, out_dir)


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", default="frames/raw/", help="Location of frames base directory.")
    parser.add_argument("--out_dir", default="frames/3-channel/", help="Output location for converted frames.")
    return parser

if __name__ == "__main__":
    args = argument_parser().parse_args()
    convert(args.in_dir, args.out_dir)