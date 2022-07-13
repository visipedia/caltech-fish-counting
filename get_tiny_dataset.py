'''
get_tiny_dataset.py
@author Suzanne Stathatos

Python script to extract small dataset from huge dataset released with ECCV
Script defaults to extract up to 50 consecutive frames from 20 video clips of each river 
in the dataset (note: the number of frames to be extracted should not exceed 200). 
These parameters can be adjusted through command-line arguments. File paths to existing 
data and tiny (subsetted) data will need to be provided via parameter arguments.

Example usage:
python get_tiny_dataset.py --frames_file_path /home/sstathat/Fish/frames/raw \
                           --frames_tiny_file_path /home/sstathat/Fish/frames-tiny/raw \
                           --annotation_file_path /home/sstathat/Fish/annotations \
                           --annotation_tiny_file_path /home/sstathat/Fish/annotations-tiny \
                           --metadata_file_path /home/sstathat/Fish/metadata \
                           --metadata_tiny_file_path /home/sstathat/Fish/metadata-tiny \
                           --tiny_dataset_file_path /home/sstathat/Fish/tiny_dataset (OPTIONAL)
'''
import os
import shutil
import numpy as np
import json
import argparse
import shutil 

kGTFile = 'gt.txt'
kKenaiChannelName = 'kenai-channel'
kKenaiRightBankName = 'kenai-rightbank'
kKenaiTrainName = 'kenai-train'
kKenaiValName = 'kenai-val'
kNushagakName = 'nushagak'
kElwhaName = 'elwha'

DEBUG=0

def get_directories ( directory ):
    '''
    return list of subdirectories under directory
    input:
        root directory (i.e. /home/sstathat/Fish/frames/raw)
    output:
        list of subdirectories (just 1 level below) in the root directory
    '''
    dir_list = [];
    for f in os.listdir ( directory ):
        d = os.path.join ( directory, f );
        if os.path.isdir ( d ):
            dir_list.append ( d )
    
    # sort the directory list alphabetically
    dir_list.sort()
    return dir_list

def get_files ( directory, sub_dir ):
    '''
     return all frames in subdirectory sorted from lowest-numbered frame 
     to highest-numbered frame
     input:
        directory: the river frames root directory (i.e. /home/sstathat/Fish/frames/raw/elwha )
        sub_dir: the sub-directory in the river frames directory (i.e. Elwha_2018_OM_ARIS_2018_07_09_2018-07-09_190000_490_941)
    output:
        a numerically sorted list of frames within the subdirectory
    '''

    files = []
    full_path = os.path.join ( directory, sub_dir );
    for f in os.listdir ( full_path ):
        fl = os.path.join ( full_path, f )
        if not os.path.isdir ( fl ):
            # get number associated with filename
            file_number = int( f[0:-4] )
            files.append ( [ fl, file_number] )
    
    # sort files by file number in ascending order
    files.sort ( key = lambda x: x[1] )

    # return list of only full filenames
    return [item[0] for item in files]

def check_dir_matches ( annotations_list, frames_dirs ):
    ''' 
    get the directory names from the annotations list and check that 
    they're in the frames list and vice versa
    input: 
        annotations_list: a list of the directories of annotations
        frames_list: a list of full path names of frames 
    output: 
        True if the names of the directories match, False otherwise
    '''
    af_names = set()
    for af in annotations_list:
        name = os.path.basename ( af );
        af_names.add ( name );

    frame_names = set()
    for ff in dirs:
        name = os.path.basename ( ff );
        frame_names.add ( name );

    return af_names == frame_names

def get_min_and_max( frame_files ):
    min_frame = np.inf
    max_frame = -1
    for file in frame_files:
        frame_num = get_frame_idx ( file )
        if frame_num < min_frame:
            min_frame = frame_num
        if frame_num > max_frame:
            max_frame = frame_num
    return min_frame, max_frame

def get_frame_idx(path):
    return int(os.path.basename(path).replace(".jpg",""))


