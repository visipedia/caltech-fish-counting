import os
import json
import glob
from multiprocessing import Pool
from tqdm import tqdm


def get_meta(metadata_dir='metadata'):
    """
    Get all metadata filepaths.
    """
    return [
            os.path.join(metadata_dir, 'kenai-train.json'),
            os.path.join(metadata_dir, 'kenai-val.json'),
            os.path.join(metadata_dir, 'kenai-rightbank.json'),
            os.path.join(metadata_dir, 'kenai-channel.json'),
            os.path.join(metadata_dir, 'nushagak.json'),
            os.path.join(metadata_dir, 'elwha.json'),
        ]
    
def get_annotation_fps(metadata_dir='metadata', annotation_dir='annotations'):
    """
    Map each location to a list of annotation filepaths, one per clip.
    
    Return: dict
        location_name -> [ list of clip annotation filepaths ]
    """
    meta = get_meta(metadata_dir)
    
    location_to_clips = {}
    for loc in meta:
        js = json.load(open(loc, "r"))
        clips_in_loc = [ c['clip_name'] for c in js ]
        loc_name = os.path.basename(loc).replace(".json","")
        clip_fps = glob.glob(os.path.join(annotation_dir, loc_name) + "/*.json")
        location_to_clips[loc_name] = clip_fps
        
    return location_to_clips

def get_annotation_fps_mot(metadata_dir='metadata', annotation_dir='annotations'): #annotation_dir, dumps, tracker_name, use_v2=False):
    meta = get_meta(metadata_dir)
    
    location_to_clips = {}
    for loc in meta:
        js = json.load(open(loc, "r"))
        clips_in_loc = [ c['clip_name'] for c in js ]
        loc_name = os.path.basename(loc).replace(".json","")
#         clip_fps = glob.glob(os.path.join(annotation_dir, loc_name) + "/*.json")
        
        
        jsons = glob.glob(annotation_dir+"/*"+loc_name+f"*/{tracker_name}/*.json")
        clip_fps = [ j for j in jsons if os.path.basename(j).split(".")[0] in clips_in_dump ]
        
        location_to_clips[loc_name] = clip_fps
    return batch_to_clips

def multi(func, args, num_cores=min(32, max(0, os.cpu_count()-1))):
    """
    Run multiprocessing with a progress bar.
    
    args: list of args, one per function call.
            for starmap functionality, pass a list of tuples
    """
    with tqdm(total=len(args), desc='Running apply_async on '+str(len(args))+' arguments') as pbar:
        with Pool(num_cores) as pool:
            def callback(*args):
                pbar.update()
                return
            results = [ pool.apply_async(func, arg, callback=callback) for arg in args ]
            print('Awaiting', len(results), 'results')
            results = [ r.get() for r in results ]