
import os
import numpy as np
from tqdm import tqdm

samples_folder_ori = '/mmdetection3d/data/nuscenes/samples'
samples_folder_new = '/mmdetection3d/data/nuscenes/samples_2'

for folder_name in sorted(os.listdir(samples_folder_new)):
    new_folder_path = os.path.join(samples_folder_new, folder_name)
    ori_folder_path = os.path.join(samples_folder_ori, folder_name)

    if "9_sweeps" in folder_name:
        points_dim = 5
    elif "10_sweeps" in folder_name:
        points_dim = 4

    files_ori = sorted(os.listdir(ori_folder_path))
    files_new = sorted(os.listdir(new_folder_path))

    assert len(files_ori) == len(files_new), f"Number of files in {folder_name} do not match: {len(files_ori)} vs {len(files_new)}"

    for file_ori, file_new in tqdm(zip(files_ori, files_new), total=len(files_ori), desc=f"Processing {folder_name}"):
        assert file_ori == file_new, f"File names do not match: {file_ori} vs {file_new}"

        ori_file_path = os.path.join(ori_folder_path, file_ori)
        new_file_path = os.path.join(new_folder_path, file_new)

        ori_points = np.fromfile(ori_file_path, dtype=np.float32).reshape(-1, points_dim+1)
        ori_points = ori_points[:, :points_dim]
        new_points = np.fromfile(new_file_path, dtype=np.float32).reshape(-1, points_dim)

        assert ori_points.shape == new_points.shape, f"Point cloud shapes do not match for {file_ori}: {ori_points.shape} vs {new_points.shape}"

print("All point clouds match between the original and new folders.")