def get_frames_in_directory ( directory, all_copied_annotation_files, max_frames_per_clip ):
    '''
    get a subset of frames in subdirectories within a river's root directory
    input: 
        directory: the river frames root directory
    output:
        a list of frame files that we'll use in the tiny dataset
    '''
    frames = []
    # iterate through all frames in all copied gt files and add them to the list
    # of frames
    for copied_gt in all_copied_annotation_files:
        # get frame numbers
        copied_gt_file = open ( copied_gt, 'r' );
        lines = copied_gt_file.readlines()
        annotated_frame_numbers = set([ int(line.split(',')[0]) for line in lines ])

        # find frames
        # get copied_gt_file directory name
        directory_name = os.path.basename ( os.path.dirname ( copied_gt ) )
        all_frame_files = get_files ( directory, directory_name )

        # find minimum, maximum of all frame numbers
        min_frame, max_frame = get_min_and_max ( all_frame_files )
        # find minimum, maximum annotated frame number
        min_annotated_frame = min ( annotated_frame_numbers )
        max_annotated_frame = max ( annotated_frame_numbers )

        # allow some of the first few frames to not be annotated, as it is in the larger dataset
        if ( min_annotated_frame - min_frame > int(max_frames_per_clip/4) ):
            min_frame = min_annotated_frame - int(max_frames_per_clip/4)
        max_frame = min_frame + max_frames_per_clip
        
        frame_numbers = list ( range ( min_frame, max_frame ) )

        # if the frame number matches a frame number that's been annotated, add
        # it to the list of frames
        file_numbers = []
        for frame_file in all_frame_files:
            frame_file_num = get_frame_idx ( frame_file )
            if frame_file_num in frame_numbers:
                frames.append ( frame_file )
                file_numbers.append ( frame_file_num )
        
        assert len(frame_numbers) == len(file_numbers ), f'The length of the number of frames to copy must = length of number of files. frame_numbers: {len(frame_numbers)}, file_numbers: {len(file_numbers)}'
        assert len(frame_numbers) == max_frames_per_clip, f'We should have been able to get {max_frames_per_clip} frames. Instead, we got {len(frame_numbers)}'
        assert np.allclose ( frame_numbers, file_numbers )

    return frames

def get_annotations_in_directory ( directory, frame_number, clip_number ):
    '''
    Returns a list of tiny ground truth files. 
    Used to read from tiny ground truth files to select corresponding frames next.
    '''
    tiny_gts = []
    
    annotations_dirs = get_directories ( directory );
    if len(annotations_dirs) > clip_number:
        # get random clip_number of directories from the list. Seed it to guarantee it's always the same
        np.random.seed(2022)
        random_indices = np.random.permutation ( clip_number )
        annotations_dirs = [ annotations_dirs[i] for i in random_indices ]
        assert len(annotations_dirs) == clip_number
    
    for annotation_dir in annotations_dirs:
        copied_annotation_file = os.path.join ( annotation_dir, 'gt_tiny.txt' );
        annotation_file_name = os.path.join ( annotation_dir, kGTFile );

        annotation_file_gt = open ( annotation_file_name, 'r' );
        copy_annot_file_write = open ( copied_annotation_file, 'w' );

        # read lines from gt file
        lines = annotation_file_gt.readlines()
        seen_lines = set({})
        count = 0;

        # write args.frame_number distinct frames in tiny gt file
        while ( len(seen_lines) < frame_number and count < len(lines) ): # done like this because a single frame could have multiple fish
            line = lines [ count ]
            frame_num = int ( line.split(',')[0] )

            # write line in tiny gt file
            copy_annot_file_write.write ( line )

            # update counter and seen_lines
            seen_lines.add ( frame_num )
            count += 1;
        
        # close files
        annotation_file_gt.close()
        copy_annot_file_write.close()
        tiny_gts.append ( copied_annotation_file )

    print ( "tiny_gt files written with selected frames");
    return tiny_gts

def split ( f ):
    '''
    split file path into filename, directory name, and directory's directory name
    '''
    river_name = os.path.basename ( os.path.dirname ( os.path.dirname ( f ) ) );
    camera_and_day_name = os.path.basename ( os.path.dirname ( f ) );
    filename = os.path.basename ( f )
    return river_name, camera_and_day_name, filename

def copy_frames ( frame_files, tiny_frames_root ):
    '''
    Copy the frames from the folder containing all frames to the folder only containing 
    the tiny subset of frames (i.e. from args.frames_file_path to args.frames_tiny_file_path )
    '''
    assert len ( frame_files ) > 0

    for f in frame_files:
        river_name, camera_and_day_name, filename = split( f )

        copied_frame_filename = os.path.join ( tiny_frames_root, river_name, camera_and_day_name, filename )

        # create tiny directories if they don't already exist
        os.makedirs ( os.path.dirname ( copied_frame_filename ), exist_ok=True )
        try:
            shutil.copyfile ( os.path.abspath (f), os.path.abspath ( copied_frame_filename ) )
        except:
            print ( "There was an error while copying the file")
        
        if DEBUG:
            print( f'copied frame file: {copied_frame_filename}')


