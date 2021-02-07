import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F


class RandomBinaryConv(nn.Module):
    """Random Binary Convolution.
    
    See Local Binary Convolutional Neural Networks.
    """
    def __init__(self, in_channels,
                 out_channels,
                 kernel_size,
                 stride=1,
                 sparsity=0.9,
                 bias=False,
                 seed=1234):
        """

        TODO(zcq) Write a cuda/c++ version.

        Parameters
        ----------
        sparsity : float

        """
        self.out_channels = out_channels
        self.in_channels = in_channels
        num_elements = out_channels * in_channels * kernel_size * kernel_size
        assert not bias, "bias=True not supported"
        weight = torch.zeros((num_elements, ), requires_grad=False).float()
        index = np.random.choice(num_elements, int(sparsity * num_elements))
        weight[index] = torch.bernoulli(torch.ones_like(weight)[index] * 0.5) * 2 - 1
        weight = weight.view((out_channels, in_channels * kernel_size * kernel_size)).t()
        weight = weight.transpose(0, 1).astype(torch.bool)
        self.register_buffer('weight', weight)
        self.unfold = nn.Unfold(kernel_size=kernel_size, padding=kernel_size // 2,
                                stride=stride)

    def forward(self, x):
        b, _, h, w = x.shape
        input = self.unfold(x).transpose(1, 2)[..., None] # N HW CKK 1
        input = torch.where(self.weight[None, None, -1, self.out_channels],
                            input, torch.zeros_like(input)) # N HW CKK O
        input = torch.sum(input, dim=-2, keepdim=False)
        output = input.view((b, self.out_channels, h, w))
        return output


class LBConv(nn.Module):
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size=3,
                 stride=1,
                 sparsity=0.9,
                 bias=False,
                 seed=1234,
                 act=F.relu):
        """Use this to replace a conv + activation.
        """
        self.random_binary_conv = RandomBinaryConv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            sparsity=sparsity,
            seed=seed)
        # self.bn = nn.BatchNorm2d(in_channels)
        self.fc = nn.Conv2d(out_channels, in_channels, 1, 1)
        self.act = act

    def forward(self, x):
        # y = self.bn(x)
        y = self.random_binary_conv(x)
        y = self.relu(y)
        y = self.fc(y)
        return y
