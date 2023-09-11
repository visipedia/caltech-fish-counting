import argparse
from collections import defaultdict
import json
import math
import os
import sys

# TrackEval imports - make sure the repo is correctly cloned at lib/TrackEval
current_dir = os.path.dirname(os.path.realpath(__file__))
trackeval_dir = os.path.join(current_dir, "lib/TrackEval/")
if not trackeval_dir in sys.path: sys.path.append(trackeval_dir)
import trackeval
from trackeval import _timing
from trackeval.metrics._base_metric import _BaseMetric


def norm(bbox, w, h):
    """
    Convert a bounding box from un-normalized, 1-indexed (MOT format) to 
    normalized, 0-indexed.
    
    Args:
        bbox: list of length 4, [x,y,w,h] 1-indexed.
        w: image width
        h: image height
    """
    bb = bbox.copy()
    bb = [ (bb[0] - 1) / w, (bb[1] - 1) / h, bb[2] / w, bb[3] / h ]
    return bb

class nMAE(_BaseMetric):
    """
    A TrackEval-compatible metric for normalized Mean Absolute Error (nMAE).
    """
    
    def __init__(self, config=None, filter_dist=0.05):
        super().__init__()
        self.plottable = False
        self.integer_fields = ['nMAE_numer', 'nMAE_denom']
        self.float_fields = ['nMAE']
        self.summary_fields = self.fields = self.integer_fields + self.float_fields
        self.filter_dist = filter_dist
        self.seq_dims = config['SEQ_DIMS']
    
    @staticmethod
    def count(tracks, filter_dist=0.05):
        """
        Args:
            tracks: dict, { track_id -> [bbox0, bbox1, ...] }
                    bboxes must be **normalized** to height and width of frame
            filter_dist: float, normalized minimum distance to be considered a valid track.
                                (used to filter stationary fish)
        Return:
            tuple, (right_count, left_count)
        """
        left = 0
        right = 0
        for track in tracks.values():
            start = track[0]
            end = track[-1]
            
            # get centers (dets are [x,y,w,h])
            x0 = start[0] + (start[2]/2.0)
            x1 = end[0] + (end[2]/2.0)
            
            # filter out stationary fish
            if filter_dist > 0:
                y0 = start[1] + (start[3]/2.0)
                y1 = end[1] + (end[3]/2.0)
                dist = math.sqrt((x1-x0)**2 + (y1-y0)**2)
                if dist < filter_dist:
                    continue
            
            if x0 < 0.5 and x1 >= 0.5:
                right += 1
            elif x0 >= 0.5 and x1 < 0.5:
                left += 1
                
        return (right, left)
    
    @_timing.time
    def eval_sequence(self, data):
        w, h = self.seq_dims[data['seq']]
        # map track IDs -> all dets in track
        gt_tracks = defaultdict(list)
        pred_tracks = defaultdict(list)
        
        # sort all ground truth & predicted into tracks
        for gt_ids, tracker_ids, gt_dets, tracker_dets in zip (data['gt_ids'], data['tracker_ids'], data['gt_dets'], data['tracker_dets']):
            for gti, gtd in zip(gt_ids, gt_dets):
                gt_tracks[gti].append(norm(gtd, w, h))
            for predi, predd in zip(tracker_ids, tracker_dets):
                pred_tracks[predi].append(norm(predd, w, h))
            
        gt_right, gt_left = self.count(gt_tracks, self.filter_dist)
        pred_right, pred_left = self.count(pred_tracks, self.filter_dist)
            
        return {
            'nMAE_numer': abs(pred_right - gt_right) + abs(pred_left - gt_left),
            'nMAE_denom': gt_right + gt_left,
            'nMAE': -1 # no per-sequence nMAE
        }
    
    def combine_sequences(self, all_res):
        nmae_top = sum([res['nMAE_numer'] for res in all_res.values()])
        nmae_bot = sum([res['nMAE_denom'] for res in all_res.values()])
        return {
            'nMAE_numer': nmae_top,
            'nMAE_denom': nmae_bot,
            'nMAE': nmae_top / nmae_bot
        }

    def combine_classes_class_averaged(self, all_res, ignore_empty_classes=False):
        pass

    def combine_classes_det_averaged(self, all_res):
        pass
    