def move_copied_ground_truth_files ( gt_files, tiny_annotations_root ):
    '''
    Subsets of ground truth files were made and stored in the annotation directory.
    Now we want to move them to the args.annotation_tiny_file_path directory
    '''
    all_moved_annotation_files = []
    for a in all_copied_annotation_files:
        river_name, camera_and_day_name, filename = split( a )

        tiny_gt_filename = os.path.join ( tiny_annotations_root, river_name, camera_and_day_name, filename )
        
        # create tiny directories if they don't already exist
        os.makedirs ( os.path.dirname ( tiny_gt_filename ), exist_ok=True )

        # move file to new directory location
        os.rename ( a, tiny_gt_filename )
        all_moved_annotation_files.append ( tiny_gt_filename );
    
    return all_moved_annotation_files

def make_tiny_metadata ( annotated_files, river_name, metadata_root, tiny_metadata_root ):
    '''
    extract from the annotated_files the names of the parent directories
    these correspond to the clip_names in the metadata file
    get the metadata of the clips that we have
    '''
    clip_names = [ os.path.basename ( os.path.dirname ( f ) ) for f in annotated_files ];
    
    original_metadata_json = os.path.join ( metadata_root, river_name + '.json' );
    tiny_metadata_json = os.path.join ( tiny_metadata_root, river_name + '.json' );

    # create tiny metadata directory if it doesn't already exist
    os.makedirs ( tiny_metadata_root, exist_ok=True )

    metadata_file = open ( original_metadata_json, "r" )
    tiny_metadata_file = open( tiny_metadata_json, "w");

    all_data = json.load( metadata_file )

    subset_data = []
    for clip in clip_names:
        result = [x for x in all_data if x["clip_name"] == clip]
        assert ( len(result) == 1 )
        subset_data.append ( result[0] )
    
    # write to tiny metadata file
    json.dump ( subset_data, tiny_metadata_file );

    # close file handle
    tiny_metadata_file.close()
    metadata_file.close()


def get_corresponding_frames_dir ( river_name, frames_root_path ):
    return os.path.join ( frames_root_path, river_name );


def clean_environment ( args ):
    '''
    remove any currently-existing tiny directories
    '''
    if os.path.exists ( args.annotation_tiny_file_path ):
        shutil.rmtree ( args.annotation_tiny_file_path );
    if os.path.exists ( args.frames_tiny_file_path ):
        shutil.rmtree ( os.path.dirname ( args.frames_tiny_file_path ) );
    if os.path.exists ( args.metadata_tiny_file_path ):
        shutil.rmtree ( args.metadata_tiny_file_path );


def parse_args ():
    '''
    Pass existing frames directory, annotations directory, and metadata directory in as arguments. 
    Also specify where you want the tiny (subsetted) dataset of frames, annotations, and metadata to be
    '''
    parser = argparse.ArgumentParser ( "Argument parser separating large fish counting dataset into toy dataset" );
    parser.add_argument ( '-f', '--frames_file_path', help='the complete path to the raw frame directory, i.e. /path/to/frames/raw')
    parser.add_argument ( '-t', '--frames_tiny_file_path', help='the complete path to where the tiny subset of frames will go, i.e. /path/to/frames-tiny/raw')
    parser.add_argument ( '-a', '--annotation_file_path', help='the complete path to the directory of annotations, i.e. /path/to/annotations')
    parser.add_argument ( '-u', '--annotation_tiny_file_path', help='the complete path to where the tiny subset of annotations will be, i.e. /path/to/annotations-tiny')
    parser.add_argument ( '-m', '--metadata_file_path', help='the complete path to the directory of metadata, i.e. /path/to/metadata')
    parser.add_argument ( '-v', '--metadata_tiny_file_path', help='the complete path to where the small subset of metadata will be, i.e. /path/to/metadata-tiny')
    parser.add_argument ( '-o', '--tiny_dataset_file_path', help='the directory under which all subdirectories (i.e. frames, annotations, metadata) will live, i.e. /path/to/tiny_dataset', default='')

    parser.add_argument ( '-n', '--frame_number', help='the maximum number of consecutive frames to get from one clip', default=50)
    parser.add_argument ( '-d', '--clip_number', help='the number of unique camera recordings to extract frames from on every river', default=20)

    return parser.parse_args()

