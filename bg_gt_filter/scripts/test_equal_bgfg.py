
import numpy as np
import os
from tqdm import tqdm

labels_path_1 = '/mmdetection3d/data/nuscenes/lidarseg_bgfg/v1.0-trainval'
labels_path_2 = '/mmdetection3d/data/nuscenes/lidarseg_bgfg_2/v1.0-trainval'

labels_files_1 = sorted(os.listdir(labels_path_1))
labels_files_2 = sorted(os.listdir(labels_path_2))

assert len(labels_files_1) == len(labels_files_2), "The number of files in both directories should be the same. bgfg_ori = {}, bgfg_new = {}".format(len(labels_files_1), len(labels_files_2))


for file1, file2 in tqdm(zip(labels_files_1, labels_files_2), desc='Comparing label files', total=len(labels_files_1)):
    assert file1 == file2, "File names do not match: {} != {}".format(file1, file2)

    file_path_1 = os.path.join(labels_path_1, file1)
    file_path_2 = os.path.join(labels_path_2, file2)

    labels_1 = np.fromfile(file_path_1, dtype=np.uint8)
    labels_2 = np.fromfile(file_path_2, dtype=np.uint8)

    assert labels_1.shape == labels_2.shape, "Label shapes do not match for file {}: {} != {}".format(file1, labels_1.shape, labels_2.shape)
    assert np.array_equal(labels_1, labels_2), "Labels do not match for file {}".format(file1)


print('All files are identical.')