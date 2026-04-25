import torch
import torch.nn as nn
from safetensors.torch import save_file

# 1. 定義一個 PyTorch FCN 模型
class SimpleFCN(nn.Module):
    def __init__(self):
        super(SimpleFCN, self).__init__()
        # 關鍵細節 1: fc1 (10 -> 50), 預設有 bias
        self.fc1 = nn.Linear(10, 50)
        # 關鍵細節 2: fc2 (50 -> 20), 明確指定 bias=False
        self.fc2 = nn.Linear(50, 20, bias=False)
        # 關鍵細節 3: fc3 (20 -> 5), 預設有 bias
        self.fc3 = nn.Linear(20, 5)

    def forward(self, x):
        # (這裡省略 relu，因為我們只關心權重)
        x = self.fc1(x)
        x = self.fc2(x)
        return self.fc3(x)

if __name__ == "__main__":
    # 為了可重複性，設定隨機種子
    torch.manual_seed(42)
    model = SimpleFCN().to(torch.device("cpu"))

    # 2. 取得模型權重 (state_dict)
    #    這將包含 'fc1.weight', 'fc1.bias', 
    #              'fc2.weight', 
    #              'fc3.weight', 'fc3.bias'
    model_weights = model.state_dict()

    # 3. 儲存為 safetensors 檔案
    save_file(model_weights, "simple_fcn.safetensors")
    print("模型已儲存為 simple_fcn.safetensors")