def valid_args ( args ):
    '''
    Checks that the metadata, frames, and annotations paths provided by the arguments exist and checks that valid
    numbers are passed in for the number of frames within each subdirectory to copy and the number of clips to copy
    Returns true is all arguments are valid, false otherwise
    '''
    return ( os.path.exists ( args.frames_file_path ) and 
         os.path.exists ( args.annotation_file_path ) and
         os.path.exists ( args.metadata_file_path ) and
         args.frame_number > 0 and args.frame_number < 200 and 
         args.clip_number > 0 )


def move_directories ( args ):
    '''
    Move the metadata-tiny, annotations-tiny, and frames-tiny directories to a specified parent directory
    '''
    # remove tiny_dataset directory if it already exists
    if ( os.path.exists (args.tiny_dataset_file_path ) ):
        shutil.rmtree ( args.tiny_dataset_file_path)
    
    to_move = [ args.metadata_tiny_file_path, args.annotation_tiny_file_path, args.frames_tiny_file_path ]
    for tiny_dir in to_move:
        name = os.path.basename ( tiny_dir )
        destination = os.path.join ( args.tiny_dataset_file_path, name )
        dest = shutil.move ( os.path.abspath(tiny_dir), os.path.abspath(destination) )
        if ( os.path.abspath(dest) != os.path.abspath(destination) ):
            print ( f'Something went wrong moving {os.path.abspath(tiny_dir)} to {os.path.abspath(destination)}. Instead, was moved to {dest}') 

if __name__ == '__main__':
    args = parse_args()

    assert valid_args ( args ),  "One of the arguments provided was invalid"

    clean_environment ( args );
    if ( args.frames_tiny_file_path[-1] != '/' ):
        args.frames_tiny_file_path += '/'

    print (f'tiny file path {os.path.abspath(args.frames_tiny_file_path)}')

    os.makedirs ( os.path.abspath(args.frames_tiny_file_path), exist_ok=True )

    if not DEBUG:
        print ( 'Getting annotations...')
        rivers = get_directories ( args.annotation_file_path )
        for river in rivers:
            print ( f'River: {os.path.basename(river)}')
            # get subdirectories in annotations that match the subdirectories of the frames we have annotated
            all_copied_annotation_files = get_annotations_in_directory ( river, args.frame_number, args.clip_number )

            # move copies of smaller ground-truth files to tiny directories
            all_moved_annotation_files = move_copied_ground_truth_files ( all_copied_annotation_files, args.annotation_tiny_file_path );

            # find corresponding river in frames directory
            print ( 'Getting corresponding frames...')
            frames_river_path = get_corresponding_frames_dir ( os.path.basename ( river ), args.frames_file_path );
            all_frames_to_copy = get_frames_in_directory ( frames_river_path, all_moved_annotation_files, args.frame_number );

            # copy frames to tiny directories
            copy_frames ( all_frames_to_copy, args.frames_tiny_file_path );

            # make tiny metadata file with only the directories (aka) clip names that we have
            make_tiny_metadata ( all_moved_annotation_files, os.path.basename(river), args.metadata_file_path, args.metadata_tiny_file_path )

    else:
        print ( f'DEBUG: getting frames and annotations from {kElwhaName} river')
        # Useful to debug just one river and a small number of frames
        all_copied_annotation_files = get_annotations_in_directory ( os.path.join ( args.annotation_file_path, kElwhaName ), args.frame_number, args.clip_number );
        all_moved_annotation_files = move_copied_ground_truth_files ( all_copied_annotation_files, args.annotation_tiny_file_path );

        all_frames_to_copy = get_frames_in_directory ( os.path.join ( args.frames_file_path, kElwhaName ), all_moved_annotation_files, args.frame_number );
        copy_frames ( all_frames_to_copy, args.frames_tiny_file_path );

        make_tiny_metadata ( all_moved_annotation_files, kElwhaName, args.metadata_file_path, args.metadata_tiny_file_path )

    # if this option is specified, move all the subdirectories into here
    if ( args.tiny_dataset_file_path != '' ):
        move_directories ( args )