import numpy as np
import torch
import torch.nn as nn
from torch import Tensor

from src.models.feat_vae import FeatVAE
from src.models.classifier import ResnetEmbedder, FeatClassifier
from src.utils.lll import prune_logits
from src.models.layers import Identity


class LatGMVAE(nn.Module):
    def __init__(self, config, attrs: np.ndarray=None):
        super(LatGMVAE, self).__init__()

        self.config = config
        if not attrs is None: self.register_buffer('attrs', torch.tensor(attrs))
        self.vae = FeatVAE(self.config, attrs)

        if self.config.get('identity_embedder'):
            self.embedder = Identity()
        else:
            self.embedder = ResnetEmbedder(config.pretrained, config.resnet_type)

        self.classifier = FeatClassifier(config, attrs)

    def forward(self, x) -> Tensor:
        return self.classifier(self.embedder(x))

    def compute_pruned_predictions(self, x: Tensor, output_mask: np.ndarray) -> Tensor:
        return self.classifier.compute_pruned_predictions(self.embedder(x), output_mask)

    def sample(self, y: Tensor) -> Tensor:
        return self.vae.generate(y)
