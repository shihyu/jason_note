# Ubuntu 休眠喚醒後鍵盤無法輸入 — 修復記錄

## 環境

- Ubuntu 24.04.4 LTS
- Kernel 6.17.0-35-generic
- ASUS PRIME Z790M-PLUS（桌上型）
- Intel i7-14700K
- 鍵盤：CX 2.4G Wireless Receiver（USB dongle 無線接收器）

## 症狀

休眠喚醒後進入登入畫面，鍵盤完全無法輸入密碼。滑鼠正常。非每次都發生，偶發性。

## 原因

USB 無線接收器在休眠時被 Linux USB autosuspend 斷電，喚醒時 RF 無線協定 handshake 未能自動重建，導致 HID 鍵盤端點無法正確註冊回輸入層。

## 解法

關閉 USB 自動省電，防止接收器在休眠時斷電：

```bash
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash usbcore.autosuspend=-1"/' /etc/default/grub
sudo update-grub
sudo reboot
```

重開機後永久生效。

## 副作用

無。桌機不依賴電池，USB 不省電對功耗影響可忽略。

## 替代方案（免重開自救）

下次發生時：

1. 拔掉 USB 接收器 → 重插 → 等 3 秒
2. 或 `Ctrl+Alt+F3` → 登入終端 → `sudo systemctl restart gdm3`

## 參考

- [Ask Ubuntu: Keyboard not working after suspend on Ubuntu 22.04](https://askubuntu.com/questions/1418676/keyboard-not-working-after-suspend-on-ubuntu-22-04)
- [Ubuntu Discourse: Keyboard unresponsive after resume from suspend](https://discourse.ubuntu.com/t/keyboard-unresponsive-after-resume-from-suspend-lid-close/64070)
