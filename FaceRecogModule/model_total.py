import torch
import torch.nn as nn
from torchvision import models

class Compressor(nn.Module):
    
    def __init__(self, in_channel, out_channel):
        super().__init__()
        mid_channel = (in_channel + out_channel) // 2
        self.conv1 = DepthwiseSeperableConv(in_channel, mid_channel)
        #self.bn1 = GDN(mid_channel)
        self.bn1 = nn.BatchNorm2d(mid_channel)
        self.lrelu1 = nn.LeakyReLU(0.1)
        self.conv2 = DepthwiseSeperableConv(mid_channel, out_channel)
        #self.bn2 = GDN(out_channel)
        self.bn2 = nn.BatchNorm2d(out_channel)
        self.lrelu2 = nn.LeakyReLU(0.1)

    def forward(self, x):
        x = self.lrelu1(self.bn1(self.conv1(x)))
        x = self.lrelu2(self.bn2(self.conv2(x)))

        return x

class DepthwiseSeperableConv(nn.Module):
    
    def __init__(self, nin, nout):
        super(DepthwiseSeperableConv, self).__init__()
        self.depthwise = nn.Conv2d(nin,
                                   nin,
                                   kernel_size=3,
                                   padding=1,
                                   groups=nin)
        self.pointwise = nn.Conv2d(nin, int(nout), kernel_size=1)

    def forward(self, x):
        out = self.depthwise(x)
        out = self.pointwise(out)
        return out

class Decompressor(nn.Module):
    
    # yapf: disable
    def __init__(self, in_channel, out_channel):
        super().__init__()
        mid_channel = (in_channel + out_channel) // 2
        self.conv1 = nn.Conv2d(out_channel, mid_channel, kernel_size = 3, padding = 1)
        self.bn1 = nn.BatchNorm2d(mid_channel)
        self.lrelu1 = nn.LeakyReLU(0.1)
        self.conv2 = nn.Conv2d(mid_channel, mid_channel, kernel_size = 3, padding = 1)
        self.bn2 = nn.BatchNorm2d(mid_channel)
        self.lrelu2 = nn.LeakyReLU(0.1)
        self.conv3 = nn.Conv2d(mid_channel, in_channel, kernel_size = 3, padding = 1)
        self.bn3 = nn.BatchNorm2d(in_channel)
        self.lrelu3 = nn.LeakyReLU(0.1)
    # yapf: enable

    def forward(self, x):
        x = self.lrelu1(self.bn1(self.conv1(x)))
        x = self.lrelu2(self.bn2(self.conv2(x)))
        x = self.lrelu3(self.bn3(self.conv3(x)))

        return x

class AutoCompressor(nn.Module):
    
    def __init__(self, in_channel, out_channel):
        super().__init__()
        self.compressor = Compressor(in_channel, out_channel)
        self.decompressor = Decompressor(in_channel, out_channel)

    def forward(self, x):
        x = self.compressor(x)
        x = self.decompressor(x)

        return x

class resnet_test(nn.Module):

    def __init__(self, model):
        super().__init__()
        self.resnet_model = models.resnet50(weights=None)
        self.autocompressor = model
        self.resnet_model.fc = nn.Sequential(
            nn.Linear(2048, 5749),
            nn.Dropout(0.5)
        )

    def forward(self, x):
        #for i in range(len(list(self.resnet_model))):
        for i, (n, m) in enumerate(self.resnet_model.named_children()):
            if i == 3:
                input_tensor = x
                output_tensor = self.autocompressor(x)
                x = output_tensor
                
            if n == 'fc':
                x = torch.flatten(x, 1)
                return x
            x = m(x)
                
        return x