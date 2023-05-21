# 深度卷積網絡的原理設計：一個簡單的SimpNet

  [原文鏈接](https://arxiv.org/pdf/1802.06205.pdf)

  作者：

  - Seyyed Hossein Hasanpour 
  - Mohammad Rouhani
  - Mohsen Fayyaz
  - Mohammad Sabokrou 
  - Ehsan Adeli

  譯者：

  - 陳曉偉

  ## 摘要

近年來，卷積神經網絡(CNN)獲得非常重大的成功，其代表就有VGGNet、ResNet和DenseNet等等，不過這些模型的參數達到了上億個(幾億到幾十億不等)，這就需要更加關注網絡推算所需要的計算資源，以及網絡所佔用的內存開銷。由於這些現實的問題，限制了其在訓練和優化的應用。這時，輕量級架構(比如：SqueezeNet)的提出，志在解決以上的問題。不過，要在計算資源和高效運行之間進行權衡，就會碰到精確度不高的問題。網絡低效的問題大部分源自於架構的點對點設計。本文在討論過程中會為構建高效的架構提出幾個原則，並會闡述在設計網絡結構過程中對於不同方面的考慮。此外，我們還會介紹一個新層——SAF-pooling，在加強網絡歸一化能力的同時，通過選擇最好的特徵保持網絡的簡單性。根據這些原則，我們提出一個簡單的網絡架構，稱為SimpNet。SimpNet架構根據提到的原則設計，其在計算/存儲效率和準確性之間有很好的折衷。SimpNet在一些知名性能測試集上的表現，要優於那些更深和更復雜的架構，比如VGGNet、ResNet和WideResidualNet等，並且在參數和操作數量上要比這些網絡少2~25倍。同時，我們在一些測試集上獲得了很不錯的結果(在模型精度和參數數量平衡方面)，比如CIFAR10，CIFAR100，MNIST和SVHN。SimpNet的實現可以在這裡看到：https://github.com/Coderx7/SimpNet

  ## 索引詞

  深度學習，卷積神經網絡，簡單網絡，分類，效率
