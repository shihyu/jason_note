## 如何在Linux上通過cgroup限制一個處理程序使用CPU和記憶體

https://blog.csdn.net/weixin_37871174/article/details/130390336

Cgroup（Control Group）是 Linux 核心的一個功能，可以通過它來限制處理程序的 CPU 和記憶體佔用。Cgroup 實現了對系統資源的細粒度控制和管理，可以將一組處理程序放入同一個 Cgroup 中，並對該 Control Group 中的所有處理程序共享相應的資源配額。

下面舉個實際的例子，演示如何使用 Cgroup 限制一個處理程序的 CPU 佔用率和記憶體使用量：

1. 首先需要安裝 cgroup 工具包，在 Ubuntu 系統上可以執行以下命令進行安裝： 

   ```sh
   sudo apt-get install cgroup-tools
   ```

2. 建立一個名為 mycg 的控制組，以限制該組中的處理程序的 CPU 佔用率和記憶體使用量。在 shell 終端輸入下列命令：

   ```sh
   sudo mkdir /sys/fs/cgroup/cpu_mytainer
   sudo mkdir /sys/fs/cgroup/memory_mytainer
   ```

3. 設定 cpu 資源限制：

   ```sh
   echo "10000" > /sys/fs/cgroup/cpu_mytainer/cpu.cfs_quota_us #設定每10ms分配給cgroup桶的最大時間片值 
   echo "200000" > /sys/fs/cgroup/cpu_mytainer/cpu.cfs_period_us #設定每次時間輪轉過多少微秒 
   ```

這兩行程式碼告訴核心同時運行的程序切換超時參數，即當前可佔用 10ms 核心時間，然後必須讓出時間，並等待 200ms 核心時間過後再佔用，以達到限制CPU使用的目地。

4. 設定memory資源限制：

   ```sh
   echo "50M" > /sys/fs/cgroup/memory_mytainer/memory.limit_in_bytes #設定cgroup總共最多能夠使用記憶體大小
   ```

   這條命令表示限制 mycg 這個 Cgroup 的處理程序總佔用記憶體不得超過 50MB。 

5. 建立一個新處理程序並將它加入 mycg 中，然後觀察該處理程序利用率是否受到限制。例如我們建立一個死循環 c

   ```c
   #include <stdio.h>
   
   int main()
   {
       while(1){
           int a=100000000,b;
           b=a/b;
       }
       return 0;
   }
   ```

編譯成可執行檔案 test.out 並運行如下程式碼：

```sh
sudo cgcreate -a root:root -g cpu_mytainer,memory_mytainer:/mycg  
sudo echo $PID >>/sys/fs/cgroup/cpu_mytainer/tasks 
sudo echo $PID >>/sys/fs/cgroup/memory_mytainer/tasks  
```

其中 PID 是指上面循環程序 test.out 的處理程序 ID。

6. 使用 `ps` 命令檢查處理程序的CPU和記憶體使用情況：

   ```sh
   ps aux | grep test.out
   ```

   你可以看到產生了類似以下的輸出:

```sh
USER      PID    %CPU     %MEM            VSZ         RSS       TTY     STAT      START         TIME        COMMAND
root     3833    10.0     0.1           62820        2580   pts/9    R     11:56         00:00:30     ./test.out
```

說明測試程序的CPU使用率已經被成功限制在10%以內，而記憶體佔用不會超過50MB。

## limit chrome

```sh
sudo chmod o+w /sys/fs/cgroup/cgroup.procs


sudo cgcreate -t $USER:$USER -a $USER:$USER  -g memory,cpuset:limitchrome
# Limit RAM to 1.5G roughly
echo 1600000000 | sudo tee /sys/fs/cgroup/limitchrome/memory.limit_in_bytes

echo 0-4 | sudo tee /sys/fs/cgroup/limitchrome/cpuset.cpus
# Run chrome in this cgroup
cgexec -g memory,cpuset:limitchrome /opt/google/chrome/google-chrome --profile-directory=Default
# Delete the cgroup (not required)
sudo cgdelete -g memory,cpuset:limitchrome
```

