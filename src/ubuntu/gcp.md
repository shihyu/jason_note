



## 從gcp 瀏覽器 ssh 登入

```sh
sudo su
sudo adduser  shihyu
sudo su shihyu

mkdir ~/.ssh
copy 要登入gcp的主機公鑰到 gcp VM 的~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 644 ~/.ssh/authorized_keys
```

之後就可以使用 shihyu 帳號登入囉～

```sh
# sudo vim /etc/ssh/sshd_config
修改地方是
LoginGraceTime 指定時間
PermitRootLogin yes
StrictModes yes
PasswordAuthentication yes
修改完成後大概是這樣
```

