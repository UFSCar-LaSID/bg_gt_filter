
from mmengine.runner import Runner
from mmengine.registry.default_scope import DefaultScope

from tqdm import tqdm

from mmdet3d.models.data_preprocessors import Det3DDataPreprocessor
from mmengine.config import ConfigDict

import os
import json
import numpy as np
import argparse

DefaultScope.get_instance('task', scope_name='mmdet3d')  

class_names = [
    'car', 'truck', 'construction_vehicle', 'bus', 'trailer', 'barrier',
    'motorcycle', 'bicycle', 'pedestrian', 'traffic_cone'
]
backend_args = None
metainfo = dict(classes=class_names)


pipeline_9_sweeps = [
    dict(
        type='LoadPointsFromFile',
        coord_type='LIDAR',
        load_dim=5,
        use_dim=5,
        backend_args=backend_args),
    dict(
        type='LoadPointsFromMultiSweeps',
        sweeps_num=9,
        load_dim=5,
        use_dim=5,
        pad_empty_sweeps=True,
        remove_close=True,
        load_seg=True,
        backend_args=backend_args),
    dict(
        type='Pack3DDetInputs',
        keys=[
            'points'
        ],
        meta_keys=[
            'sample_idx', 'lidar_path'
        ])
]
pipeline_10_sweeps = [
    dict(
        type='LoadPointsFromFile',
        coord_type='LIDAR',
        load_dim=5,
        use_dim=5,
        backend_args=backend_args),
    dict(
        type='LoadPointsFromMultiSweeps',
        sweeps_num=10,
        load_seg=True,
        backend_args=backend_args),
    dict(
        type='Pack3DDetInputs',
        keys=[
            'points'
        ],
        meta_keys=[
            'sample_idx', 'lidar_path'
        ])
]

