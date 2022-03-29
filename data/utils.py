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
    
def get_annotation_fps(data_dir):
    """
    Map each location to a list of annotation filepaths, one per clip.
    
    Assumes data_dir contains two subdirectories:
        metadata/
            contains location-level metadata jsons
        annotations/
            contains clip-level annotation jsons
    
    Return: dict
        location_name -> [ list of clip annotation filepaths ]
    """
    meta = get_meta(os.path.join(data_dir, 'metadata'))
    annotation_dir = os.path.join(data_dir, 'annotations')
    
    location_to_clips = {}
    for loc in meta:
        js = json.load(open(loc, "r"))
        clips_in_loc = [ c['clip_name'] for c in js ]
        loc_name = os.path.basename(loc).replace(".json","")
        clip_fps = glob.glob(os.path.join(annotation_dir, loc_name) + "/*.json")
        location_to_clips[loc_name] = clip_fps
        
    return location_to_clips

def multi(func, args, num_cores=os.cpu_count()-1):
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