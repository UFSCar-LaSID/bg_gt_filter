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

This section describes how to download, prepare, and preprocess the nuScenes dataset before running the detection pipeline. These steps ensure that the dataset is converted into the format expected by the framework.

#### Dataset download

The project uses the nuScenes v1.0 Full Dataset together with the nuScenes LiDAR Segmentation (lidarseg) annotations. Follow the instructions below to install the dataset:

1. Create an account and log in to the [official nuScenes website](https://www.nuscenes.org/nuscenes#download).
2. Download the following packages:
    * Full dataset (v1.0)
    * nuScenes-lidarseg
3. Extract all downloaded files into the dataset root directory `<nuscenes_path>`

A typical directory structure should look similar to:

```
<nuscenes_path>/
├── maps/
├── samples/
├── sweeps/
├── lidarseg/
├── v1.0-trainval/
└── v1.0-test/
```


#### MMDetection3D Dataset preparation

After downloading, it is necessary to run the MMDetection3D dataset preparation script to be able to run the detection models on the nuScenes data. To do so, execute the following command:

```
python tools/create_data.py nuscenes \
    --root-path ./data/nuscenes \
    --out-dir ./data/nuscenes \
    --extra-tag nuscenes
```

#### Generate background/foreground (BGFG) labels

After preparing the dataset, an additional preprocessing step is required to generate background (BG) and foreground (FG) labels used by the subsequent pipeline stages.

This script:

* Converts the original semantic labels into two classes: background (BG) and foreground (FG).
* Generates BGFG labels for non-keyframe LiDAR sweeps by propagating labels from the nearest temporal keyframes using a K-Nearest Neighbors (KNN) approach.

This script can be excecuted by running the below command:

```
python /mmdetection3d/bg_gt_filter/scripts/generate_bgfg_labels.py
```

#### Generate filtered point clouds 

The final preprocessing step generates the ground-truth (oracle) filtered point clouds used by the detection pipeline.

During this process, voxels containing only background (BG) points are removed, while voxels containing at least one foreground (FG) point are preserved. Filtered point clouds are generated for multiple voxel sizes, allowing different amounts of background context to be retained around foreground objects. Larger voxel sizes preserve more surrounding context, whereas smaller voxel sizes produce more aggressive filtering.

To support the configurations used by different detection models, filtered point clouds are generated for:

* 9 concatenated LiDAR sweeps, used by BEVFusion and CenterPoint.
* 10 concatenated LiDAR sweeps, used by SSN and PointPillars.

Run the preprocessing script with:

```
python /mmdetection3d/bg_gt_filter/scripts/generate_filtered_pcds.py
```

After completion, the filtered point clouds will be available for training and evaluating the supported detection models.

### 3. 3D detection models training

After completing the dataset preparation steps, the detection models can be trained. The table below lists the training command for each model, the expected performance in terms of mAP and NDS, and a link to download the pre-trained model weights. Using the provided checkpoints allows you to skip the training step if desired.

Models marked with * are trained using the ground-truth filtered point clouds, while the remaining models are trained using the original (raw) point clouds.

<table>
  <thead>
    <tr>
      <th>Model name</th>
      <th>mAP</th>
      <th>NDS</th>
      <th>Model weights</th>
      <th>Train command</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>BEVFusion-L</td>
      <td>0.643</td>
      <td>0.691</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/bevfusion_lidar/bevfusion_lidar.py">
          bg_gt_filter/configs/nuscenes/bevfusion_lidar/bevfusion_lidar.py
        </a>
      </td>
    </tr>
    <tr>
      <td>BEVFusion-L*</td>
      <td>0.672</td>
      <td>0.704</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/bevfusion_lidar/bevfusion_lidar_gt_filter.py">
          bg_gt_filter/configs/nuscenes/bevfusion_lidar/bevfusion_lidar_gt_filter.py
        </a>
      </td>
    </tr>
    <tr>
      <td>BEVFusion-L 3Dh</td>
      <td>0.639</td>
      <td>0.691</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/bevfusion_lidar_3dh/bevfusion_lidar_3dh.py">
          bg_gt_filter/configs/nuscenes/bevfusion_lidar_3dh/bevfusion_lidar_3dh.py
        </a>
      </td>
    </tr>
    <tr>
      <td>BEVFusion-L 3Dh*</td>
      <td>0.666</td>
      <td>0.702</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/bevfusion_lidar_3dh/bevfusion_lidar_3dh_gt_filter.py">
          bg_gt_filter/configs/nuscenes/bevfusion_lidar_3dh/bevfusion_lidar_3dh_gt_filter.py
        </a>
      </td>
    </tr>
    <tr>
      <td>CenterPoint-Voxel</td>
      <td>0.557</td>
      <td>0.642</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/centerpoint_voxel/centerpoint_voxel.py">
          bg_gt_filter/configs/nuscenes/centerpoint_voxel/centerpoint_voxel.py
        </a>
      </td>
    </tr>
    <tr>
      <td>CenterPoint-Voxel*</td>
      <td>0.612</td>
      <td>0.669</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/centerpoint_voxel/centerpoint_voxel_gt_filter.py">
          bg_gt_filter/configs/nuscenes/centerpoint_voxel/centerpoint_voxel_gt_filter.py
        </a>
      </td>
    </tr>
    <tr>
      <td>CenterPoint-Pillar</td>
      <td>0.482</td>
      <td>0.593</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/centerpoint_pillar/centerpoint_pillar.py">
          bg_gt_filter/configs/nuscenes/centerpoint_pillar/centerpoint_pillar.py
        </a>
      </td>
    </tr>
    <tr>
      <td>CenterPoint-Pillar*</td>
      <td>0.576</td>
      <td>0.645</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/centerpoint_pillar/centerpoint_pillar_gt_filter.py">
          bg_gt_filter/configs/nuscenes/centerpoint_pillar/centerpoint_pillar_gt_filter.py
        </a>
      </td>
    </tr>
    <tr>
      <td>SSN</td>
      <td>0.461</td>
      <td>0.579</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/ssn_regnext/ssn_regnext.py">
          bg_gt_filter/configs/nuscenes/ssn_regnext/ssn_regnext.py
        </a>
      </td>
    </tr>
    <tr>
      <td>SSN*</td>
      <td>0.558</td>
      <td>0.635</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/ssn_regnext/ssn_regnext_gt_filter.py">
          bg_gt_filter/configs/nuscenes/ssn_regnext/ssn_regnext_gt_filter.py
        </a>
      </td>
    </tr>
    <tr>
      <td>PointPillars</td>
      <td>0.391</td>
      <td>0.527</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/pointpillars/pointpillars.py">
          bg_gt_filter/configs/nuscenes/pointpillars/pointpillars.py
        </a>
      </td>
    </tr>
    <tr>
      <td>PointPillars*</td>
      <td>0.503</td>
      <td>0.586</td>
      <td>Download</td>
      <td>
        python tools/train.py
        <a href="bg_gt_filter/configs/nuscenes/pointpillars/pointpillars_gt_filter.py">
          bg_gt_filter/configs/nuscenes/pointpillars/pointpillars_gt_filter.py
        </a>
      </td>
    </tr>
  </tbody>
</table>

After either training the models or downloading the pre-trained checkpoints, organize the model weights using the following directory structure:

* Models trained on raw point clouds: `<models_path>/nuscenes/<model_name>/<model_name>.pth`
* Models trained on filtered point clouds: `<models_path>/nuscenes/<model_name>/<model_name>_gt_filter.pth`

Maintaining this directory structure ensures that the evaluation and benchmarking scripts can automatically locate the corresponding model checkpoints.

### 4. 3D detection models evaluation

The evaluation protocol assesses the detection models under different input configurations to measure the impact of background filtering on detection performance, computational cost, inference speed, and environmental impact.

The following evaluation scenarios are considered:

* **Original model performance**: a model trained on the **raw point clouds** is evaluated using the **raw point clouds**. This serves as the baseline for comparison.

* **Ground-truth (GT) filtered model performance**: a model trained on the **ground-truth filtered point clouds** is evaluated using the corresponding **filtered point clouds** (1x voxel size). Comparing these results with the baseline quantifies the effect of training and evaluating with filtered data.

* **Original model with progressive context removal**: the model trained on the **raw point clouds** is evaluated using filtered point clouds generated with different voxel sizes (1x, 2x, 4x, 8x, 16x, and 32x). Larger voxel sizes preserve more background context around foreground objects, allowing the analysis of how surrounding context influences the model's detection performance.

For each evaluation scenario, the following metrics are reported:

* **mAP** and **NDS**: detection accuracy metrics.
* **GFLOPs** and **Memory (GB)**: computational complexity and GPU memory usage during inference.
* **FPS@1** and **FPS@5**: inference throughput measured with batch sizes of 1 and 5, respectively. **FPS@1** represents real-time inference performance, while **FPS@5** provides a better indication of throughput for offline processing and evaluation.
* **CO₂ (g)**: estimated carbon emissions associated with model inference, providing an indication of the environmental impact of each configuration.

To evaluate all supported models across all scenarios, run:

```
python /mmdetection3d/bg_gt_filter/scripts/evaluate.py
```

All results will be saved at `/mmdetection3d/results` (can be modified with the `--results_output_dir` arg).

### 5. Plots and tables generation

After completing the evaluation, generate the figures and tables used in the analysis by executing all cells in the [`plots_and_tables.ipynb`](bg_gt_filter/scripts/plots_and_tables.ipynb) Jupyter notebook.

The notebook automatically loads the evaluation results from the specified output directory, computes the required statistics, and generates all plots and tables presented in the [results page](README_results.md). Ensure that the evaluation has been completed successfully and that the results are available in the expected location before running the notebook. By default, the notebook reads the results from `/mmdetection3d/results`. If the evaluation results are stored in a different directory, update the corresponding path in the notebook before execution. The tables and plots will be saved in `/mmdetection3d/plots_and_tables` (which can be configured by the `plots_and_tables_dir` variable).

## Citation

TODO
