# Spacemacs

spacemacs，是一個給vimer的Emacs。
## 簡介
spacemacs是一個專門給那些習慣vim的操作，同時又嚮往emacs的擴展能力的人。它非常適合我這種折騰過vim，配置過emacs的人，但同時也歡迎任何沒有基礎的新人使用。簡單來說，它是一個開箱即用的Emacs！這對一個比很多人年齡都大的軟件來說是一件極其不容易的事情。

## 安裝
由於筆者自己在linux平臺，並沒有windows平臺的經驗，所以在這裡便不獻醜了，期待各位補充。另外，windows平臺真的需要麼，斜眼瞅向了Visual Studio。

### Emacs安裝

在*nix系統中，都不一定會默認安裝了Emacs，就算安裝了，也不一定是最新的版本。在這裡，我強烈建議各位卸載掉系統自帶的Emacs，因為你不知道系統給你安裝的是個什麼奇怪的存在，最遭心的，我碰見過只提供閹割版Emacs的linux發行版。

建議各位自己去emacs項目主頁下載Emacs-24.5（本書寫作時的最新版）極其以上版本，然後下載下來源碼。至於Emacs的安裝也非常簡單，linux平臺老三步。

```bash
./configure
make
sudo make install
```

什麼？你沒有make？沒有GCC？缺少依賴？
請安裝它們……

### Spacemacs安裝

前面說了,Spacemacs就是個Emacs的配置文件庫，因此我們可以通過非常簡單的方式安裝它：

```bash
git clone https://github.com/syl20bnr/spacemacs ~/.emacs.d
mv ~/.emacs ~/_emacs.backup
cd ~/.emacs.d
echo $(git describe --tags $(git rev-list --tags --max-count=1)) | xargs git checkout
```

其中，後三行是筆者加的，這裡必須要吐槽一下的是，Spacemacs的master分支實際上是極其落後而且有錯誤的！其目前的release都是從develop分支上打的tag。

因此，一！定！不！要！用！主！分！支！

最後，之所以要加最後一行，這是筆者安裝的時候的release的一個小bug，沒有這個文件的話,emacs並不會順利的完成初始化。

好了，配置文件我們已經搞定了，接下來，啟動你的emacs，spacemacs會自動的去網上下載你需要的插件安裝包。另外，能自備梯子的最好，因為你要下的東西不大，但是這個網絡確實比較捉急。

### 前期準備

為了讓Spacemacs支持Rust，我們還需要一點小小的配置。首先，請參照[前期準備](../editors/before.md)，安裝好你的racer。

在這裡，強烈建議將racer的環境變量加入到系統變量中(通常他們在`/etc/profile/`裡進行配置)並重新啟動系統，因為真的有很多人直接點擊emacs的圖標啟動它的，這樣做很可能導致emacs並不繼承自己的環境變量，這是很令人無奈的。

## 完成配置

### 修改標準的Spacemacs配置。

Spacemacs文檔中提供了一份標準的spacemacs[配置文件](https://github.com/syl20bnr/spacemacs/blob/master/core/templates/.spacemacs.template)，你可以將其加入到你自己的`~/.spacemacs`文件中。

這裡，我們需要修改的是其關於自定義插件的部分：

```lisp
(defun dotspacemacs/layers ()
  "Configuration Layers declaration.
You should not put any user code in this function besides modifying the variable
values."
  (setq-default
   ;; Base distribution to use. This is a layer contained in the directory
   ;; `+distribution'. For now available distributions are `spacemacs-base'
   ;; or `spacemacs'. (default 'spacemacs)
   dotspacemacs-distribution 'spacemacs
   ;; List of additional paths where to look for configuration layers.
   ;; Paths must have a trailing slash (i.e. `~/.mycontribs/')
   dotspacemacs-configuration-layer-path '()
   ;; List of configuration layers to load. If it is the symbol `all' instead
   ;; of a list then all discovered layers will be installed.
   dotspacemacs-configuration-layers
   '(
     ;; ----------------------------------------------------------------
     ;; Example of useful layers you may want to use right away.
     ;; Uncomment some layer names and press <SPC f e R> (Vim style) or
     ;; <M-m f e R> (Emacs style) to install them.
     ;; ----------------------------------------------------------------
     auto-completion
     better-defaults
     git
     spell-checking
     syntax-checking
     version-control
     rust
     )
   ;; List of additional packages that will be installed without being
   ;; wrapped in a layer. If you need some configuration for these
   ;; packages then consider to create a layer, you can also put the
   ;; configuration in `dotspacemacs/config'.
   dotspacemacs-additional-packages '()
   ;; A list of packages and/or extensions that will not be install and loaded.
   dotspacemacs-excluded-packages '()
   ;; If non-nil spacemacs will delete any orphan packages, i.e. packages that
   ;; are declared in a layer which is not a member of
   ;; the list `dotspacemacs-configuration-layers'. (default t)
   dotspacemacs-delete-orphan-packages t))

;; ...
;; 以下配置文件內容省略
;; ...
```

注意`dotspacemacs-configuration-layers`的配置和標準配置文件的不同。

將配置文件保存，然後重啟你的emacs，當然，我們也可以按`SPC f e R`來完成重載配置文件的目的，然後你會發現emacs會開始下一輪下載，稍等其完成。

在上一步中，我們已經完成了對Racer的環境變量的配置，所以，現在你的Spacemacs已經配置完成了！這種簡便的配置形式，幾乎能和Atom抗衡了。

### 按鍵綁定
如下，spacemacs默認提供了幾種按鍵綁定，但是，筆者並不覺得這些很好用，還是更喜歡用命令行。

| Key Binding | Description                       |
|-------------|-----------------------------------|
| ~SPC m c c~ | compile project with Cargo        |
| ~SPC m c t~ | run tests with Cargo              |
| ~SPC m c d~ | generate documentation with Cargo |
| ~SPC m c x~ | execute the project with Cargo    |

## 嘗試

現在開始，我們可以打開一個Cargo項目，並且去使用它了。你會驚訝的發現racer/flycheck/company這三個插件配合在一起的時候是那麼的和諧簡單。
