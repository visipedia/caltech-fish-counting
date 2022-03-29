import argparse
import os
import glob
import json
from functools import partial

from piso.didson.io import write_frames, write_frames_enhanced

from utils import multi


ONE_CHANNEL_SUBDIR = '1-channel'
THREE_CHANNEL_SUBDIR = '3-channel'

def main(args):
    
    if args.location == 'all':
        locs = glob.glob(args.meta + "/*.json")
    else:
        locs = [ args.location, ]
    
    if args.channels == 1:
        fnc = write_frames
    elif args.channels == 3:
        fnc = write_frames_enhanced
    else:
        raise NotImplemented()
            
    for loc in locs:
        print("Extracting", loc)
        clip_list =  json.load(open(loc, 'r'))
        
        # do it like a starmap - add all args to a list
        all_args = []
        for clip in clip_list:
            if args.channels == 1:
                out_d = os.path.join(args.out, ONE_CHANNEL_SUBDIR, os.path.basename(loc).replace(".json",""), clip['clip_name'])
            elif args.channels == 3:
                out_d = os.path.join(args.out, THREE_CHANNEL_SUBDIR, os.path.basename(loc).replace(".json",""), clip['clip_name'])
                
            json_f = os.path.join(args.aris, clip['aris_filename'])
            all_args.append( (json_f, out_d, clip['start_frame'], clip['end_frame']) )
        
        multi(fnc, all_args)
        
        # single threaded version for testing:
#         for arg_list in all_args:
#             fnc(*arg_list)
    
def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", default='metadata/', help="Path to metadata directory.")
    parser.add_argument("--aris", default='aris/', help="Path to ARIS directory.")
    parser.add_argument("--location", default='all', help="Which data location to extract frames for. Valid args: { all, kenai-train, kenai-val"
                        + "kenai-rightbank, kenai-channel, elwha, nushagak }")
    parser.add_argument("--out", default='frames/', help="Path to output directory for frames. Single channel frames will be written to a subdirectory 1-channel;"
                       + "three channel frames will be written to a subdirectory 3-channel. Specify which you want with the --channels argument.")
    parser.add_argument("--channels", type=int, default=1, help="How many channels for the output images. 1 channel is raw frames; 3 channels is enhanced frames from Baseline++")
    return parser

if __name__ == "__main__":
    args = argument_parser().parse_args()
    main(args)