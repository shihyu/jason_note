# python

- [Python asyncio 從不會到上路](https://myapollo.com.tw/zh-tw/begin-to-asyncio/)

- [python的asyncio模組](https://ithelp.ithome.com.tw/users/20107274/articles)

## 利用Conda嚐鮮Python 3.10

```sh
conda create -n py310 python=3.10 -c conda-forge -y
conda activate py310
```

### 建立和管理 Python 虛擬環境

```shell
列出 Conda 環境
使用以下命令來列出所有 Conda 環境：
conda env list

創建虛擬環境
若要創建一個名為 myenv 的虛擬環境，並指定 Python 版本為 3.9，可以使用以下命令：
/home/shihyu/miniconda3/envs/python3.9/bin/python3.9 -m venv myenv


啟動虛擬環境
在創建虛擬環境後，使用以下命令來啟動它：
source myenv/bin/activate


退出虛擬環境
若要退出虛擬環境，使用以下命令：
deactivate

刪除虛擬環境
若要刪除虛擬環境，可以直接刪除環境目錄：
rm -rf myenv
```

