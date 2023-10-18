"""
This script includes a list of the experiments that were run, with the hyperparameters selected, in the ECCV 2022 dataset release.

File should be moved to the yolov5 directory once that is downloaded to repeat this set of experiments.
"""

from train import parse_opt
from train import main as train_main
from val import parse_opt as val_opt
from val import main as val_main
import os
import wandb
import torch

yaml_base = './yamls/'
PROJECT_NAME = "FILL ME IN"
WANDB_USER = "FILL ME IN"

# (run_name, yaml_path, task)
runs = [
    ('train_kenai_val_kenai', os.path.join(yaml_base, 'eccv_2022_dataset_release.yaml'), 'val'),
    ('train_kenai_val_elwha', os.path.join(yaml_base, 'eccv_2022_dataset_release.yaml'), 'elwha'),
    ('train_kenai_val_nushagak', os.path.join(yaml_base, 'eccv_2022_dataset_release.yaml'), 'nushagak'),
    ('train_kenai_val_channel', os.path.join(yaml_base, 'eccv_2022_dataset_release.yaml'), 'channel'),
    ('train_kenai_val_test', os.path.join(yaml_base, 'eccv_2022_dataset_release.yaml'), 'test'),
]

for i, run in enumerate(runs):
    (run_name, yaml, task) = run

    ### Train
    opt = parse_opt(True)
    opts = {
        'imgsz': 896,
        'device': '0,1',
        'weights': 'yolov5m.pt',
        'batch_size': 64,
        'epochs': 150,      # This can be changed to something lower (i.e. 20), but was originally 150 in the paper
        'project': PROJECT_NAME,

        # To be configured per run:
        'data': yaml,
        'name': run_name,
    }
    for k, v in opts.items():
        setattr(opt, k, v)
    train_main(opt)

    ### Validate
    weights_path = os.path.join(PROJECT_NAME, run_name, 'weights/best.pt')

    # Need to re-initialize the run
    api = wandb.Api()
    runs = api.runs(path=f'{WANDB_USER}/{PROJECT_NAME}')
    for run in runs:
        if run.name == run_name:
            break
    print("Resuming run", run.id, run.name)
    wandb.init(project=PROJECT_NAME, id=run.id)

    v_opt = val_opt(True)
    val_opts = {
        'imgsz': 896,
        'weights': weights_path,
        'project': PROJECT_NAME,

        # To be configured per run:
        'data': yaml,
        'task': task,
        'name': f'{run_name}_{task}',
    }
    for k, v in val_opts.items():
        setattr(v_opt, k, v)

    print(v_opt)
    r, _, t = val_main(v_opt)
    (mp, mr, map50, map, *_) = r
    wandb.log({
        f'{task}_ap50': map50
    })

    # quit this run so we can move onto the next
    wandb.run.finish()