def generate_filtered_clouds(new_data_path, multiplier, dataloader_config):
    dataloader = Runner.build_dataloader(dataloader_config)
    
    data_preprocessor = Det3DDataPreprocessor(
        pad_size_divisor=32,
        voxel=True,
        voxel_layer=dict(
            max_num_points=int(75 * (multiplier ** 2)),
            point_cloud_range=[-100.0, -100.0, -6.0, 100.0, 100.0, 4.0],
            voxel_size=[0.075 * multiplier, 0.075 * multiplier, 0.2 * multiplier],
            max_voxels=(int(1_800_000 // (multiplier ** 2)), int(1_800_000 // (multiplier ** 2))),
            deterministic=True,
            filter_bg=True,
            remove_seg=False
        )
    )
    os.makedirs(new_data_path, exist_ok=True)
    bg_proportions = []
    
    i = 0

    for data in tqdm(dataloader, desc=f'Processing with multiplier {multiplier}'):
        bg_before_count = (data['inputs']['points'][0][:, -1] == 0).sum().item()
        voxels_info = data_preprocessor.voxelize([data['inputs']['points'][0].cuda()], [data['data_samples'][0]])

        num_points = voxels_info['num_points'].cpu().numpy()
        voxels = voxels_info['voxels'].cpu().numpy()

        points_after_voxelization = voxels[np.repeat(np.arange(len(num_points)), num_points), np.concatenate([np.arange(num_points[i]) for i in range(len(num_points))])]
        bg_after_count = (points_after_voxelization[:, -1] == 0).sum().item()

        filename = data['data_samples'][0].lidar_path.split('/')[-1]
        savepath = os.path.join(new_data_path, filename)

        points_after_voxelization = points_after_voxelization[:, :-1]  # Remove the segmentation label before saving
        points_after_voxelization.astype(np.float32).tofile(savepath)

        bg_proportion = bg_after_count / bg_before_count if bg_before_count > 0 else 0
        bg_proportions.append(bg_proportion)
        
        i += 1

    avg_bg_proportion = np.mean(bg_proportions)
    
    return avg_bg_proportion


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate filtered point clouds with different multipliers.')
    parser.add_argument('--multipliers', type=int, nargs='+', default=[1, 2, 4, 8, 16, 32], help='List of multipliers to apply for filtering.')
    parser.add_argument('--output_dir', type=str, default='/mmdetection3d/data/nuscenes/samples', help='Directory to save the filtered point clouds.')
    parser.add_argument('--nuscenes_dataroot', type=str, default='/mmdetection3d/data/nuscenes', help='Path to the NuScenes dataset root directory.')
    parser.add_argument('--lidarseg_prefix', type=str, default='lidarseg_bgfg/v1.0-trainval', help='Path to the original lidarseg labels.')
    parser.add_argument('--bg_proportions_output_path', type=str, default='/mmdetection3d/bg_proportions.json', help='Path to save the background proportions JSON file.')

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    lidarseg_prefix = args.lidarseg_prefix
    data_root = args.nuscenes_dataroot
    data_prefix = dict(
        pts='samples/LIDAR_TOP',
        CAM_FRONT='samples/CAM_FRONT',
        CAM_FRONT_LEFT='samples/CAM_FRONT_LEFT',
        CAM_FRONT_RIGHT='samples/CAM_FRONT_RIGHT',
        CAM_BACK='samples/CAM_BACK',
        CAM_BACK_RIGHT='samples/CAM_BACK_RIGHT',
        CAM_BACK_LEFT='samples/CAM_BACK_LEFT',
        sweeps='sweeps/LIDAR_TOP',
        pts_semantic_mask=lidarseg_prefix,
        pts_instance_mask=lidarseg_prefix,
    )

    def generate_dataloader_config(pipeline, ann_posfix):
        return dict(
            batch_size=1,
            num_workers=0,
            persistent_workers=False,
            drop_last=False,
            sampler=dict(type='DefaultSampler', shuffle=False),
            dataset=dict(
                type='NuScenesSegDataset',
                data_root=data_root,
                ann_file=f'nuscenes_infos_{ann_posfix}.pkl',
                pipeline=pipeline,
                metainfo=metainfo,
                modality=dict(use_lidar=True, use_camera=False),
                data_prefix=data_prefix,
                test_mode=True,
                load_eval_anns=True,
                box_type_3d='LiDAR',
                backend_args=backend_args)
        )

    val_dataloader_config_9_sweeps = generate_dataloader_config(pipeline_9_sweeps, 'val')
    val_dataloader_config_10_sweeps = generate_dataloader_config(pipeline_10_sweeps, 'val')

    generate_filtered_clouds(
        new_data_path=os.path.join(args.output_dir, 'LIDAR_TOP_GT_FILTERED_9_sweeps_1x_voxel'),
        multiplier=1,
        dataloader_config=generate_dataloader_config(pipeline_9_sweeps, 'train')
    )

    generate_filtered_clouds(
        new_data_path=os.path.join(args.output_dir, 'LIDAR_TOP_GT_FILTERED_10_sweeps_1x_voxel'),
        multiplier=1,
        dataloader_config=generate_dataloader_config(pipeline_10_sweeps, 'train')
    )

    results_9_sweeps = {}
    results_10_sweeps = {}

    multipliers = args.multipliers

    for multiplier in multipliers:
        results_9_sweeps[str(multiplier)] = generate_filtered_clouds(
            new_data_path=os.path.join(args.output_dir, f'LIDAR_TOP_GT_FILTERED_9_sweeps_{multiplier}x_voxel'),
            multiplier=multiplier,
            dataloader_config=val_dataloader_config_9_sweeps
        )

        # It is necessary to overwrite the use_dim every time because the pipeline modifies it in place internally.
        pipeline_10_sweeps[1]['use_dim'] = [0, 1, 2, 4]  
        val_dataloader_config_10_sweeps = generate_dataloader_config(pipeline_10_sweeps)
        results_10_sweeps[str(multiplier)] = generate_filtered_clouds(
            new_data_path=os.path.join(args.output_dir, f'LIDAR_TOP_GT_FILTERED_10_sweeps_{multiplier}x_voxel'),
            multiplier=multiplier,
            dataloader_config=val_dataloader_config_10_sweeps
        )
    
    results = {
        '9_sweeps': results_9_sweeps,
        '10_sweeps': results_10_sweeps
    }

    with open(args.bg_proportions_output_path, 'w') as f:
        json.dump(results, f, indent=4)