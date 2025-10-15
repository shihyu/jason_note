筒子們好，我們又見面了。之前第5章，我們一起探討了cargo的一些常用的基本技能。通過第5章的學習，大家基本能解決日常項目開發中遇到的大多數問題。但實際上，cargo提供給我們所使用的功能不僅限於此。我只想說一個字：cargo很好很強大，而且遠比你想象的強大。
本章將深入探討cargo的一些細節問題，這包括以下幾個方面：

- 基於語義化版本的項目版本聲明與管理
- cargo的toml描述文件配置字段詳細參考

# 基於語義化版本的項目版本聲明與管理
我們在使用toml描述文件對項目進行配置時，經常會遇到項目版本聲明及管理的問題，比如：

```toml
[package]
name = "libevent_sys"
version = "0.1.0"

[dependencies]
libc = "0.2"

```

這裡package段落中的version字段的值，以及dependencies段落中的libc字段的值，這些值的寫法，都涉及到語義化版本控制的問題。語義化版本控制是用一組簡單的規則及條件來約束版本號的配置和增長。這些規則是根據（但不侷限於）已經被各種封閉、開放源碼軟件所廣泛使用的慣例所設計。簡單來說，語義化版本控制遵循下面這些規則：

- 版本格式：主版本號.次版本號.修訂號，版本號遞增規則如下：

1. 主版本號：當你做了不兼容的 API 修改，
2. 次版本號：當你做了向下兼容的功能性新增，
3. 修訂號：當你做了向下兼容的問題修正。

- 先行版本號及版本編譯信息可以加到“主版本號.次版本號.修訂號”的後面，作為延伸。

