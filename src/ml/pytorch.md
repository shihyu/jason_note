# PyTorch 學習筆記

colab 使用GPU 的方法

Edit ->NoteBook Settings 選GPU

![img](images/1*HpmXaFjFCDL_jAtLaYEeGw.jpeg)

如果要將定義好的張量放到GPU上執行，可以用x.cuda()來指定

```python
import torch
import numpy as np
x_tensor = torch.rand(5,3)
y_numpy = np.random.rand(5,3)
x_numpy = x_tensor.numpy()
y_tensor = torch.from_numpy(y_numpy)

print(x_tensor)
print(x_numpy)
print(y_numpy)
print(y_tensor)

if torch.cuda.is_available():
    x = x_tensor.cuda()
    y = y_tensor.cuda()
    print(x+y)
```

關於自動微分變數，在使用自動微分變數後，針對後續變數的計算，系統會自動展開計算突來運算。也因為這個關係，可以很快地運用.backward 來執行反向傳播演算法。

下面的例子宣告x 是個張量變數(tensor)，無法調用x.grad_fn方法

```python
import torch
import numpy as np
x = torch.ones(3,3)
y = x + 10
print(x)
print(x.grad_fn)
```

傳回

```
tensor([[1., 1., 1.], [1., 1., 1.], [1., 1., 1.]])
None
```

宣告x為自動微分變數， x = Variable(torch.ones(2,2),requires_grad = True)

```python
import torch
import numpy as np
from torch.autograd import Variable
x = Variable(torch.ones(2,2),requires_grad = True)
y = x + 2
print(y.grad_fn)
```

傳回 <AddBackward0 object at 0x7fc37bd17438>

```python
import torch
import numpy as np
from torch.autograd import Variable
num_x = np.array([[1.0, 2.0],[3.0,4.0]])
tensor_x = torch.from_numpy(num_x)
x = Variable(tensor_x,requires_grad = True)
y = x + 2
z = y*y
print(z)
m = torch.mean(z)
print(m)
```

傳回

tensor([[ 9., 16.], [25., 36.]], dtype=torch.float64, grad_fn=<MulBackward0>) tensor(21.5000, dtype=torch.float64, grad_fn=<MeanBackward0>)

```python
import torch
import numpy as np
from torch.autograd import Variable
num_x = np.array([[1.0, 2.0],[3.0,4.0]])
tensor_x = torch.from_numpy(num_x)
x = Variable(tensor_x,requires_grad = True)
y = x + 2
z = y*y   #等價  z=torch.mul(y, y)
m = torch.mean(z)
m.backward()
print(x.grad)
```

傳回

tensor([[1.5000, 2.0000]

, [2.5000, 3.0000]], dtype=torch.float64)