

from collections import OrderedDict
import time
import torch
import math


class FlopsCalculator:

    MAC_TO_FLOP = 2.0

    def __init__(self, per_layer_stats):
        self.per_layer_stats = per_layer_stats
        self.needs_compute_mean_stats = {}

    def conv3d_hook(self, component_name, module_name):
        
        self.needs_compute_mean_stats[component_name] = True

        def hook(module, inp, out):

            stats = OrderedDict()
            stats['name'] = module_name

            voxels_active = out.features.shape[0]

            channels_in = module.in_channels
            channels_out = module.out_channels

            kernel_volume = 1
            for size in module.kernel_size:
                kernel_volume *= size

            # The folowing way to compute FLOPs uses the number of active neighboorhood, so the convolution does not uses non active voxels in the computation
            active_conv_map = (out.indice_dict[module.indice_key].pair_fwd >= 0).sum().item()

            macs = channels_in * channels_out * active_conv_map

            flops = macs * self.MAC_TO_FLOP

            # The following way to compute FLOPs uses the number of active voxels, considering that even non active voxels are used in the convolution proccess
            macs_dense = voxels_active * channels_in * channels_out * kernel_volume
            flops_dense = macs_dense * self.MAC_TO_FLOP

            component_stats = self.per_layer_stats[component_name]

            if module_name not in component_stats:
                component_stats[module_name] = {
                    'name': module_name,
                    'channels_in': channels_in,
                    'channels_out': channels_out,
                    'kernel_volume': kernel_volume,
                    'voxels_active': 0,
                    'MACs': 0,
                    'FLOPs': 0,
                    'count': 0,
                    'MACs_dense': 0,
                    'FLOPs_dense': 0
                }
                
            stats = component_stats[module_name]

            stats['voxels_active'] += voxels_active
            stats['MACs'] += macs
            stats['FLOPs'] += flops
            stats['MACs_dense'] += macs_dense
            stats['FLOPs_dense'] += flops_dense
            stats['count'] += 1

        return hook


    def conv2d_hook(self, component_name, module_name):
        
        # A good example of how conv2ds works, and a good reference to understand how to compute FLOPS for conv2D
        # https://cs231n.github.io/convolutional-networks/
        
        self.needs_compute_mean_stats[component_name] = False

        def hook(module, inp, out):
            
            if module_name in self.per_layer_stats[component_name]:
                return

            stats = OrderedDict()

            _, channels_out, height_out, width_out = out.shape

            channels_in = module.in_channels

            kernel_area = math.prod(module.kernel_size)
            
            macs = channels_in * channels_out * kernel_area * height_out * width_out

            flops = macs * self.MAC_TO_FLOP

            stats.update({
                'name': module_name,
                'channels_in': channels_in,
                'channels_out': channels_out,
                'kernel_area': kernel_area,
                'height_out': height_out,
                'width_out': width_out,
                'MACs': macs,
                'FLOPs': flops
            })

            self.per_layer_stats[component_name][module_name] = stats

        return hook

    def conv_transpose2d_hook(self, component_name, module_name):
        
        # A good example of how transposed conv2ds works, and a good reference to understand how to compute FLOPS for transposed conv2D
        # https://www.geeksforgeeks.org/machine-learning/apply-a-2d-transposed-convolution-operation-in-pytorch/
        
        self.needs_compute_mean_stats[component_name] = False

        def hook(module, inp, out):
            
            if module_name in self.per_layer_stats[component_name]:
                return

            stats = OrderedDict()

            _, channels_in, height_in, width_in = inp[0].shape

            channels_out = module.out_channels

            kernel_area = math.prod(module.kernel_size)
            
            macs = channels_in * channels_out * kernel_area * height_in * width_in

            flops = macs * self.MAC_TO_FLOP

            stats.update({
                'name': module_name,
                'channels_in': channels_in,
                'channels_out': channels_out,
                'kernel_area': kernel_area,
                'height_in': height_in,
                'width_in': width_in,
                'MACs': macs,
                'FLOPs': flops
            })

            self.per_layer_stats[component_name][module_name] = stats

        return hook
    
    def conv1d_hook(self, component_name, module_name):
        
        self.needs_compute_mean_stats[component_name] = False

        def hook(module, inp, out):

            if module_name in self.per_layer_stats[component_name]:
                return

            stats = OrderedDict()

            _, channels_out, out_lenght = out.shape

            channels_in = module.in_channels

            kernel_size = module.kernel_size[0]

            macs = channels_in * channels_out * kernel_size * out_lenght

            flops = macs * self.MAC_TO_FLOP

            stats.update({
                'name': module_name,
                'channels_in': channels_in,
                'channels_out': channels_out,
                'out_lenght': out_lenght,
                'kernel_size': kernel_size,
                'MACs': macs,
                'FLOPs': flops
            })

            self.per_layer_stats[component_name][module_name] = stats

        return hook
    
    def linear_hook(self, component_name, module_name):
        
        self.needs_compute_mean_stats[component_name] = False

        def hook(module, inp, out):
            
            if module_name in self.per_layer_stats[component_name]:
                return

            stats = OrderedDict()

            in_features = module.in_features
            out_features = module.out_features

            macs = in_features * out_features
    
            flops = macs * self.MAC_TO_FLOP

            stats.update({
                'name': module_name,
                'in_features': in_features,
                'out_features': out_features,
                'MACs': macs,
                'FLOPs': flops
            })

            self.per_layer_stats[component_name][module_name] = stats

        return hook
    
    def multihead_attention_hook(self, component_name, module_name):
        self.needs_compute_mean_stats[component_name] = False

        def hook(module, inp, out):
            if module_name in self.per_layer_stats[component_name]:
                return

            stats = OrderedDict()

            attn_output, attn_weights = out

            if module.batch_first:
                _, seq_len_q, embed_dim = attn_output.shape
            else:
                seq_len_q, _, embed_dim = attn_output.shape

            seq_len_kv = attn_weights.shape[-1]

            q_proj = seq_len_q * embed_dim * embed_dim
            kv_proj = 2 * (seq_len_kv * embed_dim * embed_dim)
            qkv_macs = q_proj + kv_proj

            qk_matmul_macs = seq_len_q * seq_len_kv * embed_dim
            score_v_matmul_macs = seq_len_q * seq_len_kv * embed_dim

            out_proj_macs = seq_len_q * embed_dim * embed_dim

            macs = qkv_macs + qk_matmul_macs + score_v_matmul_macs + out_proj_macs
            flops = macs * self.MAC_TO_FLOP

            stats.update({
                'name': module_name,
                'seq_len_q': seq_len_q,
                'seq_len_kv': seq_len_kv,
                'embed_dim': embed_dim,
                'MACs': macs,
                'FLOPs': flops
            })

            self.per_layer_stats[component_name][module_name] = stats

        return hook
    
    def pfn_hook(self, component_name, module_name):
        
        self.needs_compute_mean_stats[component_name] = True
        
        def hook(module, inp, out):

            N_pillars = inp[0].shape[0]
            max_points = inp[0].shape[1]
            channels_in = module.linear.in_features
            channels_out = module.linear.out_features

            macs_linear = N_pillars * max_points * channels_in * channels_out
            macs_pool_relu = N_pillars * channels_out * max_points
            
            macs = macs_linear + macs_pool_relu
            flops = macs * self.MAC_TO_FLOP
            
            component_stats = self.per_layer_stats[component_name]

            if module_name not in component_stats:
                component_stats[module_name] = {
                    'name': module_name,
                    'channels_in': channels_in,
                    'channels_out': channels_out,
                    'max_points': max_points,
                    'N_pillars': 0,
                    'MACs': 0,
                    'FLOPs': 0,
                    'count': 0
                }
                
            stats = component_stats[module_name]
            
            stats['N_pillars'] += N_pillars
            stats['MACs'] += macs
            stats['FLOPs'] += flops
            stats['count'] += 1
            
        return hook



    def __compute_mean_stats(self, component_name):
        for stats in self.per_layer_stats[component_name].values():
            stats['mean_MACs'] = stats['MACs'] / stats['count']
            stats['mean_FLOPs'] = stats['FLOPs'] / stats['count']
            if 'voxels_active' in stats:
                stats['mean_voxels_active'] = stats['voxels_active'] / stats['count']
            if 'N_pillars' in stats:
                stats['mean_N_pillars'] = stats['N_pillars'] / stats['count']
            if 'MACs_dense' in stats:
                stats['mean_MACs_dense'] = stats['MACs_dense'] / stats['count']
            if 'FLOPs_dense' in stats:
                stats['mean_FLOPs_dense'] = stats['FLOPs_dense'] / stats['count']

    def __compute_final_flops(self):
        
        for comp_name, needs_mean in self.needs_compute_mean_stats.items():
            if needs_mean:
                self.__compute_mean_stats(comp_name)
        
        flops_dict = {}
        for comp_name, comp_stats in self.per_layer_stats.items():
            if self.needs_compute_mean_stats[comp_name]:
                flops_dict[comp_name] = sum([stats['mean_FLOPs'] for stats in comp_stats.values()])
            else:
                flops_dict[comp_name] = sum([stats['FLOPs'] for stats in comp_stats.values()])
        
        flops_dict['overall'] = sum(flops_dict.values())
        
        return flops_dict


    def compute_flops(self, model, dataloader):
        times = []
        predictions = []

        for data in dataloader:

            with torch.no_grad():

                torch.cuda.synchronize()
                start_time = time.time()
                
                results_model = model.test_step(data)
                
                torch.cuda.synchronize()
                end_time = time.time()
                
                times.append(end_time - start_time)

            for i in range(len(results_model)):
                results_model[i] = results_model[i].to('cpu').to_dict()

            predictions.extend(results_model)
        
        
        flops_results = self.__compute_final_flops()
        
        fps = 1.0 / (sum(times) / len(times))
        
        return flops_results, fps, predictions, self.per_layer_stats