def get_default_ds_config(anno_dir, trackers_dir, tracker_name='baseline'):
    """
    Get a TrackEval dataset config for MOT tracking predictions.
    Args:
        anno_dir: Directory of ground truth MOT annotations for this location. E.g. 'annotations/kenai-val/'
        trackers_dir: Directory of trackers for this location. E.g. 'results/kenai-val/baseline/'
        tracker_name: The tracker to evaluate. There should exist a directory with the same name within trackers_dir.
    """
    dataset_config = trackeval.datasets.MotChallenge2DBox.get_default_dataset_config()
    dataset_config['GT_FOLDER'] = anno_dir
    dataset_config['TRACKERS_FOLDER'] = trackers_dir
    dataset_config['TRACKERS_TO_EVAL'] = [tracker_name,]
    dataset_config['SKIP_SPLIT_FOL'] = True
    
    dataset_config['GT_LOC_FORMAT'] = '{gt_folder}/{seq}/gt.txt'
    dataset_config['DO_PREPROC'] = False
    dataset_config['PRINT_CONFIG'] = False
    return dataset_config

def get_default_eval_config(quiet=False):
    eval_config = trackeval.Evaluator.get_default_eval_config()
    eval_config['DISPLAY_LESS_PROGRESS'] = True
    eval_config['TIME_PROGRESS'] = False
    
    # parallelization in TrackEval is only within clips
    # this offers speedup on MOTChallenge dataset; not really on ours
    # because our clips are much shorter
    eval_config['USE_PARALLEL'] = False
    eval_config['NUM_PARALLEL_CORES'] = 1
    
    eval_config['PRINT_ONLY_COMBINED'] = not quiet
    eval_config['PRINT_RESULTS'] = not quiet
    eval_config['PRINT_CONFIG'] = not quiet
    return eval_config

def get_default_metrics_config():
    return {'METRICS': ['CLEAR', 'Identity', 'HOTA', 'nMAE'], 'THRESHOLD': 0.5}

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

def evaluate(results_dir, anno_dir, metadata_dir, tracker_name, quiet, iou_thresh=0.5):
    meta = get_meta(metadata_dir)
    
    results = {}
    for meta_f in meta:
        if 'train' in meta_f: continue
        location = os.path.basename(meta_f).replace(".json","")
        print("Evaluating MOT results on", location)
        
        # construct one 'dataset' per location, containing all sequences
        dataset_list = []
        loc_anno_dir = os.path.join(anno_dir, location)
        loc_trackers_dir = os.path.join(results_dir, location)
        dataset_config = get_default_ds_config(loc_anno_dir, loc_trackers_dir, tracker_name)
        eval_config = get_default_eval_config(quiet=quiet)
        metrics_config = get_default_metrics_config()
        metrics_config['THRESHOLD'] = iou_thresh
        metrics_config['PRINT_CONFIG'] = False
        
        with open(meta_f, "r") as f: 
            js = json.load(f)
            dataset_config['SEQ_INFO'] = { c['clip_name'] : c['num_frames'] for c in js }
            metrics_config['SEQ_DIMS'] = { c['clip_name'] : (c['width'], c['height']) for c in js}
        
        dataset_list.append(trackeval.datasets.MotChallenge2DBox(dataset_config))
        evaluator = trackeval.Evaluator(eval_config)
        metrics_list = []
        for metric in [trackeval.metrics.HOTA, trackeval.metrics.CLEAR, trackeval.metrics.Identity, trackeval.metrics.VACE, nMAE]:
            if metric.get_name() in metrics_config['METRICS']:
                metrics_list.append(metric(metrics_config))
                
        # run evaluation
        output_res, output_msg = evaluator.evaluate(dataset_list, metrics_list)
        results[meta_f] = output_res
        
    return output_res
    
def eval_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="results", help="Location of results directory. Should contain subdirectories kenai-val, kenai-rightbank, etc.")
    parser.add_argument("--anno_dir", default="annotations", help="Location of ground truth annotations in MOTChallenge format.")
    parser.add_argument("--metadata_dir", default="metadata", help="Location of ground truth annotations in MOTChallenge format.")
    parser.add_argument("--tracker", default="baseline", help="Name of tracker to evaluate. MOT results for each location should be in {results_dir}/{location_name}/{tracker}/data")
    parser.add_argument("--quiet", action="store_true")
    return parser

if __name__ == "__main__":
    args = eval_argument_parser().parse_args()
    evaluate(args.results_dir, args.anno_dir, args.metadata_dir, args.tracker, args.quiet)
