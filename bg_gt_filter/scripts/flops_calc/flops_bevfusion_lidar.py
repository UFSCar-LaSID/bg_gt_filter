
import torch
from spconv.pytorch import SparseConv3d, SubMConv3d

from flops_calc.general.FlopsCalculator import FlopsCalculator
from flops_calc.general.skiped_modules import skiped_modules




def calc_bevfusion_lidar_flops(model, dataloader):
    
    hooks = []
    
    flops_calculator = FlopsCalculator(
        per_layer_stats = {
            'middle_encoder': {},
            'backbone': {},
            'neck': {},
            'head': {}
        }
    )

    component_name = 'middle_encoder'
    for name, module in model.pts_middle_encoder.named_modules():
        if isinstance(module, (SparseConv3d, SubMConv3d, torch.nn.Conv3d)):
            hooks.append(
                module.register_forward_hook(
                    flops_calculator.conv3d_hook(
                        component_name,
                        name
                    )
                )
            )
        elif not isinstance(module, skiped_modules):
            raise NotImplementedError(f"Module type {type(module)} not supported in middle_encoder.")

    component_name = 'backbone'
    for name, module in model.pts_backbone.named_modules():
        if isinstance(module, torch.nn.Conv2d):
            hooks.append(
                module.register_forward_hook(
                    flops_calculator.conv2d_hook(
                        component_name,
                        name
                    )
                )
            )
        elif not isinstance(module, skiped_modules):
            raise NotImplementedError(f"Module type {type(module)} not supported in backbone.")
    
    component_name = 'neck'
    for name, module in model.pts_neck.named_modules():
        if isinstance(module, (torch.nn.Conv2d)):
            hooks.append(
                module.register_forward_hook(
                    flops_calculator.conv2d_hook(
                        component_name,
                        name
                    )
                )
            )
        elif isinstance(module, torch.nn.ConvTranspose2d):
            hooks.append(
                module.register_forward_hook(
                    flops_calculator.conv_transpose2d_hook(
                        component_name,
                        name
                    )
                )
            )
        elif not isinstance(module, skiped_modules):
            raise NotImplementedError(f"Module type {type(module)} not supported in neck.")

    component_name = 'head'
    for name, module in model.bbox_head.named_modules():
        if isinstance(module, (torch.nn.Conv2d)):
            hooks.append(
                module.register_forward_hook(
                    flops_calculator.conv2d_hook(
                        component_name,
                        f'head.{name}'
                    )
                )
            )
        elif isinstance(module, torch.nn.ConvTranspose2d):
            hooks.append(
                module.register_forward_hook(
                    flops_calculator.conv_transpose2d_hook(
                        component_name,
                        f'head.{name}'
                    )
                )
            )
        elif isinstance(module, torch.nn.Conv1d):
            hooks.append(
                module.register_forward_hook(
                    flops_calculator.conv1d_hook(
                        component_name,
                        f'head.{name}'
                    )
                )
            )
        elif isinstance(module, torch.nn.Linear):
            hooks.append(
                module.register_forward_hook(
                    flops_calculator.linear_hook(
                        component_name,
                        f'head.{name}'
                    )
                )
            )
        elif isinstance(module, torch.nn.MultiheadAttention):
            hooks.append(
                module.register_forward_hook(
                    flops_calculator.multihead_attention_hook(
                        component_name,
                        f'head.{name}'
                    )
                )
            )
        elif not isinstance(module, skiped_modules):
            raise NotImplementedError(f"Module type {type(module)} not supported in head.")

    flops_results, fps, predictions, per_layer_stats = flops_calculator.compute_flops(model, dataloader)

    for h in hooks:
        h.remove()

    return flops_results, fps, predictions, per_layer_stats