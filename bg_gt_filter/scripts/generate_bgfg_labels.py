
from tqdm import tqdm
import os
import numpy as np
import json
import argparse

from scipy.spatial import KDTree
import numpy as np
from mmengine.fileio import get
from pyquaternion import Quaternion

from nuscenes.nuscenes import NuScenes



def generate_keyframes_bgfg_labels(category_json_path, lidarseg_path, lidarseg_bgfg_path):
    with open(category_json_path) as cat_file:
        categories = json.load(cat_file)

    classes = [cat['name'] for cat in categories]
    classes_idxes = [cat['index'] for cat in categories]

    BACKGROUND_CLASSES_NAMES = [
        'noise',  "movable_object.debris", "movable_object.pushable_pullable",
        "static_object.bicycle_rack", "flat.driveable_surface", "flat.other", "flat.sidewalk", "flat.terrain", "static.manmade",
        "static.other", "static.vegetation", "vehicle.ego"
    ]
    FOREGROUND_CLASSES_NAMES = []
    for class_name in classes:
        if class_name not in BACKGROUND_CLASSES_NAMES:
            FOREGROUND_CLASSES_NAMES.append(class_name)

    BACKGROUND_IDXES = []
    FOREGROUND_IDXES = []

    for category in categories:
        if category['name'] in BACKGROUND_CLASSES_NAMES:
            BACKGROUND_IDXES.append(category['index'])
        else:
            FOREGROUND_IDXES.append(category['index'])

    os.makedirs(lidarseg_bgfg_path, exist_ok=True)

    lidarseg_types = os.listdir(lidarseg_path)

    for lidarseg_type in lidarseg_types:
        print(f'Loading {lidarseg_type}...')

        lidarseg_files = os.listdir(os.path.join(lidarseg_path, lidarseg_type))
        os.makedirs(os.path.join(lidarseg_bgfg_path, lidarseg_type), exist_ok=True)

        for lidarseg_file in tqdm(lidarseg_files):
            lidarseg = np.fromfile(os.path.join(lidarseg_path, lidarseg_type, lidarseg_file), dtype=np.uint8)
            lidarseg_bgfg = np.zeros_like(lidarseg, dtype=np.uint8)

            lidarseg_bgfg[np.isin(lidarseg, BACKGROUND_IDXES)] = 0
            lidarseg_bgfg[np.isin(lidarseg, FOREGROUND_IDXES)] = 1

            lidarseg_bgfg.tofile(os.path.join(lidarseg_bgfg_path, lidarseg_type, lidarseg_file))


def generate_non_keyframes_bgfg_labels(lidarseg_bgfg_path, nuscenes_dataroot):
    lidarseg_bgfg_path = os.path.join(lidarseg_bgfg_path, 'v1.0-trainval')
    nusc = NuScenes(version='v1.0-trainval', dataroot=nuscenes_dataroot, verbose=True)

    def read_point_cloud(sample_data):
        file_path = os.path.join(nuscenes_dataroot, sample_data['filename'])
        ego_pose = nusc.get('ego_pose', sample_data['ego_pose_token'])
        pts_bytes = get(file_path, backend_args=None)
        points = np.frombuffer(pts_bytes, dtype=np.float32).reshape(-1, 5)
        return transform_points(points[:, :3], 
                                -np.array(ego_pose['translation']), 
                                Quaternion(ego_pose['rotation']).inverse)

    def read_labels(token):
        return np.fromfile(os.path.join(lidarseg_bgfg_path, f'{token}_lidarseg.bin'), dtype=np.uint8)

    def transform_points(points: np.ndarray, translation: np.ndarray, rotation: Quaternion) -> np.ndarray:
        return (rotation.rotation_matrix @ points.T).T + translation

    def get_labels_by_knn(original_point_cloud, original_labels, new_point_cloud, k=3, height_weight=1):
        
        weighted_original_point_cloud = np.copy(original_point_cloud[:, :3])
        weighted_original_point_cloud[:, 2] *= height_weight

        weighted_new_point_cloud = np.copy(new_point_cloud[:, :3])
        weighted_new_point_cloud[:, 2] *= height_weight

        tree = KDTree(weighted_original_point_cloud)
        idxes = tree.query(weighted_new_point_cloud, k=k, workers=-1)[1]
        labels = (original_labels[idxes].sum(axis=1) >= (k // 2 + 1)).astype(np.uint8)
        
        return labels

    def save_labels_from_sample(sample, k, height_weight):

        first_sample_data = nusc.get('sample_data', sample['data']['LIDAR_TOP'])
        last_sample_data = nusc.get('sample_data', nusc.get('sample', sample['next'])['data']['LIDAR_TOP'])

        first_points = read_point_cloud(first_sample_data)
        first_labels = read_labels(first_sample_data['token'])
        first_time = first_sample_data['timestamp']

        last_points = read_point_cloud(last_sample_data)
        last_labels = read_labels(last_sample_data['token'])
        last_time = last_sample_data['timestamp']

        cur_sample_data = nusc.get('sample_data', first_sample_data['next'])
        prev_points = first_points
        prev_labels = first_labels
        while cur_sample_data['timestamp'] - first_time <= last_time - cur_sample_data['timestamp']:
            points = read_point_cloud(cur_sample_data)
            labels = get_labels_by_knn(prev_points, prev_labels, points, k, height_weight)
            labels.tofile(os.path.join(lidarseg_bgfg_path, f'{cur_sample_data["token"]}_lidarseg.bin'))

            cur_sample_data = nusc.get('sample_data', cur_sample_data['next'])
            prev_points = points
            prev_labels = labels
        
        cur_sample_data = nusc.get('sample_data', last_sample_data['prev'])
        prev_points = last_points
        prev_labels = last_labels
        while cur_sample_data['timestamp'] - first_time > last_time - cur_sample_data['timestamp']:
            points = read_point_cloud(cur_sample_data)
            labels = get_labels_by_knn(prev_points, prev_labels, points, k, height_weight)
            labels.tofile(os.path.join(lidarseg_bgfg_path, f'{cur_sample_data["token"]}_lidarseg.bin'))

            cur_sample_data = nusc.get('sample_data', cur_sample_data['prev'])
            prev_points = points
            prev_labels = labels


    def save_scene_labels(scene, k, height_weight):
        sample = nusc.get('sample', scene['first_sample_token'])
        while sample['next']:
            save_labels_from_sample(sample, k, height_weight)
            sample = nusc.get('sample', sample['next'])

    for scene in tqdm(nusc.scene):
        save_scene_labels(scene, k=3, height_weight=10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate background-foreground labels for keyframes.')
    parser.add_argument('--category_json_path', type=str, default='/mmdetection3d/data/nuscenes/v1.0-trainval/category.json', help='Path to the category JSON file.')
    parser.add_argument('--lidarseg_path', type=str, default='/mmdetection3d/data/nuscenes/lidarseg', help='Path to the original lidarseg labels.')
    parser.add_argument('--lidarseg_bgfg_path', type=str, default='/mmdetection3d/data/nuscenes/lidarseg_bgfg', help='Path to save the generated background-foreground labels.')
    parser.add_argument('--nuscenes_dataroot', type=str, default='/mmdetection3d/data/nuscenes', help='Path to the NuScenes dataset root directory.')

    args = parser.parse_args()

    generate_keyframes_bgfg_labels(args.category_json_path, args.lidarseg_path, args.lidarseg_bgfg_path)
    generate_non_keyframes_bgfg_labels(args.lidarseg_bgfg_path, args.nuscenes_dataroot)