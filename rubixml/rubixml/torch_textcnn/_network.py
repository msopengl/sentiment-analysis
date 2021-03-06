from torch.autograd import Variable
import torch.nn.functional as F
import torch.nn as nn
import torch
import torchtext


class TextCNN(nn.Module):
    """ A typical convolutional neural network for text classification
    Paper: https://arxiv.org/pdf/1408.5882.pdf
    """

    def __init__(self,
                 vocab_size,
                 embed_dim,
                 class_num,
                 kernel_num,
                 kernel_sizes=[3, 4, 5],
                 dropout=0.5,
                 static=True):
        super(TextCNN, self).__init__()
        """
        Args:
            vocab_size: integer, the number of unique words in corpus
            embed_dim: integer, the dimension of word embedding
            kernel_num: integer, the number of kernels in CNN
            kernel_sizes: a list of integer, the types of kernels
            dropout: float, probability of an element to be zeroed.
            static: boolean, whether re-train the embedding layer
        """

        self.class_num = class_num
        self.static = static

        V = vocab_size
        D = embed_dim
        C = class_num
        Ci = 1  # input channel
        Co = kernel_num
        Ks = kernel_sizes

        self.embed = nn.Embedding(V, D)
        self.convs1 = nn.ModuleList([nn.Conv2d(Ci, Co, (K, D)) for K in Ks])
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(len(Ks) * Co, C)
        return

    def forward(self, x):
        x = self.embed(x)  # (N, W, D)

        if not self.static:
            x = Variable(x)

        x = x.unsqueeze(1)  # (N, Ci, W, D)
        x = [F.relu(conv(x)).squeeze(3) for conv in self.convs1]
        x = [F.max_pool1d(i, i.size(2)).squeeze(2) for i in x]

        x = torch.cat(x, 1)
        x = self.dropout(x)  # (N, len(Ks)*Co)
        logit = self.fc1(x)  # (N, C)
        if self.class_num > 1:
            y_pred = torch.softmax(logit)
        else:
            y_pred = torch.sigmoid(logit)
        return y_pred
