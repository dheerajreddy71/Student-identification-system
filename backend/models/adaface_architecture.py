"""
AdaFace Architecture Implementation
Based on: "AdaFace: Quality Adaptive Margin for Face Recognition"
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Linear, Conv2d, BatchNorm1d, BatchNorm2d, PReLU, Dropout, Sequential, Module
import math


class Flatten(Module):
    """Flatten layer"""
    def forward(self, input):
        return input.view(input.size(0), -1)


class SEModule(Module):
    """Squeeze-and-Excitation Module"""
    def __init__(self, channels, reduction=16):
        super(SEModule, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc1 = Conv2d(channels, channels // reduction, kernel_size=1, padding=0, bias=False)
        self.relu = nn.ReLU(inplace=True)
        self.fc2 = Conv2d(channels // reduction, channels, kernel_size=1, padding=0, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        module_input = x
        x = self.avg_pool(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        return module_input * x


class BottleneckIR(Module):
    """Improved Residual Bottleneck - matches AdaFace checkpoint structure"""
    def __init__(self, in_channel, depth, stride):
        super(BottleneckIR, self).__init__()
        if in_channel == depth:
            self.shortcut_layer = nn.MaxPool2d(1, stride)
        else:
            self.shortcut_layer = Sequential(
                Conv2d(in_channel, depth, (1, 1), stride, bias=False),
                BatchNorm2d(depth)
            )
        # Checkpoint structure: BN → Conv → BN → PReLU → Conv → BN
        self.res_layer = Sequential(
            BatchNorm2d(in_channel),           # 0: BN
            Conv2d(in_channel, depth, (3, 3), (1, 1), 1, bias=False),  # 1: Conv
            BatchNorm2d(depth),                # 2: BN
            PReLU(depth),                      # 3: PReLU
            Conv2d(depth, depth, (3, 3), stride, 1, bias=False),       # 4: Conv
            BatchNorm2d(depth)                 # 5: BN
        )

    def forward(self, x):
        shortcut = self.shortcut_layer(x)
        res = self.res_layer(x)
        return res + shortcut


class BottleneckIRSE(Module):
    """Improved Residual Bottleneck with SE module - matches AdaFace checkpoint"""
    def __init__(self, in_channel, depth, stride):
        super(BottleneckIRSE, self).__init__()
        if in_channel == depth:
            self.shortcut_layer = nn.MaxPool2d(1, stride)
        else:
            self.shortcut_layer = Sequential(
                Conv2d(in_channel, depth, (1, 1), stride, bias=False),
                BatchNorm2d(depth)
            )
        # Checkpoint structure: BN → Conv → BN → PReLU → Conv → BN → SE
        self.res_layer = Sequential(
            BatchNorm2d(in_channel),           # 0: BN
            Conv2d(in_channel, depth, (3, 3), (1, 1), 1, bias=False),  # 1: Conv
            BatchNorm2d(depth),                # 2: BN
            PReLU(depth),                      # 3: PReLU
            Conv2d(depth, depth, (3, 3), stride, 1, bias=False),       # 4: Conv
            BatchNorm2d(depth),                # 5: BN
            SEModule(depth, 16)                # 6: SE
        )

    def forward(self, x):
        shortcut = self.shortcut_layer(x)
        res = self.res_layer(x)
        return res + shortcut


class IR_50(Module):
    """IR-50 Backbone"""
    def __init__(self, input_size=(112, 112), num_layers=50, mode='ir'):
        super(IR_50, self).__init__()
        assert input_size[0] in [112, 224], "input_size should be 112x112 or 224x224"
        assert num_layers in [50, 100, 152], "num_layers should be 50, 100, or 152"
        assert mode in ['ir', 'ir_se'], "mode should be 'ir' or 'ir_se'"
        
        blocks = self._get_blocks(num_layers)
        unit_module = BottleneckIRSE if mode == 'ir_se' else BottleneckIR

        self.input_layer = Sequential(
            Conv2d(3, 64, (3, 3), 1, 1, bias=False),
            BatchNorm2d(64),
            PReLU(64)
        )
        
        if input_size[0] == 112:
            self.output_layer = Sequential(
                BatchNorm2d(512),
                Dropout(0.4),
                Flatten(),
                Linear(512 * 7 * 7, 512),
                BatchNorm1d(512)
            )
        else:  # 224
            self.output_layer = Sequential(
                BatchNorm2d(512),
                Dropout(0.4),
                Flatten(),
                Linear(512 * 14 * 14, 512),
                BatchNorm1d(512)
            )

        modules = []
        for block in blocks:
            for bottleneck in block:
                modules.append(unit_module(bottleneck[0], bottleneck[1], bottleneck[2]))
        self.body = Sequential(*modules)

    def _get_blocks(self, num_layers):
        """Get network blocks configuration - matches AdaFace checkpoint structure"""
        if num_layers == 50:
            return [
                [[64, 64, 2], [64, 64, 1], [64, 64, 1]],  # Stage 1
                [[64, 128, 2], [128, 128, 1], [128, 128, 1], [128, 128, 1]],  # Stage 2
                [[128, 256, 2], [256, 256, 1], [256, 256, 1], [256, 256, 1], 
                 [256, 256, 1], [256, 256, 1], [256, 256, 1], [256, 256, 1], 
                 [256, 256, 1], [256, 256, 1], [256, 256, 1], [256, 256, 1], 
                 [256, 256, 1], [256, 256, 1]],  # Stage 3
                [[256, 512, 2], [512, 512, 1], [512, 512, 1]]  # Stage 4
            ]
        elif num_layers == 100:
            # IR-101 structure from checkpoint analysis:
            # Layer 0-2: 64→64 (3 blocks)
            # Layer 3-15: 64→128, then 128→128 (13 blocks total)
            # Layer 16-45: 128→256, then 256→256 (30 blocks total)
            # Layer 46-48: 256→512, then 512→512 (3 blocks total)
            blocks = []
            # Stage 1: 3 blocks of 64→64
            blocks.append([[64, 64, 2], [64, 64, 1], [64, 64, 1]])
            # Stage 2: Transition 64→128, then 12 blocks of 128→128
            stage2 = [[64, 128, 2]]
            stage2.extend([[128, 128, 1]] * 12)
            blocks.append(stage2)
            # Stage 3: Transition 128→256, then 29 blocks of 256→256
            stage3 = [[128, 256, 2]]
            stage3.extend([[256, 256, 1]] * 29)
            blocks.append(stage3)
            # Stage 4: Transition 256→512, then 2 blocks of 512→512
            blocks.append([[256, 512, 2], [512, 512, 1], [512, 512, 1]])
            return blocks
        else:  # 152
            return [
                [[64, 64, 2], [64, 64, 1], [64, 64, 1]],
                [[64, 128, 2]] + [[128, 128, 1]] * 7,
                [[128, 256, 2]] + [[256, 256, 1]] * 35,
                [[256, 512, 2], [512, 512, 1], [512, 512, 1]]
            ]

    def forward(self, x):
        x = self.input_layer(x)
        x = self.body(x)
        x = self.output_layer(x)
        return x


class IR_101(IR_50):
    """IR-101 Backbone (AdaFace uses this)"""
    def __init__(self, input_size=(112, 112), mode='ir'):
        super(IR_101, self).__init__(input_size, num_layers=100, mode=mode)


class IR_152(IR_50):
    """IR-152 Backbone"""
    def __init__(self, input_size=(112, 112), mode='ir'):
        super(IR_152, self).__init__(input_size, num_layers=152, mode=mode)


class AdaFaceHead(Module):
    """AdaFace Head with quality-adaptive margins"""
    def __init__(self, embedding_size=512, num_classes=10000, m=0.4, h=0.333, s=64.0):
        super(AdaFaceHead, self).__init__()
        self.embedding_size = embedding_size
        self.num_classes = num_classes
        self.m = m
        self.h = h
        self.s = s
        
        self.weight = nn.Parameter(torch.FloatTensor(num_classes, embedding_size))
        nn.init.xavier_uniform_(self.weight)

    def forward(self, embeddings, labels=None, norms=None):
        """
        Args:
            embeddings: (batch_size, embedding_size)
            labels: (batch_size,) ground truth labels
            norms: (batch_size,) embedding norms (quality proxy)
        """
        # Normalize weights
        weight_norm = F.normalize(self.weight, p=2, dim=1)
        
        # Normalize embeddings
        embedding_norm = F.normalize(embeddings, p=2, dim=1)
        
        # Compute cosine similarity
        cos_theta = F.linear(embedding_norm, weight_norm)
        
        if labels is None:
            return cos_theta * self.s
        
        # Quality-adaptive margin
        if norms is None:
            norms = torch.norm(embeddings, 2, 1, keepdim=True)
        
        # Adaptive margin based on image quality
        safe_norms = torch.clamp(norms, min=0.001, max=100)
        ada_margin = self.m * (safe_norms ** self.h)
        ada_margin = torch.clamp(ada_margin, 0, self.m)
        
        # Apply margin to target class
        batch_size = embeddings.size(0)
        one_hot = torch.zeros(batch_size, self.num_classes, device=embeddings.device)
        one_hot.scatter_(1, labels.view(-1, 1).long(), 1)
        
        # Add adaptive margin
        cos_theta_m = cos_theta - ada_margin * one_hot
        
        # Scale
        output = cos_theta_m * self.s
        
        return output


def build_model(architecture='ir_101'):
    """
    Build AdaFace model
    
    Args:
        architecture: 'ir_50', 'ir_101', or 'ir_152'
    
    Returns:
        Model instance
    """
    if architecture == 'ir_50':
        return IR_50(input_size=(112, 112), mode='ir')
    elif architecture == 'ir_101':
        return IR_101(input_size=(112, 112), mode='ir')
    elif architecture == 'ir_152':
        return IR_152(input_size=(112, 112), mode='ir')
    else:
        raise ValueError(f"Unknown architecture: {architecture}")
