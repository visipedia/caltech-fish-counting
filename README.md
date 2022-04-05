<img src="assets/examples.gif" width=100%>

# Caltech Fish Counting Dataset

Resources for the Caltech Fish Counting Dataset, as described in [link to paper](link to paper)

This repository includes:
- [x] Links to download the dataset and annotations
- [x] Evaluation code to reproduce our results and evaluate new algorithms
- [ ] Scripts to convert raw sonar frames into the enhanced format used by the Baseline++ method in the paper

## Data Download

Data can be downloaded from AWS using the following links.

**Training, validation, and testing images [xx GB]:** [Link to download](link to download)

- Running `md5sum` on the tar.gz file should produce: ``

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

The 3-channel frames used by our Baseline++ method can be generated using `TODO`

### Metadata

Clip-level metadata is provided for each video clip in the dataset. One JSON file is provided for each location: `kenai-train.json`, `kenai-val.json`, `kenai-rightbank.json`, `kenai-channel.json`, `nushagak.json`, and `elwha.json`. Each JSON file contains a list of dictionaries, one per video clip. Each entry contains the following metadata:

```
```

### Annotations

We provide annotations in the MOTChallenge format and use the default directory structure as described [here](https://github.com/JonathonLuiten/TrackEval/tree/master/docs/MOTChallenge-Official#data-format). After extracting the `tar.gz`, the directory structure is as follows:

```
TODO
```

Following the MOTChallenge format, each `gt.txt` file contains one entry per track per frame. Track IDs in these `.txt` files match the IDs in the provided metadata for each clip.

```
TODO
```


### Prediction Results

We provide output from our Baseline and Baseline++ methods in MOTChallenge format as well. Note that the directory structure for predictions is different from the ground truth annotations. After extracting the `tar.gz`, the directory structure is as follows:

```
```

## Repository Setup and Usage

`TODO`

### Installation

`TODO`

### Evaluation

We provide evaluation code using the [TrackEval](https://github.com/JonathonLuiten/TrackEval) codebase. We extend `TODO`

## Reference

```Bibtex for citing us```
