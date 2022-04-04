import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
trackeval_dir = os.path.join(current_dir, "lib/TrackEval/")
if not trackeval_dir in sys.path: 
    sys.path.append(trackeval_dir)

import argparse
from collections import defaultdict
import copy
import glob
import json
import math
import pandas as pd
from tqdm import tqdm

from trackeval import _timing
from trackeval.metrics._base_metric import _BaseMetric


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
    
    @staticmethod
    def count(tracks, filter_dist=0.0):
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
        # map track IDs -> all dets in track
        gt_tracks = defaultdict(list)
        pred_tracks = defaultdict(list)
        
        # sort all ground truth & predicted into tracks
        for gt_ids, tracker_ids, gt_dets, tracker_dets in zip (data['gt_ids'], data['tracker_ids'], data['gt_dets'], data['tracker_dets']):
            for gti, gtd in zip(gt_ids, gt_dets):
                gt_tracks[gti].append(gtd)
            for predi, predd in zip(tracker_ids, tracker_dets):
                pred_tracks[predi].append(predd)
            
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
    