關於語義化版本控制的具體細節問題，大家可以參考[這裡](http://semver.org/lang/zh-CN/)，我不再贅述。

# cargo的toml描述文件配置字段詳細參考

## [package]段落
啥也不多說了，直接上例子，大家注意我在例子中的中文解釋，個人覺得這樣比較一目瞭然：

```toml
[package]
 # 軟件包名稱，如果需要在別的地方引用此軟件包，請用此名稱。
name = "hello_world"

# 當前版本號，這裡遵循semver標準，也就是語義化版本控制標準。
version = "0.1.0"    # the current version, obeying semver

# 軟件所有作者列表
authors = ["you@example.com"]

# 非常有用的一個字段，如果要自定義自己的構建工作流，
# 尤其是要調用外部工具來構建其他本地語言（C、C++、D等）開發的軟件包時。
# 這時，自定義的構建流程可以使用rust語言，寫在"build.rs"文件中。
build = "build.rs"

# 顯式聲明軟件包文件夾內哪些文件被排除在項目的構建流程之外，
# 哪些文件包含在項目的構建流程中
exclude = ["build/**/*.o", "doc/**/*.html"]
include = ["src/**/*", "Cargo.toml"]

# 當軟件包在向公共倉庫發佈時出現錯誤時，使能此字段可以阻止此錯誤。
publish = false

# 關於軟件包的一個簡短介紹。
description = "..."

# 下面這些字段標明瞭軟件包倉庫的更多信息
documentation = "..."
homepage = "..."
repository = "..."

# 顧名思義，此字段指向的文件就是傳說中的ReadMe，
# 並且，此文件的內容最終會保存在註冊表數據庫中。
readme = "..."

# 用於分類和檢索的關鍵詞。
keywords = ["...", "..."]

# 軟件包的許可證，必須是cargo倉庫已列出的已知的標準許可證。
license = "..."

# 軟件包的非標許可證書對應的文件路徑。
license-file = "..."
```

## 依賴的詳細配置
最直接的方式在之前第五章探討過，這裡不在贅述，例如這樣：

```toml
[dependencies]
hammer = "0.5.0"
color = "> 0.6.0, < 0.8.0"
```

與平臺相關的依賴定義格式不變，不同的是需要定義在[target]字段下。例如：

```toml
# 注意，此處的cfg可以使用not、any、all等操作符任意組合鍵值對。
# 並且此用法僅支持cargo 0.9.0（rust 1.8.0）以上版本。
# 如果是windows平臺，則需要此依賴。
[target.'cfg(windows)'.dependencies]
winhttp = "0.4.0"

[target.'cfg(unix)'.dependencies]
openssl = "1.0.1"

#如果是32位平臺，則需要此依賴。
[target.'cfg(target_pointer_width = "32")'.dependencies]
native = { path = "native/i686" }

[target.'cfg(target_pointer_width = "64")'.dependencies]
native = { path = "native/i686" }

# 另一種寫法就是列出平臺的全稱描述
[target.x86_64-pc-windows-gnu.dependencies]
winhttp = "0.4.0"
[target.i686-unknown-linux-gnu.dependencies]
openssl = "1.0.1"

# 如果使用自定義平臺，請將自定義平臺文件的完整路徑用雙引號包含
[target."x86_64/windows.json".dependencies]
winhttp = "0.4.0"
[target."i686/linux.json".dependencies]
openssl = "1.0.1"
native = { path = "native/i686" }
openssl = "1.0.1"
native = { path = "native/x86_64" }

# [dev-dependencies]段落的格式等同於[dependencies]段落，
# 不同之處在於，[dependencies]段落聲明的依賴用於構建軟件包，
# 而[dev-dependencies]段落聲明的依賴僅用於構建測試和性能評估。
# 此外，[dev-dependencies]段落聲明的依賴不會傳遞給其他依賴本軟件包的項目
[dev-dependencies]
iron = "0.2"

```

## 自定義編譯器調用方式模板詳細參數
cargo內置五種編譯器調用模板，分別為dev、release、test、bench、doc，分別用於定義不同類型生成目標時的編譯器參數，如果我們自己想改變這些編譯模板，可以自己定義相應字段的值，例如（注意：下述例子中列出的值均為此模板字段對應的系統默認值）：

```toml
# 開發模板, 對應`cargo build`命令
[profile.dev]
opt-level = 0  # 控制編譯器的 --opt-level 參數，也就是優化參數
debug = true   # 控制編譯器是否開啟 `-g` 參數
rpath = false  # 控制編譯器的 `-C rpath` 參數
lto = false    # 控制`-C lto` 參數，此參數影響可執行文件和靜態庫的生成，
debug-assertions = true  # 控制調試斷言是否開啟
codegen-units = 1 # 控制編譯器的 `-C codegen-units` 參數。注意，當`lto = true`時，此字段值被忽略

# 發佈模板, 對應`cargo build --release`命令
[profile.release]
opt-level = 3
debug = false
rpath = false
lto = false
debug-assertions = false
codegen-units = 1

# 測試模板，對應`cargo test`命令
[profile.test]
opt-level = 0
debug = true
rpath = false
lto = false
debug-assertions = true
codegen-units = 1

# 性能評估模板，對應`cargo bench`命令
[profile.bench]
opt-level = 3
debug = false
rpath = false
lto = false
debug-assertions = false
codegen-units = 1

# 文檔模板，對應`cargo doc`命令
[profile.doc]
opt-level = 0
debug = true
rpath = false
lto = false
debug-assertions = true
codegen-units = 1

```

需要注意的是，當調用編譯器時，只有位於調用最頂層的軟件包的模板文件有效，其他的子軟件包或者依賴軟件包的模板定義將被頂層軟件包的模板覆蓋。

## [features]段落
[features]段落中的字段被用於條件編譯選項或者是可選依賴。例如：

```toml
[package]
name = "awesome"

[features]
# 此字段設置了可選依賴的默認選擇列表，
# 注意這裡的"session"並非一個軟件包名稱，
# 而是另一個featrue字段session
default = ["jquery", "uglifier", "session"]

# 類似這樣的值為空的feature一般用於條件編譯，
# 類似於`#[cfg(feature = "go-faster")]`。
go-faster = []

# 此feature依賴於bcrypt軟件包，
# 這樣封裝的好處是未來可以對secure-password此feature增加可選項目。
secure-password = ["bcrypt"]

# 此處的session字段導入了cookie軟件包中的feature段落中的session字段
session = ["cookie/session"]

[dependencies]
# 必要的依賴
cookie = "1.2.0"
oauth = "1.1.0"
route-recognizer = "=2.1.0"

# 可選依賴
jquery = { version = "1.0.2", optional = true }
uglifier = { version = "1.5.3", optional = true }
bcrypt = { version = "*", optional = true }
civet = { version = "*", optional = true }
```

如果其他軟件包要依賴使用上述awesome軟件包，可以在其描述文件中這樣寫：

```toml
[dependencies.awesome]
version = "1.3.5"
default-features = false # 禁用awesome 的默認features
features = ["secure-password", "civet"] # 使用此處列舉的各項features
```

使用features時需要遵循以下規則：

- feature名稱在本描述文件中不能與出現的軟件包名稱衝突
- 除了default feature，其他所有的features均是可選的
- features不能相互循環包含
- 開發依賴包不能包含在內
- features組只能依賴於可選軟件包

features的一個重要用途就是，當開發者需要對軟件包進行最終的發佈時，在進行構建時可以聲明暴露給終端用戶的features，這可以通過下述命令實現：

```
$ cargo build --release --features "shumway pdf"
```

## 關於測試
當運行cargo test命令時，cargo將會按做以下事情：

- 編譯並運行軟件包源代碼中被#[cfg(test)] 所標誌的單元測試
- 編譯並運行文檔測試
- 編譯並運行集成測試
- 編譯examples

## 配置構建目標
所有的諸如[[bin]], [lib], [[bench]], [[test]]以及 [[example]]等字段，均提供了類似的配置，以說明構建目標應該怎樣被構建。例如（下述例子中[lib]段落中各字段值均為默認值）：

```toml
[lib]
# 庫名稱，默認與項目名稱相同
name = "foo"

# 此選項僅用於[lib]段落，其決定構建目標的構建方式，
# 可以取dylib, rlib, staticlib 三種值之一，表示生成動態庫、r庫或者靜態庫。
crate-type = ["dylib"]

# path字段聲明瞭此構建目標相對於cargo.toml文件的相對路徑
path = "src/lib.rs"

# 單元測試開關選項
test = true

# 文檔測試開關選項
doctest = true

# 性能評估開關選項
bench = true

# 文檔生成開關選項
doc = true

# 是否構建為編譯器插件的開關選項
plugin = false

# 如果設置為false，`cargo test`將會忽略傳遞給rustc的--test參數。
harness = true
```
