_base_ = [
    '../../../../../configs/_base_/models/pointpillars_hv_fpn_nus.py',
    '../../../../../configs/_base_/datasets/nus-3d.py', '../../../../../configs/_base_/schedules/schedule-2x.py',
    '../../../../../configs/_base_/default_runtime.py'
]

data_root = 'data/nuscenes/'
train_cfg = dict(val_interval=24)
point_cloud_range = [-50, -50, -5, 50, 50, 3]
class_names = [
    'car', 'truck', 'trailer', 'bus', 'construction_vehicle', 'bicycle',
    'motorcycle', 'pedestrian', 'traffic_cone', 'barrier'
]
backend_args = None

data_prefix = dict(
    pts='samples/LIDAR_TOP_GT_FILTERED_10', 
    img='', 
    sweeps=''
)

model = dict(
    data_preprocessor=dict(
        voxel_layer=dict(deterministic=False))
)

train_pipeline = [
    dict(
        type='LoadPointsFromFile',
        coord_type='LIDAR',
        load_dim=4,
        use_dim=4,
        backend_args=backend_args),
    #dict(
    #    type='LoadPointsFromMultiSweeps',
    #    sweeps_num=10,
    #    backend_args=backend_args),
    dict(type='LoadAnnotations3D', with_bbox_3d=True, with_label_3d=True),
    dict(
        type='GlobalRotScaleTrans',
        rot_range=[-0.3925, 0.3925],
        scale_ratio_range=[0.95, 1.05],
        translation_std=[0, 0, 0]),
    dict(type='RandomFlip3D', flip_ratio_bev_horizontal=0.5),
    dict(type='PointsRangeFilter', point_cloud_range=point_cloud_range),
    dict(type='ObjectRangeFilter', point_cloud_range=point_cloud_range),
    dict(type='ObjectNameFilter', classes=class_names),
    dict(type='PointShuffle'),
    dict(
        type='Pack3DDetInputs',
        keys=['points', 'gt_bboxes_3d', 'gt_labels_3d'])
]
test_pipeline = [
    dict(
        type='LoadPointsFromFile',
        coord_type='LIDAR',
        load_dim=4,
        use_dim=4,
        backend_args=backend_args),
    #dict(
    #    type='LoadPointsFromMultiSweeps',
    #    sweeps_num=10,
    #    test_mode=True,
    #    backend_args=backend_args),
    dict(
        type='MultiScaleFlipAug3D',
        img_scale=(1333, 800),
        pts_scale_ratio=1,
        flip=False,
        transforms=[
            dict(
                type='GlobalRotScaleTrans',
                rot_range=[0, 0],
                scale_ratio_range=[1., 1.],
                translation_std=[0, 0, 0]),
            dict(type='RandomFlip3D'),
            dict(
                type='PointsRangeFilter', point_cloud_range=point_cloud_range)
        ]),
    dict(type='Pack3DDetInputs', keys=['points'])
]
# construct a pipeline for data and gt loading in show function
# please keep its loading function consistent with test_pipeline (e.g. client)
eval_pipeline = [
    dict(
        type='LoadPointsFromFile',
        coord_type='LIDAR',
        load_dim=5,
        use_dim=5,
        backend_args=backend_args),
    #dict(
    #    type='LoadPointsFromMultiSweeps',
    #    sweeps_num=10,
    #    test_mode=True,
    #    backend_args=backend_args),
    dict(type='Pack3DDetInputs', keys=['points'])
]

train_dataloader = dict(
    batch_size=4,
    num_workers=4,
    dataset=dict(data_root=data_root, data_prefix=data_prefix, pipeline=train_pipeline, metainfo=dict(classes=class_names)))
test_dataloader = dict(
    dataset=dict(data_root=data_root, data_prefix=data_prefix, pipeline=test_pipeline, metainfo=dict(classes=class_names)))
val_dataloader = dict(
    dataset=dict(data_root=data_root, data_prefix=data_prefix, pipeline=test_pipeline, metainfo=dict(classes=class_names)))