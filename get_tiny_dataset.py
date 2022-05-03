#python file to extract small dataset from huge dataset released with ECCV
import os
import shutil
import numpy as np
import json

#TODO: FILL THESE IN BEFORE RUNNING THE SCRIPT

kFramesRoot = 'path/to/frames/raw'
kTinyFramesRoot = 'path/to/frames-tiny/raw'

kAnnotationsRoot = 'path/to/annotations'
kTinyAnnotationsRoot = 'path/to/annotations-tiny'

kMetadataRoot = 'path/to/metadata'
kTinyMetadataRoot = 'path/to/metadata-tiny'

kGTFile = 'gt.txt'

kKenaiChannelName = 'kenai-channel'
kKenaiRightBankName = 'kenai-rightbank'
kKenaiTrainName = 'kenai-train'
kKenaiValName = 'kenai-val'
kNushagakName = 'nushagak'
kElwhaName = 'elwha'

assert ( os.path.exists ( kFramesRoot ), f"Directory does not exist: {kFramesRoot}")
assert ( os.path.exists ( kAnnotationsRoot ), f"Directory does not exist: {kAnnotationsRoot}" )
assert ( os.path.exists ( kMetadataRoot ), f"Directory does not exist: {kMetadataRoot}" )

kDirectoryNumber = 20 # only look at 20 directories (i.e. 20 camera recordings) at a time on a particular river
kFrameNumber = 100 # maximum number of consecutive frames to get from one clip

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

def get_frames_in_directory ( directory, all_copied_annotation_files ):
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
        frame_numbers = set([ int(line.split(',')[0]) for line in lines ])

        # find frames
        # get copied_gt_file directory name
        directory_name = os.path.basename ( os.path.dirname ( copied_gt ) )
        all_frame_files = get_files ( directory, directory_name )

        # if the frame number matches a frame number that's been annotated, add
        # it to the list of frames
        for frame_file in all_frame_files:
            frame_file_num = int ( os.path.basename ( frame_file )[0:-4] )
            if frame_file_num in frame_numbers:
                frames.append ( frame_file )

    return frames

def get_annotations_in_directory ( directory ):
    '''
    Returns a list of tiny ground truth files. 
    Used to read from tiny ground truth files to select corresponding frames next.
    '''
    tiny_gts = []
    
    annotations_dirs = get_directories ( directory );
    if len(annotations_dirs) > kDirectoryNumber:
        # get random kDirectoryNumber of directories from the list. Seed it to guarantee it's always the same
        np.random.seed(2022)
        random_indices = np.random.permutation ( kDirectoryNumber )
        annotations_dirs = [ annotations_dirs[i] for i in random_indices ]
        assert len(annotations_dirs) == kDirectoryNumber
    
    for annotation_dir in annotations_dirs:
        copied_annotation_file = os.path.join ( annotation_dir, 'gt_tiny.txt' );
        annotation_file_name = os.path.join ( annotation_dir, kGTFile );

        annotation_file_gt = open ( annotation_file_name, 'r' );
        copy_annot_file_write = open ( copied_annotation_file, 'w' );

        # read lines from gt file
        lines = annotation_file_gt.readlines()
        seen_lines = set({})
        count = 0;

        # write kFrameNumber distinct frames in tiny gt file
        while ( len(seen_lines) < kFrameNumber and count < len(lines) ): # done like this because a single frame could have multiple fish
            line = lines [ count ]
            frame_num = int ( line.split(',')[0] )

            # write line in tiny gt file
            copy_annot_file_write.write ( line )

            # update counter and seen_lines
            seen_lines.add ( frame_num )
            count += 1;
        
        # Useful for debugging
        if DEBUG:
            if ( count == len(lines) ):
                print(f'Did not reach {kFrameNumber} due to too few lines in ground truth file {annotation_file_name}. Instead got {count} frames')

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

