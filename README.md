# How Much Context Do 3D Object Detectors Need? An Oracle-Based Sensitivity Analysis

Official repository for "How Much Context Do 3D Object Detectors Need? An Oracle-Based Sensitivity Analysis". The code will be available soon.

## Abstract

Modern LiDAR-based 3D object detection operates on increasingly dense point clouds, where background regions dominate the data, imposing a massive, often redundant computational burden. Our spatial analysis of the nuScenes dataset reveals that over 92% of points belong to background classes, which typically contribute zero value to bounding box localization. In this work, we move beyond incremental heuristic filtering to establish the theoretical upper bound of background removal. By leveraging pointwise semantic ground-truth annotations, we isolate the intrinsic impact of spatial context on deep perception stacks. We subject six distinct pillar- and voxel-based architectures to a clean-slate evaluation under completely filtered environments, alongside a controlled spatial context scaling analysis to measure background dependency. Our empirical findings uncover a sharp architectural asymmetry: while pillar-based frameworks achieve the highest absolute gains in detection accuracy (up to +28.9% mAP), voxel-based detectors exploit spatial sparsity to secure dramatic computational savings, slashing complexity by up to 62.3% GFLOPS. Furthermore, we track end-to-end carbon footprints, demonstrating an 80.4% drop in estimated CO2 emissions for localized inference. This systematic exploration maps the trade-offs among geometric detail, localized context, and system latency, providing foundational insights for designing next-generation 3D object detectors.

## Results

Below we present the main results of our study. A more comprehensive analysis is available on the [dedicated page containing the full set of results](README_results.md). Further details and discussion can also be found in our paper (TODO LINK).

### nuScenes dataset analysis

<img src="figs/bg_fg_proportions_plot_horizontal.svg" width="50%" />

<em>Distribution of foreground and background point proportions across semantic classes in the nuScenes dataset.</em>

### 3D object detection analysis

<table> <thead> <tr> <th>Model</th> <th>mAP</th> <th>NDS</th> <th>GFLOPS</th> <th>Mem (GB)</th> <th>FPS@1</th> <th>FPS@5</th> <th>CO₂ (g)</th> </tr> </thead> <tbody> <tr> <td>BEVFusion-L</td> <td>0.643</td> <td>0.691</td> <td>246.09</td> <td>2.81</td> <td>21.8</td> <td>38.6</td> <td>2.51</td> </tr> <tr> <td>BEVFusion-L<sup>*</sup></td> <td>0.672 (+4.5%)</td> <td>0.704 (+1.9%)</td> <td>185.67 (-24.6%)</td> <td>2.79 (-0.7%)</td> <td>26.8 (+22.8%)</td> <td>61.0 (+57.9%)</td> <td>1.69 (-32.6%)</td> </tr>

<tr> <td>BEVFusion-L 3Dh</td> <td>0.639</td> <td>0.691</td> <td>230.48</td> <td>2.80</td> <td>17.2</td> <td>32.9</td> <td>3.10</td> </tr> <tr> <td>BEVFusion-L 3Dh<sup>*</sup></td> <td>0.666 (+4.3%)</td> <td>0.702 (+1.5%)</td> <td>113.65 (-50.7%)</td> <td>2.78 (-0.7%)</td> <td>22.1 (+28.1%)</td> <td>65.9 (+100.2%)</td> <td>1.58 (-49.0%)</td> </tr>

<tr> <td>CenterPoint-Voxel</td> <td>0.557</td> <td>0.642</td> <td>163.53</td> <td>1.06</td> <td>14.5</td> <td>26.4</td> <td>3.27</td> </tr> <tr> <td>CenterPoint-Voxel<sup>*</sup></td> <td>0.612 (+10.0%)</td> <td>0.669 (+4.2%)</td> <td>121.62 (-25.6%)</td> <td>0.45 (-57.4%)</td> <td>17.2 (+18.1%)</td> <td>39.0 (+47.6%)</td> <td>1.54 (-52.9%)</td> </tr>

