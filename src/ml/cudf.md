## CUDF

https://pytorch.org/



```sh
nvidia-smi 


Tue Jun  4 00:12:58 2024       
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.171.04             Driver Version: 535.171.04   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA GeForce RTX 3060        Off | 00000000:01:00.0  On |                  N/A |
|  0%   58C    P8              18W / 170W |   2476MiB / 12288MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
                                                                                         
+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|    0   N/A  N/A      2592      G   /usr/lib/xorg/Xorg                         1377MiB |
|    0   N/A  N/A      2867      G   /usr/bin/gnome-shell                         82MiB |
|    0   N/A  N/A      4678      G   /usr/libexec/xdg-desktop-portal-gnome        22MiB |
|    0   N/A  N/A     47979      G   /usr/bin/nautilus                           492MiB |
|    0   N/A  N/A     57448      G   ...AAAAAAAACAAAAAAAAAA= --shared-files       80MiB |
|    0   N/A  N/A    315568      G   /usr/bin/yelp                                 2MiB |
|    0   N/A  N/A    508948      G   ...seed-version=20240531-130126.993000      288MiB |
|    0   N/A  N/A    513981      G   /usr/bin/gnome-text-editor                   12MiB |
|    0   N/A  N/A    969401      G   ...irefox/4336/usr/lib/firefox/firefox       19MiB |
|    0   N/A  N/A   1030653      G   ...ures=SpareRendererForSitePerProcess       73MiB |
+---------------------------------------------------------------------------------------+
```



```
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

```
pip install --extra-index-url=https://pypi.nvidia.com cudf-cu12
```

```python
import cudf

tips_df = cudf.read_csv("https://github.com/plotly/datasets/raw/master/tips.csv")
tips_df["tip_percentage"] = tips_df["tip"] / tips_df["total_bill"] * 100
#
# display average tip by dining party size
print(tips_df.groupby("size").tip_percentage.mean())
```