def copy_frames ( frame_files ):
    '''
    Copy the frames from the folder containing all frames to the folder only containing 
    the tiny subset of frames (i.e. from kFramesRoot to kTinyFramesRoot )
    '''
    assert len ( frame_files ) > 0

    for f in frame_files:
        river_name, camera_and_day_name, filename = split( f )

        copied_frame_filename = os.path.join ( kTinyFramesRoot, river_name, camera_and_day_name, filename )

        # create tiny directories if they don't already exist
        os.makedirs ( os.path.dirname ( copied_frame_filename ), exist_ok=True )

        shutil.copyfile ( f, copied_frame_filename )
        if DEBUG:
            print( f'copied frame file: {copied_frame_filename}')


def move_copied_ground_truth_files ( gt_files ):
    '''
    Subsets of ground truth files were made and stored in the annotation directory.
    Now we want to move them to the kTinyAnnotationsRoot directory
    '''
    all_moved_annotation_files = []
    for a in all_copied_annotation_files:
        river_name, camera_and_day_name, filename = split( a )

        tiny_gt_filename = os.path.join ( kTinyAnnotationsRoot, river_name, camera_and_day_name, filename )
        
        # create tiny directories if they don't already exist
        os.makedirs ( os.path.dirname ( tiny_gt_filename ), exist_ok=True )

        # move file to new directory location
        os.rename ( a, tiny_gt_filename )
        all_moved_annotation_files.append ( tiny_gt_filename );
    
    return all_moved_annotation_files

def make_tiny_metadata ( annotated_files, river_name ):
    '''
    extract from the annotated_files the names of the parent directories
    these correspond to the clip_names in the metadata file
    get the metadata of the clips that we have
    '''
    clip_names = [ os.path.basename ( os.path.dirname ( f ) ) for f in annotated_files ];
    
    original_metadata_json = os.path.join ( kMetadataRoot, river_name + '.json' );
    tiny_metadata_json = os.path.join ( kTinyMetadataRoot, river_name + '.json' );

    # create tiny metadata directory if it doesn't already exist
    os.makedirs ( kTinyMetadataRoot, exist_ok=True )

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


def get_corresponding_frames_dir ( river_name ):
    return os.path.join ( kFramesRoot, river_name );

def clean_environment ( ):
    '''
    remove any currently-existing tiny directories
    '''
    if os.path.exists ( kTinyAnnotationsRoot ):
        shutil.rmtree ( kTinyAnnotationsRoot );
    if os.path.exists ( kTinyFramesRoot ):
        shutil.rmtree ( os.path.dirname ( kTinyFramesRoot ) );
    if os.path.exists ( kTinyMetadataRoot ):
        shutil.rmtree ( kTinyMetadataRoot );

if __name__ == '__main__':
    clean_environment ();

    if not DEBUG:
        print ( 'Getting annotations...')
        rivers = get_directories ( kAnnotationsRoot )
        for river in rivers:
            print ( f'River: {os.path.basename(river)}')
            # get subdirectories in annotations that match the subdirectories of the frames we have annotated
            all_copied_annotation_files = get_annotations_in_directory ( river )

            # move copies of smaller ground-truth files to tiny directories
            all_moved_annotation_files = move_copied_ground_truth_files ( all_copied_annotation_files );

            # find corresponding river in frames directory
            print ( 'Getting corresponding frames...')
            frames_river_path = get_corresponding_frames_dir ( os.path.basename ( river ) );
            all_frames_to_copy = get_frames_in_directory ( frames_river_path, all_moved_annotation_files );

            # copy frames to tiny directories
            copy_frames ( all_frames_to_copy );

            # make tiny metadata file with only the directories (aka) clip names that we have
            make_tiny_metadata ( all_moved_annotation_files, os.path.basename(river) )

    else:
        print ( f'DEBUG: getting frames and annotations from {kElwhaName} river')
        # Useful to debug just one river and a small number of frames
        all_copied_annotation_files = get_annotations_in_directory ( os.path.join ( kAnnotationsRoot, kElwhaName ) );
        all_moved_annotation_files = move_copied_ground_truth_files ( all_copied_annotation_files );

        all_frames_to_copy = get_frames_in_directory ( os.path.join ( kFramesRoot, kElwhaName ), all_moved_annotation_files );
        copy_frames ( all_frames_to_copy );

        make_tiny_metadata ( all_moved_annotation_files, kElwhaName )

