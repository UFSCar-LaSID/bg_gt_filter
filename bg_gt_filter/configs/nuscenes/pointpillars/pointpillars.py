_base_ = [
    '../../../../../configs/_base_/models/pointpillars_hv_fpn_nus.py',
    '../../../../../configs/_base_/datasets/nus-3d.py', '../../../../../configs/_base_/schedules/schedule-2x.py',
    '../../../../../configs/_base_/default_runtime.py'
]

# For nuScenes dataset, we usually evaluate the model at the end of training.
# Since the models are trained by 24 epochs by default, we set evaluation
# interval to be 24. Please change the interval accordingly if you do not
# use a default schedule.

model = dict(
    data_preprocessor=dict(
        voxel_layer=dict(deterministic=False))
)

train_cfg = dict(val_interval=24)