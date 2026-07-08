
from spconv.pytorch import SparseSequential

from mmdet3d.models.layers.sparse_block import SparseBasicBlock
from mmdet3d.models.dense_heads.centerpoint_head import SeparateHead
from mmdet3d.models.backbones.second import SECOND
from mmdet3d.models.necks.second_fpn import SECONDFPN
from mmdet3d.models.middle_encoders.sparse_encoder import SparseEncoder
from mmdet3d.models.dense_heads.centerpoint_head import CenterHead
from mmdet3d.models.voxel_encoders.pillar_encoder import PillarFeatureNet
from mmdet3d.models.voxel_encoders.voxel_encoder import HardVFE
from mmdet3d.models.dense_heads.anchor3d_head import Anchor3DHead
from mmdet3d.models.dense_heads.shape_aware_head import ShapeAwareHead, BaseShapeHead
from mmdet3d.models.backbones.nostem_regnet import NoStemRegNet

from projects.BEVFusion.bevfusion.transfusion_head import TransFusionHead
from projects.BEVFusion.bevfusion.transformer import TransformerDecoderLayer, PositionEncodingLearned
from projects.BEVFusion.bevfusion.sparse_encoder import BEVFusionSparseEncoder

import torch.nn as nn

from mmdet.models.losses import FocalLoss, L1Loss, GaussianFocalLoss, SmoothL1Loss, CrossEntropyLoss
from mmdet.models.necks.fpn import FPN
from mmdet.models.backbones.resnext import Bottleneck

from mmcv.cnn.bricks.conv_module import ConvModule
from mmcv.cnn.bricks.transformer import FFN, MultiheadAttention



skiped_modules = (
    # Containers
    SparseSequential,
    SparseBasicBlock,
    nn.Sequential,
    nn.ModuleList,
    nn.ModuleDict,
    TransFusionHead,
    ConvModule,
    TransformerDecoderLayer,
    FFN,
    PositionEncodingLearned,
    SeparateHead,
    CenterHead,
    MultiheadAttention,
    BEVFusionSparseEncoder,
    SparseEncoder,
    SECOND,
    SECONDFPN,
    PillarFeatureNet,
    HardVFE,
    FPN,
    Anchor3DHead,
    ShapeAwareHead,
    BaseShapeHead,
    NoStemRegNet,
    Bottleneck,
    
    # Normalization
    nn.BatchNorm1d,
    nn.BatchNorm2d,
    nn.BatchNorm3d,
    nn.LayerNorm,
    
    # Activation
    nn.ReLU,
    
    # Losses
    FocalLoss,
    L1Loss,
    GaussianFocalLoss,
    SmoothL1Loss,
    CrossEntropyLoss,
    
    # Misc
    nn.Dropout,
    nn.Identity
)