<tr> <td>CenterPoint-Pillar</td> <td>0.482</td> <td>0.593</td> <td>127.86</td> <td>3.22</td> <td>22.0</td> <td>48.9</td> <td>2.59</td> </tr> <tr> <td>CenterPoint-Pillar<sup>*</sup></td> <td>0.576 (+19.5%)</td> <td>0.645 (+8.8%)</td> <td>127.25 (-0.5%)</td> <td>0.82 (-74.4%)</td> <td>34.5 (+56.9%)</td> <td>71.1 (+45.2%)</td> <td>1.40 (-46.0%)</td> </tr>

<tr> <td>SSN</td> <td>0.461</td> <td>0.579</td> <td>237.34</td> <td>4.10</td> <td>9.3</td> <td>19.3</td> <td>9.29</td> </tr> <tr> <td>SSN<sup>*</sup></td> <td>0.558 (+21.1%)</td> <td>0.635 (+9.8%)</td> <td>231.96 (-2.3%)</td> <td>0.80 (-80.5%)</td> <td>20.9 (+124.4%)</td> <td>32.0 (+65.7%)</td> <td>2.01 (-78.4%)</td> </tr>

<tr> <td>PointPillars</td> <td>0.391</td> <td>0.527</td> <td>130.15</td> <td>12.91</td> <td>11.4</td> <td>18.0</td> <td>9.96</td> </tr> <tr> <td>PointPillars<sup>*</sup></td> <td>0.503 (+28.8%)</td> <td>0.586 (+11.2%)</td> <td>112.92 (-13.2%)</td> <td>1.27 (-90.2%)</td> <td>27.7 (+143.5%)</td> <td>37.8 (+109.8%)</td> <td>1.84 (-81.5%)</td> </tr> </tbody> </table>

<p><em>Performance results of the models. Values in parentheses indicate the percentage improvement over the unfiltered baseline. Models marked with <sup>*</sup> are trained and evaluated using filtered point clouds.</em></p>

## Reproducing our results

TODO

### 1. Packages Installation

To run the experiments, you must install MMDetection3D along with the required Python dependencies. There are two supported installation methods:

1. Using Docker (recommended)
2. Installing from source (without Docker)

We strongly recommend using the Docker-based installation, as it provides a consistent environment and makes reproducing the experimental results significantly more reliable.

#### Docker installation (recommended)

Build the Docker image containing all the required dependencies by running:

```
docker build -t bg_gt_filter .
```

Once the image has been built, create a Docker container with the following command:

```
docker run --gpus all --shm-size=8g -it -d \
    -v <nuscenes_path>:/mmdetection3d/data/nuscenes \
    -v ./bg_gt_filter:/mmdetection3d/bg_gt_filter \
    -v <models_path>:/mmdetection3d/models \
    bg_gt_filter
```

Replace the placeholders as follows:

* `<nuscenes_path>`: Path where the nuScenes dataset is (or will be) stored. If you have already downloaded the dataset, use its existing location.
* `<models_path>`: Directory where the 3D object detection model checkpoints will be downloaded or generated.

After creating the container, list the running containers to obtain its ID:

```
docker ps
```

Then attach to the container:

```
docker attach <container_id>
```

Once inside the container, you can proceed to the next steps.

#### Installation without docker

Alternatively, you can install MMDetection3D directly on your system. Follow the [official installation guide](https://mmdetection3d.readthedocs.io/en/latest/get_started.html) and install MMDetection3D from source.

After completing the MMDetection3D installation, install the additional dependencies required by this project:

```
pip install -r requirements.txt
```

In this installation option:

* `<nuscenes_path>` will be `<path_to_mmdet3d_installation>/data/nuscenes`
* `<models_path>` will be `<path_to_mmdet3d_installation>/models`

Once these dependencies have been installed, you can continue with the dataset preparation and experiment setup described in the following sections.

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
