
import os
import argparse

import numpy as np

from flops_calc.flops_bevfusion_lidar import calc_bevfusion_lidar_flops
from flops_calc.flops_centerpoint_voxel import calc_centerpoint_voxel_flops
from flops_calc.flops_centerpoint_pillar import calc_centerpoint_pillar_flops
from flops_calc.flops_pointpillars import calc_pointpillars_flops
from flops_calc.flops_ssn import calc_ssn_flops

from mmengine.runner import Runner
from mmengine.config import Config
import os.path as osp
import torch
from tqdm import tqdm
import time
from mmengine import load
import json

import pandas as pd

import warnings

from codecarbon import EmissionsTracker

warnings.filterwarnings("ignore", category=UserWarning)


def json_converter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def get_model_path_configs(model_name, model_root_path, model_config_root_path):
    return {
        'original_config_path': os.path.join(model_config_root_path, model_name, model_name + '.py'),
        'original_model_path': os.path.join(model_root_path, model_name, model_name + '.pth'),
        
        'gt_filter_config_path': os.path.join(model_config_root_path, model_name, model_name + '_gt_filter.py'),
        'gt_filter_model_path': os.path.join(model_root_path, model_name, model_name + '_gt_filter.pth'),
    }
    

def placeholder_flops_calc(model, dataloader):
    raise NotImplementedError("FLOPs calculation function not implemented for this model yet.")


def evaluate(model_config_path, model_weights_path, calc_flops, data_prefix, load_dim=None, only_flops=False):
    cfg = Config.fromfile(model_config_path)
    cfg.log_level = 'ERROR'  # Stop printing
    cfg.work_dir = osp.join('./work_dirs',
                                    osp.splitext(osp.basename(model_config_path))[0])

    runner = Runner.from_cfg(cfg)
    runner.load_checkpoint(model_weights_path)
    model = runner.model
    model.eval()
    diff_rank_seed = runner._randomness_cfg.get('diff_rank_seed', False)
    
    cfg['val_dataloader']['batch_size'] = 1
    cfg['val_dataloader']['dataset']['data_prefix'] = data_prefix
    if load_dim is not None:
        cfg['val_dataloader']['dataset']['pipeline'][0]['load_dim'] = load_dim
    
    dataloader = runner.build_dataloader(cfg['val_dataloader'], runner.seed, diff_rank_seed=diff_rank_seed)
    
    flops_results, fps_1, predictions, per_layer_stats = calc_flops(model, dataloader)
    
    if only_flops:
        return flops_results, per_layer_stats
    
    cfg['val_dataloader']['batch_size'] = 5
    dataloader = runner.build_dataloader(cfg['val_dataloader'], runner.seed, diff_rank_seed=diff_rank_seed)
    
    times = []

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    peak_memory_allocated = 0
    peak_memory_reserved = 0

    tracker = EmissionsTracker(
        measure_power_secs=1,
        tracking_mode="process",
        gpu_ids=[0],
        save_to_file=False,
        log_level='error'
    )
    tracker.start()

    for data in tqdm(dataloader):
        with torch.no_grad():

            torch.cuda.synchronize()
            start_time = time.time()

            model.test_step(data)

            torch.cuda.synchronize()
            end_time = time.time()

            times.append(end_time - start_time)

            peak_memory_allocated = max(
                peak_memory_allocated,
                torch.cuda.max_memory_allocated()
            )

            peak_memory_reserved = max(
                peak_memory_reserved,
                torch.cuda.max_memory_reserved()
            )

    fps_5 = 1.0 / (sum(times) / len(times)) * cfg['val_dataloader']['batch_size']

    peak_memory_allocated_gb = peak_memory_allocated / (1024 ** 3)
    peak_memory_reserved_gb = peak_memory_reserved / (1024 ** 3)
    
    dataset_metric = runner.val_evaluator.metrics[0]
    dataset_metric.data_infos = load(dataset_metric.ann_file, backend_args=dataset_metric.backend_args)['data_list']
    
    results_dict = dataset_metric.compute_metrics(predictions)
    
    mAP = results_dict['pred_instances_3d_NuScenes/mAP']
    nds = results_dict['pred_instances_3d_NuScenes/NDS']

    co2_kg = tracker.stop()
    
    return flops_results, fps_1, fps_5, peak_memory_allocated_gb, peak_memory_reserved_gb, co2_kg, mAP, nds, results_dict, per_layer_stats







