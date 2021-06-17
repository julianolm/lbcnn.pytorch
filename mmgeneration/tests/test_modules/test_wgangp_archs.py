import pytest
import torch

from mmgen.models import WGANGPDiscriminator, WGANGPGenerator, build_module


class TestWGANGPGenerator(object):

    @classmethod
    def setup_class(cls):
        cls.noise = torch.randn((2, 100))
        cls.default_config = dict(
            type='WGANGPGenerator', noise_size=128, out_scale=128)

    def test_wgangp_generator(self):

        # test default setting with builder
        g = build_module(self.default_config)
        assert isinstance(g, WGANGPGenerator)
        x = g(None, num_batches=3)
        assert x.shape == (3, 3, 128, 128)

        # test different out_scale
        config = dict(type='WGANGPGenerator', noise_size=128, out_scale=64)
        g = build_module(config)
        assert isinstance(g, WGANGPGenerator)
        x = g(None, num_batches=3)
        assert x.shape == (3, 3, 64, 64)

        # test different conv config
        config = dict(
            type='WGANGPGenerator',
            noise_size=128,
            out_scale=128,
            conv_module_cfg=dict(
                conv_cfg=None,
                kernel_size=3,
                stride=1,
                padding=1,
                bias=True,
                act_cfg=dict(type='LeakyReLU', negative_slope=0.2),
                norm_cfg=dict(type='BN'),
                order=('conv', 'norm', 'act')))
        g = build_module(config)
        assert isinstance(g, WGANGPGenerator)
        x = g(None, num_batches=3)
        assert x.shape == (3, 3, 128, 128)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason='requires cuda')
    def test_wgangp_generator_cuda(self):

        # test default setting with builder
        g = build_module(self.default_config).cuda()
        assert isinstance(g, WGANGPGenerator)
        x = g(None, num_batches=3)
        assert x.shape == (3, 3, 128, 128)

        # test different out_scale
        config = dict(type='WGANGPGenerator', noise_size=128, out_scale=64)
        g = build_module(config).cuda()
        assert isinstance(g, WGANGPGenerator)
        x = g(None, num_batches=3)
        assert x.shape == (3, 3, 64, 64)

        # test different conv config
        config = dict(
            type='WGANGPGenerator',
            noise_size=128,
            out_scale=128,
            conv_module_cfg=dict(
                conv_cfg=None,
                kernel_size=3,
                stride=1,
                padding=1,
                bias=True,
                act_cfg=dict(type='LeakyReLU', negative_slope=0.2),
                norm_cfg=dict(type='BN'),
                order=('conv', 'norm', 'act')))
        g = build_module(config).cuda()
        assert isinstance(g, WGANGPGenerator)
        x = g(None, num_batches=3)
        assert x.shape == (3, 3, 128, 128)


class TestWGANGPDiscriminator(object):

    @classmethod
    def setup_class(cls):
        cls.x = torch.randn((2, 3, 128, 128))
        cls.default_config = dict(
            type='WGANGPDiscriminator', in_channel=3, in_scale=128)
        cls.conv_ln_module_config = dict(
            conv_cfg=None,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=True,
            act_cfg=dict(type='LeakyReLU', negative_slope=0.2),
            norm_cfg=dict(type='LN2d'),
            order=('conv', 'norm', 'act'))
        cls.conv_gn_module_config = dict(
            conv_cfg=None,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=True,
            act_cfg=dict(type='LeakyReLU', negative_slope=0.2),
            norm_cfg=dict(type='GN'),
            order=('conv', 'norm', 'act'))

    def test_wgangp_discriminator(self):

        # test default setting with builder
        d = build_module(self.default_config)
        assert isinstance(d, WGANGPDiscriminator)
        score = d(self.x)
        assert score.shape == (2, 1)

        # test different in_scale
        config = dict(type='WGANGPDiscriminator', in_channel=3, in_scale=64)
        d = build_module(config)
        assert isinstance(d, WGANGPDiscriminator)
        x = torch.randn((2, 3, 64, 64))
        score = d(x)
        assert score.shape == (2, 1)

        # test different conv config
        config = dict(
            type='WGANGPDiscriminator',
            in_channel=3,
            in_scale=128,
            conv_module_cfg=self.conv_ln_module_config)
        d = build_module(config)
        assert isinstance(d, WGANGPDiscriminator)
        score = d(self.x)
        assert score.shape == (2, 1)

        config = dict(
            type='WGANGPDiscriminator',
            in_channel=3,
            in_scale=128,
            conv_module_cfg=self.conv_gn_module_config)
        d = build_module(config)
        assert isinstance(d, WGANGPDiscriminator)
        score = d(self.x)
        assert score.shape == (2, 1)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason='requires cuda')
    def test_wgangp_discriminator_cuda(self):

        # test default setting with builder
        d = build_module(self.default_config).cuda()
        assert isinstance(d, WGANGPDiscriminator)
        score = d(self.x.cuda())
        assert score.shape == (2, 1)

        # test different in_scale
        config = dict(type='WGANGPDiscriminator', in_channel=3, in_scale=64)
        d = build_module(config).cuda()
        assert isinstance(d, WGANGPDiscriminator)
        x = torch.randn((2, 3, 64, 64))
        score = d(x.cuda())
        assert score.shape == (2, 1)

        # test different conv config
        config = dict(
            type='WGANGPDiscriminator',
            in_channel=3,
            in_scale=128,
            conv_module_cfg=self.conv_ln_module_config)
        d = build_module(config).cuda()
        assert isinstance(d, WGANGPDiscriminator)
        score = d(self.x.cuda())
        assert score.shape == (2, 1)

        config = dict(
            type='WGANGPDiscriminator',
            in_channel=3,
            in_scale=128,
            conv_module_cfg=self.conv_gn_module_config)
        d = build_module(config).cuda()
        assert isinstance(d, WGANGPDiscriminator)
        score = d(self.x.cuda())
        assert score.shape == (2, 1)
