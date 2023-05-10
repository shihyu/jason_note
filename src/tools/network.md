# ufw：簡易防火牆設置

出處:https://noob.tw/ufw/

Linux 上的 iptables 可能太難，我們不是專業的資安工程師，也不是什麼 Linux 老鳥。像我們這種菜鳥，還是用 ufw 就好了。這篇整理一些常用的 ufw 設定。

## 安裝 ufw

ufw 的全名是 Uncomplicated Firewall，意思是不複雜的防火牆。它的指令不但好記，寫好的規則也淺顯易懂，不會像 iptables 的裹腳布又臭又長。

大部分的 Ubuntu 系統應該都已經裝好 ufw。如果你是 Debian，或是什麼特別瘦身版的 Ubuntu 的話，可以透過以下指令安裝：

```bash
sudo apt-get install ufw
```

## 設定防火牆預設規則

如果你想要規則嚴一點，可以預設封鎖所有通訊埠，再選擇性打開幾個 port；你也可以預設開放所有 port，然後再封鎖幾個 port。預設允許/封鎖的指令如下：

```bash
sudo ufw default allow # 預設允許
sudo ufw default deny # 預設封鎖
```

## 允許/封鎖通訊埠（port）

如果你要允許 SSH port 的話，可以這樣下：

```bash
sudo ufw allow ssh
```

或是

```bash
sudo ufw allow 22
```

也可以允許或封鎖其他的 port：

```bash
sudo ufw allow 80 # 允許 80
sudo ufw allow 443 # 允許 443
sudo ufw deny 3389 # 封鎖 3389
sudo ufw deny 21 # 封鎖 21
```

甚至可以一次允許一個範圍的 port：

```bash
sudo ufw allow 6000:6007/tcp # 允許 TCP 6000~6007
sudo ufw allow 6000:6007/udp # 允許 UDP 6000~6007
```

## 來自特定 IP 的規則

上面的規則是針對所有 IP，如果你想要針對某些 IP 可以不受控管，你也可以這樣設定：

```bash
sudo ufw allow from 192.168.11.10 # 允許 192.168.11.10 的所有連線
sudo ufw allow from 192.168.11.0/24 # 允許 192.168.11.1~192.168.11.255 的所有連線
sudo ufw deny from 192.168.11.4 # 封鎖 192.168.11.4 的所有連線
```

如果你只是不想讓某個小明偷偷連到你的 SSH Port，你也可以針對他封鎖：

```bash
sudo ufw deny from 192.168.11.7 to any port 22
```

## 查看目前設了什麼規則

推薦使用這個指令來看目前設了什麼規則：

```bash
sudo ufw status numbered
```

這個指令會幫你把規則前面加上編號：

```
Numbered Output:
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22                         ALLOW IN    Anywhere
[ 2] 80                         ALLOW IN    Anywhere
[ 3] 443                        ALLOW IN    Anywhere
```

如果你突然不喜歡某個規則了，可以直接刪除它：

```bash
sudo ufw delete 3
```

那個規則就不見囉！

## 開啟/關閉/重設防火牆

設定完所有規則後，記得把防火牆打開。

> 如果你是用 SSH 連線，別忘了要先 allow 自己的 SSH 連線。

```bash
sudo ufw enable # 啟用防火牆
sudo ufw disable # 停用防火牆
```

如果你把規則改爛了，想要重新來過的話，可以重設：

```bash
sudo ufw reset
```