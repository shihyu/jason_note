# Ubuntu 休眠喚醒後登入密碼框無法輸入 — 排查與修復記錄

## 環境

- Ubuntu 24.04.4 LTS
- Kernel 6.17.0-35-generic
- ASUS PRIME Z790M-PLUS（桌上型）
- Intel i7-14700K
- 鍵盤：CX 2.4G Wireless Receiver（USB dongle 無線接收器）

## 症狀

休眠喚醒後進入登入或鎖定畫面，密碼框無法輸入。滑鼠正常。非每次都發生，偶發性。

這次重點是：鍵盤確定可以使用，但登入密碼框不吃鍵盤輸入。

先分兩類判斷：

1. **鍵盤完全失效**
   - `Caps Lock` 燈不反應
   - `Ctrl+Alt+F3` 無法切到 TTY
   - 拔插 USB 接收器後才恢復
   - 較像 USB HID / 無線接收器 / autosuspend 問題
2. **鍵盤可用，但密碼框不能輸入**
   - `Caps Lock` 或其他按鍵有反應
   - `Ctrl+Alt+F3` 可以切 TTY
   - 只有 GDM/GNOME 登入或鎖定畫面的密碼框不吃字
   - 較像 GDM/GNOME lock screen focus、input method 或 session unlock 問題

## 立即脫困流程

按破壞性由低到高處理。

### 1. 重新取得輸入焦點

在登入或鎖定畫面先試：

1. 按 `Esc`
2. 用滑鼠點密碼框
3. 按 `Ctrl+Alt+F3` 切到 TTY
4. 再按 `Ctrl+Alt+F2` 或 `Ctrl+Alt+F1` 回到圖形畫面

如果回到圖形畫面後密碼框恢復，主因比較可能是 lock screen / GDM focus 卡住。

### 2. 從 TTY 解鎖 session

如果 `Ctrl+Alt+F3` 可用：

```bash
loginctl list-sessions
loginctl unlock-sessions
```

然後按 `Ctrl+Alt+F2` 或 `Ctrl+Alt+F1` 回圖形畫面。

### 3. 只在必要時重啟 GDM

如果圖形登入畫面仍卡住，且可以接受圖形 session 被中斷，才使用：

```bash
sudo systemctl restart gdm3
```

注意：這可能會關掉目前圖形 session，未儲存工作可能遺失。

### 4. USB 接收器分支

如果鍵盤本身也失效，先拔掉 USB 接收器，重插後等 3 秒。若重插後恢復，才優先懷疑 USB autosuspend 或 USB 控制器 resume 問題。

## 可能原因

USB 無線接收器在休眠時被 Linux USB autosuspend 斷電，喚醒時 RF 無線協定 handshake 未能自動重建，導致 HID 鍵盤端點無法正確註冊回輸入層。

但如果鍵盤確定可用，只是密碼框不能輸入，原因不一定是 USB。更可能是：

- GNOME lock screen 或 GDM greeter 的輸入焦點卡住
- input method / IBus 狀態異常
- resume 後圖形 session 與 lock screen 狀態不同步

## Debug 指令

### 確認 USB autosuspend 參數是否生效

```bash
cat /proc/cmdline
cat /sys/module/usbcore/parameters/autosuspend
```

若有套用 `usbcore.autosuspend=-1`，第二個指令通常會顯示 `-1`。

### 查 USB / HID / resume log

目前這次開機：

```bash
journalctl -b -k --no-pager | rg -i 'usb|hid|xhci|suspend|resume|keyboard|input'
```

前一次開機：

```bash
journalctl -b -1 -k --no-pager | rg -i 'usb|hid|xhci|suspend|resume|keyboard|input'
```

### 查 GDM / GNOME / input method log

```bash
journalctl -b --no-pager | rg -i 'gdm|gnome-shell|ibus|input|keyboard'
```

如果 USB/HID 沒有斷線或重新註冊失敗，但 GDM、GNOME shell 或 IBus 有錯誤，優先處理登入畫面/input method 分支。

## 永久修復選項

### 選項 A：USB autosuspend 修復

關閉 USB 自動省電，防止接收器在休眠時斷電：

```bash
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash usbcore.autosuspend=-1"/' /etc/default/grub
sudo update-grub
sudo reboot
```

重開機後永久生效。

回滾：

```bash
sudo sed -i 's/ usbcore.autosuspend=-1//g' /etc/default/grub
sudo update-grub
sudo reboot
```

適用情境：

- 鍵盤接收器拔插後恢復
- kernel log 有 USB/HID resume 異常
- `Ctrl+Alt+F3` 也無法使用

### 選項 B：登入畫面 / 鎖定畫面分支

如果鍵盤可用但密碼框不吃輸入，先不要把問題歸因為 USB。優先收集 GDM/GNOME log，並用「立即脫困流程」確認是否是 focus 或 lock screen 狀態問題。

可觀察：

- 切 TTY 再切回來是否恢復
- `loginctl unlock-sessions` 是否能解鎖
- 是否只有 suspend resume 後發生
- 是否和輸入法切換、螢幕鎖定、外接螢幕喚醒順序有關

## 副作用與風險

- `usbcore.autosuspend=-1` 會全域關閉 USB autosuspend。桌機通常影響很小；筆電可能增加耗電。
- `sudo systemctl restart gdm3` 可能中斷目前圖形 session，未儲存工作可能遺失。
- 如果根因是 GNOME lock screen/input focus，USB autosuspend 修復可能不會改善。

## 參考

- [Ask Ubuntu: Keyboard not working after suspend on Ubuntu 22.04](https://askubuntu.com/questions/1418676/keyboard-not-working-after-suspend-on-ubuntu-22-04)
- [Ubuntu Discourse: Keyboard unresponsive after resume from suspend](https://discourse.ubuntu.com/t/keyboard-unresponsive-after-resume-from-suspend-lid-close/64070)
