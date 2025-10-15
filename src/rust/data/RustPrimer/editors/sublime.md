# Sublime

Sublime Text是一款非常有名的文本編輯器，其本身也具備強大的插件機制。通過配置各種插件可以在使用Sublime Text編輯rust代碼時獲得更加良好的支持。

本文主要展示在已經預裝rust的Windows環境下的安裝，如果您還沒有安裝rust，請先參照本書的[安裝章節](../install/install_rust_on_windows.md)安裝rust。

## 安裝

### Sublime Text3安裝

請在 [Sublime Text3官網](http://www.sublimetext.com/3)上選擇適合當前機器版本的Sublime Text版本進行下載和安裝。

### rust的安裝

請在rust官網的[下載頁面](https://www.rust-lang.org/downloads.html)下載rust的源代碼壓縮包並在本地解壓縮安裝，在稍後的配置環節我們將會用到這個路徑。如果國內下載速度過慢，可以考慮使用中科大的[鏡像](http://mirrors.ustc.edu.cn/)下載rust源碼包。

### 下載Rust並編譯代碼提示插件racer

具體安裝和編譯內容請查看本章第一節的[安裝準備](../editors/before.md)，請牢記編譯後的racer.exe文件路徑，在稍後的配置環節中我們將用到它。

## 配置

### Sublime Text3相關插件安裝

#### 安裝Package Control

Sublime Text3在安裝各種插件前需要先安裝Package Control，如果您的編輯器已安裝Package Control請跳過本段直接安裝rust相關插件。

您可以查看[Package Control官網](https://packagecontrol.io/installation)學習如何安裝。
也可以直接在編輯器中使用 `ctrl+~` 快捷鍵啟動控制檯，粘貼以下代碼並回車進行安裝。

```shell

import urllib.request,os,hashlib; h = '2915d1851351e5ee549c20394736b442' + '8bc59f460fa1548d1514676163dafc88'; pf = 'Package Control.sublime-package'; ipp = sublime.installed_packages_path(); urllib.request.install_opener( urllib.request.build_opener( urllib.request.ProxyHandler()) ); by = urllib.request.urlopen( 'http://packagecontrol.io/' + pf.replace(' ', '%20')).read(); dh = hashlib.sha256(by).hexdigest(); print('Error validating download (got %s instead of %s), please try manual install' % (dh, h)) if dh != h else open(os.path.join( ipp, pf), 'wb' ).write(by)

```

#### rust相關插件

在編輯器下使用快捷鍵 `ctrl+shift+p` 啟動命令行工具，輸入Install Package按回車進入插件安裝，選擇或輸入插件名稱並回車即可完成插件的安裝。

使用上述方式安裝Rust插件\(rust語法高亮\)、RustAutoComplete\(rust代碼提示和自動補全插件\)。

此時安裝尚未完成，我們需要將本地的 racer.exe配置進RustAutoComplete插件中。打開編輯器頂端的Preferences選項卡，依次 Preferences->Package Settings->RustAutoComplete->Settings-User 來打開 RustAutoComplete 的配置文件，在文件中配置以下信息並保存。

```shell
{
  "racer": "E:/soft/racer-master/target/release/racer.exe",
  "search_paths": [    "E:/soft/rustc-1.7.0/src"   ]
}
```

其中racer是編譯後的racer.exe程序的絕對路徑。search_paths是rust源碼文件下src目錄的絕對路徑。

編輯器重啟後插件即可生效。

## 快速編譯

Sublime本身支持多種編譯系統，在Tools選項卡下的Build System中選擇Rust或者Cargo作為編譯系統，選中後使用快捷鍵 `ctrl+B` 即可對代碼進行快速編譯。