if __name__ == '__main__':
    
    possible_options = ['ori', 'gt_filter', '1x', '2x', '4x', '8x', '16x', '32x']
    possible_models = ['bevfusion_lidar_3dh', 'bevfusion_lidar', 'pointpillars', 'centerpoint_voxel', 'centerpoint_voxel_3dh', 'centerpoint_pillar', 'ssn']
    
    parser = argparse.ArgumentParser(description='Evaluate model FLOPs and predictions')
    parser.add_argument('--model_names', nargs='+', default=possible_models, help='Name of the models to evaluate')
    parser.add_argument('--model_root_path', type=str, default='/mmdetection3d/models/nuscenes', help='Root path for model weights')
    parser.add_argument('--model_config_root_path', type=str, default='/mmdetection3d/bg_gt_filter/configs/nuscenes', help='Root path for model configs')
    parser.add_argument('--options', nargs='+', help='Options for tests', default=possible_options)
    parser.add_argument('--results_output_dir', type=str, default='/mmdetection3d/results', help='Path to save the evaluation results CSV')
    parser.add_argument('--only_flops', action='store_true', help='Only calculate FLOPs and skip prediction evaluation')
    
    args = parser.parse_args()
    
    model_configs = {
        'bevfusion_lidar_3dh': {
            'model_name': 'bevfusion_lidar_3dh',
            'model_category': 'voxel',
            'dataset': 'nuscenes',
            'num_sweeps': 9,
            'calc_flops_func': calc_bevfusion_lidar_flops,
            **get_model_path_configs('bevfusion_lidar_3dh', args.model_root_path, args.model_config_root_path)
        },
        'bevfusion_lidar': {
            'model_name': 'bevfusion_lidar',
            'model_category': 'voxel',
            'dataset': 'nuscenes',
            'num_sweeps': 9,
            'calc_flops_func': calc_bevfusion_lidar_flops,
            **get_model_path_configs('bevfusion_lidar', args.model_root_path, args.model_config_root_path)
        },
        'pointpillars': {
            'model_name': 'pointpillars',
            'model_category': 'pillar',
            'dataset': 'nuscenes',
            'num_sweeps': 10,
            'calc_flops_func': calc_pointpillars_flops,
            **get_model_path_configs('pointpillars', args.model_root_path, args.model_config_root_path)
        },
        'centerpoint_voxel': {
            'model_name': 'centerpoint_voxel',
            'model_category': 'voxel',
            'dataset': 'nuscenes',
            'num_sweeps': 9,
            'calc_flops_func': calc_centerpoint_voxel_flops,
            **get_model_path_configs('centerpoint_voxel', args.model_root_path, args.model_config_root_path)
        },
        'centerpoint_voxel_3dh': {
            'model_name': 'centerpoint_voxel_3dh',
            'model_category': 'voxel',
            'dataset': 'nuscenes',
            'num_sweeps': 9,
            'calc_flops_func': calc_centerpoint_voxel_flops,
            **get_model_path_configs('centerpoint_voxel_3dh', args.model_root_path, args.model_config_root_path)
        },
        'centerpoint_pillar': {
            'model_name': 'centerpoint_pillar',
            'model_category': 'pillar',
            'dataset': 'nuscenes',
            'num_sweeps': 9,
            'calc_flops_func': calc_centerpoint_pillar_flops,
            **get_model_path_configs('centerpoint_pillar', args.model_root_path, args.model_config_root_path)
        },
        'ssn': {
            'model_name': 'ssn',
            'model_category': 'pillar',
            'dataset': 'nuscenes',
            'num_sweeps': 10,
            'calc_flops_func': calc_ssn_flops,
            **get_model_path_configs('ssn_regnext', args.model_root_path, args.model_config_root_path)
        }
    }
    
    if args.model_names:
        for model_name in args.model_names:
            if model_name not in model_configs:
                raise ValueError(f"Model name '{model_name}' not found in predefined configurations.")
    else:
        raise ValueError("No model names provided.")

    if args.options:
        for opt in args.options:
            if opt not in possible_options:
                raise ValueError(f"Invalid option '{opt}' provided. Valid options are: {possible_options}")
    
    model_configs = [model_configs[model_name] for model_name in args.model_names]
    
    pbar = tqdm(total=len(args.options) * len(model_configs), desc='Evaluating models')

    results = []

    for model_config in model_configs:
        model_name = model_config['model_name']
        model_category = model_config['model_category']
        dataset_name = model_config['dataset']
        num_sweeps = model_config['num_sweeps']
        calc_flops = model_config['calc_flops_func']

        model_results = []

        pbar.desc = f"Evaluating {model_name}"

        for option in args.options:
            if option == 'gt_filter':
                model_config_path = model_config['gt_filter_config_path']
                model_weights_path = model_config['gt_filter_model_path']
                data_prefix = {
                    'pts': f'samples/LIDAR_TOP_GT_FILTERED_{num_sweeps}_sweeps_1x_voxel',
                    'sweeps': ''
                }
                load_dim = None
                filter_type = '1x'
            elif option == 'ori':
                model_config_path = model_config['original_config_path']
                model_weights_path = model_config['original_model_path']
                data_prefix = {
                    'pts': 'samples/LIDAR_TOP',
                    'sweeps': 'sweeps/LIDAR_TOP',
                }
                load_dim = None
                filter_type = 'no_filter'
            elif option in ['1x', '2x', '4x', '8x', '16x', '32x']:
                model_config_path = model_config['gt_filter_config_path']
                model_weights_path = model_config['original_model_path']
                data_prefix = {
                    'pts': f'samples/LIDAR_TOP_GT_FILTERED_{num_sweeps}_sweeps_{option}_voxel',
                    'sweeps': '',
                }
                load_dim = None
                filter_type = option
                
            flops_save_dir = os.path.join(args.results_output_dir, 'flops', model_name)
            os.makedirs(flops_save_dir, exist_ok=True)
            
            if args.only_flops:
                flops_results, per_layer_stats = evaluate(
                    model_config_path, 
                    model_weights_path, 
                    calc_flops, 
                    data_prefix,
                    load_dim,
                    only_flops=True
                )
                
                for key, value in flops_results.items():
                    print(f"{key}: {value / 10 ** 9:.2f} GFLOPs")
                
                with open(os.path.join(flops_save_dir, f'{option}_per_layer_stats.json'), 'w') as f:
                    json.dump(per_layer_stats, f, indent=4, default=json_converter)
            else:
                flops_results, fps_1, fps_5, peak_memory_allocated_gb, peak_memory_reserved_gb, co2_kg, mAP, nds, results_dict, per_layer_stats = evaluate(
                    model_config_path, 
                    model_weights_path, 
                    calc_flops, 
                    data_prefix,
                    load_dim
                )
                
                metrics_save_dir = os.path.join(args.results_output_dir, 'metrics', model_name)
                os.makedirs(metrics_save_dir, exist_ok=True)
                with open(os.path.join(metrics_save_dir, f'{option}_metrics.json'), 'w') as f:
                    json.dump(results_dict, f, indent=4, default=json_converter)

                results.append({
                    'model_name': model_name,
                    'model_category': model_category,
                    'trained_on_filter': option == 'gt_filter',
                    'dataset': dataset_name,
                    'filter_type': filter_type,
                    'mAP': mAP,
                    'NDS': nds,
                    'flops': flops_results['overall'],
                    'fps_1': fps_1,
                    'fps_5': fps_5,
                    'peak_memory_allocated_gb': peak_memory_allocated_gb,
                    'peak_memory_reserved_gb': peak_memory_reserved_gb,
                    'co2_kg': co2_kg
                })

                model_results.append({
                    'model_name': model_name,
                    'model_category': model_category,
                    'trained_on_filter': option == 'gt_filter',
                    'dataset': dataset_name,
                    'filter_type': filter_type,
                    **flops_results
                })
                
                with open(os.path.join(flops_save_dir, f'{option}_per_layer_stats.json'), 'w') as f:
                    json.dump(per_layer_stats, f, indent=4, default=json_converter)

            pbar.update(1)
        
        if not args.only_flops:
            df = pd.DataFrame(model_results)
            os.makedirs(args.results_output_dir, exist_ok=True)
            os.makedirs(os.path.join(args.results_output_dir, 'flops'), exist_ok=True)
            df.to_csv(os.path.join(args.results_output_dir, 'flops', f'{model_name}.csv'), index=False)

    if not args.only_flops:
        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(args.results_output_dir, 'evaluation_results.csv'), index=False)