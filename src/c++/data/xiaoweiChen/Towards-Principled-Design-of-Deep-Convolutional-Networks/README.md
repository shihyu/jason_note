# 深度卷积网络的原理设计：一个简单的SimpNet

  [原文链接](https://arxiv.org/pdf/1802.06205.pdf)

  作者：

  - Seyyed Hossein Hasanpour 
  - Mohammad Rouhani
  - Mohsen Fayyaz
  - Mohammad Sabokrou 
  - Ehsan Adeli

  译者：

  - 陈晓伟

  ## 摘要

近年来，卷积神经网络(CNN)获得非常重大的成功，其代表就有VGGNet、ResNet和DenseNet等等，不过这些模型的参数达到了上亿个(几亿到几十亿不等)，这就需要更加关注网络推算所需要的计算资源，以及网络所占用的内存开销。由于这些现实的问题，限制了其在训练和优化的应用。这时，轻量级架构(比如：SqueezeNet)的提出，志在解决以上的问题。不过，要在计算资源和高效运行之间进行权衡，就会碰到精确度不高的问题。网络低效的问题大部分源自于架构的点对点设计。本文在讨论过程中会为构建高效的架构提出几个原则，并会阐述在设计网络结构过程中对于不同方面的考虑。此外，我们还会介绍一个新层——SAF-pooling，在加强网络归一化能力的同时，通过选择最好的特征保持网络的简单性。根据这些原则，我们提出一个简单的网络架构，称为SimpNet。SimpNet架构根据提到的原则设计，其在计算/存储效率和准确性之间有很好的折衷。SimpNet在一些知名性能测试集上的表现，要优于那些更深和更复杂的架构，比如VGGNet、ResNet和WideResidualNet等，并且在参数和操作数量上要比这些网络少2~25倍。同时，我们在一些测试集上获得了很不错的结果(在模型精度和参数数量平衡方面)，比如CIFAR10，CIFAR100，MNIST和SVHN。SimpNet的实现可以在这里看到：https://github.com/Coderx7/SimpNet

  ## 索引词

  深度学习，卷积神经网络，简单网络，分类，效率
