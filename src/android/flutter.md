# Flutter

在Ubuntu上進行Flutter開發，您需要安裝Android SDK。Flutter使用Android SDK來構建和運行Android應用程序。以下是安裝Android SDK的簡單步驟：

**下載 Android SDK：** 您可以從[Android 開發者網站](https://developer.android.com/studio#command-tools)下載 Android SDK Command Line Tools。選擇壓縮檔案（ZIP）版本。

**解壓縮檔案：** 解壓縮下載的檔案到您選擇的目錄。例如，您可以將其解壓縮到`/usr/local/android-sdk`目錄下。

```sh
sudo mkdir /usr/local/android-sdk
sudo tar -xvzf commandlinetools-linux-xxxxxx_latest.zip -C /usr/local/android-sdk
```

**設定環境變量：** 在您的`~/.bashrc`或`~/.zshrc`文件中添加以下環境變量：

```sh
export ANDROID_SDK_ROOT=/usr/local/android-sdk
export PATH="$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/tools/bin"
```

然後在終端機中運行`source ~/.bashrc`或`source ~/.zshrc`以應用變更。

**安裝SDK組件：** 運行以下命令來安裝所需的SDK組件：

```sh
sdkmanager --install "platforms;android-30" "build-tools;30.0.3" "platform-tools"
```

這將安裝Android 30平臺、30.0.3版本的構建工具以及平臺工具。

現在，您已經成功安裝了Android SDK，可以開始使用Flutter來開發Android應用程序。請注意，這些步驟可能需要根據您的系統配置和Android SDK版本進行微調。

---

## 在Ubuntu上安裝Flutter的最簡單步驟如下：

1. 在終端機中運行以下命令，下載Flutter SDK：

```sh
git clone https://github.com/flutter/flutter.git
```

1. 將Flutter的`bin`目錄添加到您的`PATH`環境變量中。您可以在`~/.bashrc`或`~/.zshrc`文件中添加類似以下的行：

```sh
export PATH="$PATH:`pwd`/flutter/bin"
```

1. 運行以下命令來檢查Flutter的依賴項：

```sh
flutter doctor
```

1. 根據`flutter doctor`的輸出，安裝所需的依賴項，例如Android Studio、Xcode（僅限Mac）、Dart等。
2. 安裝完成後，重新啟動終端機，然後您應該能夠運行Flutter命令，例如：

```sh
flutter --version
```

現在，您已經在Ubuntu上成功安裝了Flutter，可以開始開發您的Flutter應用程序了。

## Ubuntu 怎麼寫個 flutter 的 hello world apk

要在Ubuntu上創建一個Flutter的Hello World APK，請按照以下步驟進行：

1. **安裝Flutter：** 如果您尚未安裝Flutter，請參照前面的步驟進行安裝。

2. **創建Flutter項目：** 在終端機中運行以下命令來創建一個新的Flutter項目：

   ```shell
   flutter create hello_world
   ```

   這會在當前目錄中創建一個名為`hello_world`的Flutter項目。

3. **進入項目目錄：** 進入創建的項目目錄：

   ```shell
   cd hello_world
   ```

4. **運行應用：** 運行以下命令來確保一切正常：

   ```shell
   flutter run
   ```

   這將啟動您的應用程序。您可以在模擬器或連接的設備上看到Hello World應用程序運行。

5. **生成APK：** 當您確保應用程序運行正常後，您可以生成APK文件。在項目目錄中運行：

   ```shell
   flutter build apk
   ```

   這將在`build/app/outputs/flutter-apk/`目錄中生成一個APK文件，例如`app-release.apk`。

現在，您已經成功生成了一個Flutter Hello World APK。您可以將這個APK安裝到Android設備上，或者在模擬器中運行。



## 在Flutter中，您可以使用Android Studio或Visual Studio Code等集成開發環境（IDE）來設計和編輯您的UI

這兩個IDE都提供了可視化的UI編輯器，使得設計和排版Flutter應用程序變得更加容易。

以下是使用Android Studio的基本步驟：

1. **打開Android Studio：** 啟動Android Studio。

2. **打開您的Flutter項目：** 選擇您的Flutter項目文件夾，並打開它。

3. **選擇`lib/main.dart`文件：** 通常，您的主應用程序代碼位於`lib/main.dart`中。選擇該文件以打開代碼編輯器。

4. **切換到設計模式：** 在Android Studio中，有兩種模式，即代碼模式和設計模式。您可以在右下角的選項卡中切換這兩種模式。

   ![Android Studio Design Mode](https://developer.android.com/studio/images/intro/layout-editor_2x.png)

5. **使用可視化編輯器：** 在設計模式中，您可以使用可視化編輯器拖放UI元素，例如按鈕、文本框等，並調整它們的屬性。

   ![Android Studio Visual Editor](https://developer.android.com/studio/images/intro/layout-editor-design_2x.png)

6. **查看預覽：** 您可以在右上角的裝置預覽區域查看您的UI在不同設備上的預覽。

   ![Android Studio Preview](https://developer.android.com/studio/images/intro/layout-editor-toolbar_2x.png)

7. **保存並查看變更：** 完成設計後，請保存文件。您可以回到代碼模式查看生成的Dart代碼。然後，使用`flutter run`命令在模擬器或設備上運行應用程序，查看您的UI的實際外觀。

類似的操作也適用於Visual Studio Code等其他Flutter IDE。這些IDE都提供了方便的工具，使得在Flutter應用程序中進行UI設計和開發變得更加直觀。