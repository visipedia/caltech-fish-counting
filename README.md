<img src="assets/examples.gif" width=100%>

# Caltech Fish Counting Dataset

Resources for the Caltech Fish Counting Dataset, as described in [link to paper](link to paper)

This repository includes:
- [x] Links to download the dataset and annotations
- [x] Evaluation code to reproduce our results and evaluate new algorithms
- [ ] Scripts to convert raw sonar frames into the enhanced format used by the Baseline++ method in the paper

## Data Download

Data can be downloaded from AWS using the following links.

**Training, validation, and testing images [123 GB]:** [Link to download](link to download)

- Running `md5sum` on the tar.gz file should produce: `176648e618fc5013db972aa7ded01517  fish_counting_frames.tar.gz`

**Metadata [xx MB]:** [Link to download](link to download)

**Annotations [xx MB]:** [Link to download](link to download)

## Data Format

### Images

Frames are provided as single-channel JPGs. After extracting the `tar.gz`, frames are organized as follows. Each location described in the paper -- Kenai Left Bank (training & validation), Kenai Right Bank, Kenai Channel, Nushagak, and Elwha -- has its own directory, with subdirectories for each video clip at that location.

```
frames/
    raw/
        kenai-train/
            One directory per video sequence in the training set.
                Images are named by frame index in the video clip, e.g. 0.jpg, 1.jpg ...
        kenai-val/
            One directory per video sequence in the validation set.
                0.jpg, 1.jpg ...
        kenai-rightbank/
            ...
        kenai-channel/
            ...
        nushagak/
            ...
        elwha/
            ...
```     

The 3-channel frames used by our Baseline++ method can be generated using `convert.py`:

```
python convert.py --in PATH/TO/frames --out PATH/TO/OUTPUT/DIRECTORY
```

The directory structure will be maintained.

### Metadata

Clip-level metadata is provided for each video clip in the dataset. One JSON file is provided for each location: `kenai-train.json`, `kenai-val.json`, `kenai-rightbank.json`, `kenai-channel.json`, `nushagak.json`, and `elwha.json`. Each JSON file contains a list of dictionaries, one per video clip. Each entry contains the following metadata:

```
{   // Information for a single clip
    "clip_name" :              // Unique ID for this clip; matches the name of the directory containing image frames
    "num_frames":              // Number of frames in the video clip
    "upstream_direction" :     // Either `left` or `right`
    "width":                   // Image width in pixels
    "height":                  // Image width in pixels
    "framerate":               // Video frame rate, in frames per second
    "x_meter_start":           // Meter distance from the sonar camera at x = 0
    "x_meter_stop":            // Meter distance from the sonar camera at x = width-1
    "y_meter_start":           // Meter distance from the sonar camera at y = 0
    "y_meter_stop":            // Meter distance from the sonar camera at y = height-1
}
```

### Annotations

We provide annotations in the MOTChallenge format and use the default directory structure as described [here](https://github.com/JonathonLuiten/TrackEval/tree/master/docs/MOTChallenge-Official#data-format). After extracting the `tar.gz`, the directory structure is as follows:

```
annotations/
    kenai-train/
        One directory per video sequence in the training set.
                gt.txt
    kenai-val/
        One directory per video sequence in the validation set.
                gt.txt
    kenai-rightbank/
        ...
    kenai-channel/
        ...
    nushagak/
        ...
    elwha/
        ...
```

Following the MOTChallenge format, each `gt.txt` file contains one entry per track per frame. Each line contains 10 values:

```<frame_number>, <track_id>, <bb_left>, <bb_top>, <bb_width>, <bb_height>, <conf>, <x>, <y>, <z>```

The world coordinates `x,y,z` are ignored for 2D data and are filled with -1. For ground truth tracks, `conf=-1` as well. All frame numbers, target IDs and bounding boxes are 1-indexed (i.e. the minimum `bb_left` and `bb_top` values are 1, not 0). Here is an example:

```
1, 3, 794.27, 247.59, 71.245, 174.88, -1, -1, -1, -1
1, 6, 1648.1, 119.61, 66.504, 163.24, -1, -1, -1, -1
1, 8, 875.49, 399.98, 95.303, 233.93, -1, -1, -1, -1
```


### Prediction Results

We provide output from our Baseline and Baseline++ methods in MOTChallenge format as well. Note that the directory structure for predictions is different from the ground truth annotations. After extracting the `tar.gz`, the directory structure is as follows:

```
results/
    kenai-val/
        baseline/
            data/
                One text file per clip, named {clip_name}.txt
        baseline++/
            data/
                One text file per clip, named {clip_name}.txt
    kenai-rightbank/
        ...
    kenai-channel/
        ...
    nushagak/
        ...
    elwha/
        ...
```

## Repository Setup and Usage

### Installation

Clone the repo **with submodules** to enable MOT evaluation:

```
git clone --recursive https://github.com/visipedia/caltech-fish-counting.git
// or 
git clone --recursive git@github.com:visipedia/caltech-fish-counting.git
```

If you already cloned, submodules can be retroactively intialized with:

```
git submodule init
git submodule update
```

### Evaluation

We provide evaluation code using the [TrackEval](https://github.com/JonathonLuiten/TrackEval) codebase. In addition to the [CLEAR](https://link.springer.com/article/10.1155/2008/246309) and [ID](https://arxiv.org/abs/1609.01775) tracking metrics, we extend the TrackEval codebase with a custom metric `nMAE` as described in the paper:

<img src="https://render.githubusercontent.com/render/math?math=nMAE = \frac{\frac{1}{N}\sum_{i=1}^{N} E_i}{\frac{1}{N}\sum_{i=1}^{N} \hat{z}_i} = \frac{\sum_{i=1}^{N} E_i}{\sum_{i=1}^{N} \hat{z}_i}">, 

where <img src="https://render.githubusercontent.com/render/math?math=N"> is the number of video clips, <img src="https://render.githubusercontent.com/render/math?math=E_i"> is the absolute counting error for each clip:

<img src="https://render.githubusercontent.com/render/math?math=E_i = | z_{left_i} - \hat{z}_{left_i} | \%2B | z_{right_i} - \hat{z}_{right_i} |">, 

and <img src="https://render.githubusercontent.com/render/math?math=\hat{z}_i"> is the ground truth count for clip <img src="https://render.githubusercontent.com/render/math?math=i">:

<img src="https://render.githubusercontent.com/render/math?math=\hat{z}_i = \hat{z}_{left_i} \%2B \hat{z}_{right_i}">

Run the evaluation script from the command line to reproduce the results from the paper:

```
python evaluate.py --results_dir PATH/TO/results --anno_dir PATH/TO/annotations --metadata_dir PATH/TO/metadata --tracker baseline
```
```
python evaluate.py --results_dir PATH/TO/results --anno_dir PATH/TO/annotations --metadata_dir PATH/TO/metadata --tracker baseline++
```

## Reference

```TODO: Bibtex for citing us```
