# How Much Context Do 3D Object Detectors Need? An Oracle-Based Sensitivity Analysis

Official repository for "How Much Context Do 3D Object Detectors Need? An Oracle-Based Sensitivity Analysis". The code will be available soon.

## Abstract

Modern LiDAR-based 3D object detection operates on increasingly dense point clouds, where background regions dominate the data, imposing a massive, often redundant computational burden. Our spatial analysis of the nuScenes dataset reveals that over 92% of points belong to background classes, which typically contribute zero value to bounding box localization. In this work, we move beyond incremental heuristic filtering to establish the theoretical upper bound of background removal. By leveraging pointwise semantic ground-truth annotations, we isolate the intrinsic impact of spatial context on deep perception stacks. We subject six distinct pillar- and voxel-based architectures to a clean-slate evaluation under completely filtered environments, alongside a controlled spatial context scaling analysis to measure background dependency. Our empirical findings uncover a sharp architectural asymmetry: while pillar-based frameworks achieve the highest absolute gains in detection accuracy (up to +28.9% mAP), voxel-based detectors exploit spatial sparsity to secure dramatic computational savings, slashing complexity by up to 62.3% GFLOPS. Furthermore, we track end-to-end carbon footprints, demonstrating an 80.4% drop in estimated CO2 emissions for localized inference. This systematic exploration maps the trade-offs among geometric detail, localized context, and system latency, providing foundational insights for designing next-generation 3D object detectors.

## Results

TODO

## Reproducing our results

TODO

### 1. Libraries installation

TODO

### 2. Dataset download and preparation

TODO

### 3. Filtered point clouds generation

TODO

### 4. 3D detection models training

TODO

### 5. 3D detection models evaluation

TODO

### 6. Plots and tables generation

TODO

## Citation

TODO