基於 SBI 服務完成輸出和關機
=================================================================

.. toctree::
   :hidden:
   :maxdepth: 5

本節導讀
------------------------------------

本節我們將進行構建“三葉蟲”操作系統的最後一個步驟，即基於 RustSBI 提供的服務完成在屏幕上打印 ``Hello world!`` 和關機操作。事實上，作為對我們之前提到的 :ref:`應用程序執行環境 <app-software-stack>` 的細化，RustSBI 介於底層硬件和內核之間，是我們內核的底層執行環境。本節將會提到執行環境除了為上層應用進行初始化的第二種職責：即在上層應用運行時提供服務。

使用 RustSBI 提供的服務
------------------------------------------

之前我們對 RustSBI 的瞭解僅限於它會在計算機啟動時進行它所負責的環境初始化工作，並將計算機控制權移交給內核。但實際上作為內核的執行環境，它還有另一項職責：即在內核運行時響應內核的請求為內核提供服務。當內核發出請求時，計算機會轉由 RustSBI 控制來響應內核的請求，待請求處理完畢後，計算機控制權會被交還給內核。從內存佈局的角度來思考，每一層執行環境（或稱軟件棧）都對應到內存中的一段代碼和數據，這裡的控制權轉移指的是 CPU 從執行一層軟件的代碼到執行另一層軟件的代碼的過程。這個過程與我們使用高級語言編程時調用庫函數比較類似。

這裡展開介紹一些相關術語：從第二章將要講到的 :ref:`RISC-V 特權級架構 <riscv-priv-arch>` 的視角來看，我們編寫的 OS 內核位於 Supervisor 特權級，而 RustSBI 位於 Machine 特權級，也是最高的特權級。類似 RustSBI 這樣運行在 Machine 特權級的軟件被稱為 Supervisor Execution Environment(SEE)，即 Supervisor 執行環境。兩層軟件之間的接口被稱為 Supervisor Binary Interface(SBI)，即 Supervisor 二進制接口。 `SBI Specification <https://github.com/riscv-non-isa/riscv-sbi-doc>`_ （簡稱 SBI spec）規定了 SBI 接口層要包含哪些功能，該標準由 RISC-V 開源社區維護。RustSBI 按照 SBI spec 標準實現了需要支持的大多數功能，但 RustSBI 並不是 SBI 標準的唯一一種實現，除此之外還有社區中的前輩 OpenSBI 等等。

目前， SBI spec 已經發布了 v2.0-rc8 版本，但本教程基於 2023 年 3 月份發佈的 `v1.0.0 版本 <https://github.com/riscv-non-isa/riscv-sbi-doc/releases/download/v1.0.0/riscv-sbi.pdf>`_ 。我們可以來看看裡面約定了 SEE 要向 OS 內核提供哪些功能，並尋找我們本節所需的打印到屏幕和關機的接口。可以看到從 Chapter 4 開始，每一章包含了一個 SBI 拓展（Chapter 5 包含多個 Legacy Extension），代表一類功能接口，這有點像 RISC-V 指令集的 IMAFD 等拓展。每個 SBI 拓展還包含若干子功能。其中：

- Chapter 5 列出了若干 SBI 遺留接口，其中包括串口的寫入（正是我們本節所需要的）和讀取接口，分別位於 5.2 和 5.3 小節。在教程第九章我們自己實現串口外設驅動之前，與串口的交互都是通過這兩個接口來進行的。順帶一提，第三章開始還會用到 5.1 小節介紹的 set timer 接口。
- Chapter 10 包含了若干系統重啟相關的接口，我們本節所需的關機接口也在其中。

內核應該如何調用 RustSBI 提供的服務呢？通過函數調用是行不通的，因為內核並沒有和 RustSBI 鏈接到一起，我們僅僅使用 RustSBI 構建後的可執行文件，因此內核無從得知 RustSBI 中的符號或地址。幸而， RustSBI 開源社區的 `sbi_rt <https://github.com/rustsbi/sbi-rt>`_ 封裝了調用 SBI 服務的接口，我們直接使用即可。首先，我們在 ``Cargo.toml`` 中引入 sbi_rt 依賴：

.. code-block::
    :linenos:

    // os/Cargo.toml
    [dependencies]
    sbi-rt = { version = "0.0.2", features = ["legacy"] }

這裡需要帶上 ``legacy`` 的 feature，因為我們需要用到的串口讀寫接口都屬於 SBI 的遺留接口。

.. _term-llvm-sbicall:

我們將內核與 RustSBI 通信的相關功能實現在子模塊 ``sbi`` 中，因此我們需要在 ``main.rs`` 中加入 ``mod sbi`` 將該子模塊加入我們的項目。在 ``os/src/sbi.rs`` 中，我們直接調用 sbi_rt 提供的接口來將輸出字符：

.. code-block:: rust
    :linenos:

    // os/src/sbi.rs
    pub fn console_putchar(c: usize) {
        #[allow(deprecated)]
        sbi_rt::legacy::console_putchar(c);
    }

注意我們為了簡單起見並未用到 ``sbi_call`` 的返回值，有興趣的同學可以在 SBI spec 中查閱 SBI 服務返回值的含義。到這裡，同學們可以試著在 ``rust_main`` 中調用 ``console_putchar`` 來在屏幕上輸出 ``OK`` 。接著在 Qemu 上運行一下，我們便可看到由我們自己輸出的第一條 log 了。

同樣，我們再來實現關機功能：

.. code-block:: rust
    :linenos:

    // os/src/sbi.rs
    pub fn shutdown(failure: bool) -> ! {
        use sbi_rt::{system_reset, NoReason, Shutdown, SystemFailure};
        if !failure {
            system_reset(Shutdown, NoReason);
        } else {
            system_reset(Shutdown, SystemFailure);
        }
        unreachable!()
    }

這裡的參數 ``failure`` 表示系統是否正常退出，這會影響 Qemu 模擬器進程退出之後的返回值，我們則會依此判斷系統的執行是否正常。更多內容可以參閱 SBI spec 的 Chapter 10。

.. note:: **sbi_rt 是如何調用 SBI 服務的**

    SBI spec 的 Chapter 3 介紹了服務的調用方法：只需將要調用功能的拓展 ID 和功能 ID 分別放在 ``a7`` 和 ``a6`` 寄存器中，並按照 RISC-V 調用規範將參數放置在其他寄存器中，隨後執行 ``ecall`` 指令即可。這會將控制權轉交給 RustSBI 並由 RustSBI 來處理請求，處理完成後會將控制權交還給內核。返回值會被保存在 ``a0`` 和 ``a1`` 寄存器中。在本書的第二章中，我們會手動編寫彙編代碼來實現類似的過程。

實現格式化輸出
-----------------------------------------------

``console_putchar`` 的功能過於受限，如果想打印一行 ``Hello world!`` 的話需要進行多次調用。能否像本章第一節那樣使用 ``println!`` 宏一行就完成輸出呢？因此我們嘗試自己編寫基於 ``console_putchar`` 的 ``println!`` 宏。

.. code-block:: rust
    :linenos:

    // os/src/main.rs
    #[macro_use]
    mod console;

    // os/src/console.rs
    use crate::sbi::console_putchar;
    use core::fmt::{self, Write};

    struct Stdout;

    impl Write for Stdout {
        fn write_str(&mut self, s: &str) -> fmt::Result {
            for c in s.chars() {
                console_putchar(c as usize);
            }
            Ok(())
        }
    }

    pub fn print(args: fmt::Arguments) {
        Stdout.write_fmt(args).unwrap();
    }

    #[macro_export]
    macro_rules! print {
        ($fmt: literal $(, $($arg: tt)+)?) => {
            $crate::console::print(format_args!($fmt $(, $($arg)+)?));
        }
    }

    #[macro_export]
    macro_rules! println {
        ($fmt: literal $(, $($arg: tt)+)?) => {
            $crate::console::print(format_args!(concat!($fmt, "\n") $(, $($arg)+)?));
        }
    }

我們在 ``console`` 子模塊中編寫 ``println!`` 宏。結構體 ``Stdout`` 不包含任何字段，因此它被稱為類單元結構體（Unit-like structs，請參考 [#unit-like-structs]_ ）。 ``core::fmt::Write`` trait 包含一個用來實現 ``println!`` 宏很好用的 ``write_fmt`` 方法，為此我們準備為結構體 ``Stdout`` 實現 ``Write`` trait 。在 ``Write`` trait 中， ``write_str`` 方法必須實現，因此我們需要為 ``Stdout`` 實現這一方法，它並不難實現，只需遍歷傳入的 ``&str`` 中的每個字符並調用 ``console_putchar`` 就能將傳入的整個字符串打印到屏幕上。

在此之後 ``Stdout`` 便可調用 ``Write`` trait 提供的 ``write_fmt`` 方法並進而實現 ``print`` 函數。在聲明宏（Declarative macros，參考 [#declarative-macros]_ ） ``print!`` 和 ``println!`` 中會調用 ``print`` 函數完成輸出。

現在我們可以在 ``rust_main`` 中使用 ``print!`` 和 ``println!`` 宏進行格式化輸出了，如有興趣的話可以輸出 ``Hello, world!`` 試一下。

.. note::

    **Rust Tips：Rust Trait**

    在 Rust 語言中，trait（中文翻譯：特質、特徵）是一種類型，用於描述一組方法的集合。trait 可以用來定義接口（interface），並可以被其他類型實現。
    舉個例子，假設我們有一個簡單的Rust程序，其中有一個名為 Shape 的 trait，用於描述形狀：

    .. code-block:: rust
        :linenos:

        trait Shape {
            fn area(&self) -> f64;
        }


    我們可以使用這個 trait 來定義一個圓形類型：

    .. code-block:: rust
        :linenos:

        struct Circle {
            radius: f64,
        }

        impl Shape for Circle {
            fn area(&self) -> f64 {
                3.14 * self.radius * self.radius
            }
        }

    這樣，我們就可以使用 Circle 類型的實例調用 area 方法了。

    .. code-block:: rust
        :linenos:

        let c = Circle { radius: 1.0 };
        println!("Circle area: {}", c.area());  // 輸出: Circle area: 3.14    



處理致命錯誤
-----------------------------------------------

錯誤處理是編程的重要一環，它能夠保證程序的可靠性和可用性，使得程序能夠從容應對更多突發狀況而不至於過早崩潰。不同於 C 的返回錯誤編號 ``errno`` 模型和 C++/Java 的 ``try-catch`` 異常捕獲模型，Rust 將錯誤分為可恢復和不可恢復錯誤兩大類。這裡我們主要關心不可恢復錯誤。和 C++/Java 中一個異常被拋出後始終得不到處理一樣，在 Rust 中遇到不可恢復錯誤，程序會直接報錯退出。例如，使用 ``panic!`` 宏便會直接觸發一個不可恢復錯誤並使程序退出。不過在我們的內核中，目前不可恢復錯誤的處理機制還不完善：

.. code-block:: rust
    :linenos:

    // os/src/lang_items.rs
    use core::panic::PanicInfo;

    #[panic_handler]
    fn panic(_info: &PanicInfo) -> ! {
        loop {}
    }

可以看到，在目前的實現中，當遇到不可恢復錯誤的時候，被標記為語義項 ``#[panic_handler]`` 的 ``panic`` 函數將會被調用，然而其中只是一個死循環，會使得計算機卡在這裡。藉助前面實現的 ``println!`` 宏和 ``shutdown`` 函數，我們可以在 ``panic`` 函數中打印錯誤信息並關機：

.. code-block:: rust
    :linenos:

    // os/src/main.rs
    #![feature(panic_info_message)]

    // os/src/lang_item.rs
    use crate::sbi::shutdown;
    use core::panic::PanicInfo;

    #[panic_handler]
    fn panic(info: &PanicInfo) -> ! {
        if let Some(location) = info.location() {
            println!(
                "Panicked at {}:{} {}",
                location.file(),
                location.line(),
                info.message().unwrap()
            );
        } else {
            println!("Panicked: {}", info.message().unwrap());
        }
        shutdown(true)
    }

我們嘗試打印更加詳細的信息，包括 panic 所在的源文件和代碼行數。我們嘗試從傳入的 ``PanicInfo`` 中解析這些信息，如果解析成功的話，就和 panic 的報錯信息一起打印出來。我們需要在 ``main.rs`` 開頭加上 ``#![feature(panic_info_message)]`` 才能通過 ``PanicInfo::message`` 獲取報錯信息。當打印完畢之後，我們直接調用 ``shutdown`` 函數關機，由於系統是異常 panic 關機的，參數 ``failure`` 應為 ``true`` 。

為了測試我們的實現是否正確，我們將 ``rust_main`` 改為：

.. code-block:: rust
    :linenos:

    // os/src/main.rs
    #[no_mangle]
    pub fn rust_main() -> ! {
        clear_bss();
        println!("Hello, world!");
        panic!("Shutdown machine!");
    }

使用 Qemu 運行我們的內核，運行結果為：

.. code-block::

    [RustSBI output]
    Hello, world!
    Panicked at src/main.rs:26 Shutdown machine!

可以看到，panic 所在的源文件和代碼行數被正確報告，這將為我們後續章節的開發和調試帶來很大方便。到這裡，我們就實現了一個可以在Qemu模擬的計算機上運行的裸機應用程序，其具體內容就是上述的 `rust_main` 函數，而其他部分，如 `entry.asm` 、 `lang_items.rs` 、`console.rs` 、 `sbi.rs` 則形成了支持裸機應用程序的寒武紀“三葉蟲”操作系統 -- LibOS 。

.. note::

    **Rust Tips：Rust 可恢復錯誤**

    在有可能出現錯誤時，Rust 函數的返回值可以屬於一種特殊的類型，該類型可以涵蓋兩種情況：要麼函數正常退出，則函數返回正常的返回值；要麼函數執行過程中出錯，則函數返回出錯的類型。Rust 的類型系統保證這種返回值不會在程序員無意識的情況下被濫用，即程序員必須顯式對其進行分支判斷或者強制排除出錯的情況。如果不進行任何處理，那麼無法從中得到有意義的結果供後續使用或是無法通過編譯。這樣，就杜絕了很大一部分因程序員的疏忽產生的錯誤（如不加判斷地使用某函數返回的空指針）。

    在 Rust 中有兩種這樣的特殊類型，它們都屬於枚舉結構：

    - ``Option<T>`` 既可以有值 ``Option::Some<T>`` ，也有可能沒有值 ``Option::None``；
    - ``Result<T, E>`` 既可以保存某個操作的返回值 ``Result::Ok<T>`` ，也可以表明操作過程中出現了錯誤 ``Result::Err<E>`` 。

    我們可以使用 ``Option/Result`` 來保存一個不能確定存在/不存在或是成功/失敗的值。之後可以通過匹配 ``if let`` 或是在能夠確定
    的場合直接通過 ``unwrap`` 將裡面的值取出。詳細的內容可以參考 Rust 官方文檔 [#recoverable-errors]_ 。


.. [#unit-like-structs] https://doc.rust-lang.org/book/ch05-01-defining-structs.html#unit-like-structs-without-any-fields
.. [#declarative-macros] https://doc.rust-lang.org/book/ch19-06-macros.html#declarative-macros-with-macro_rules-for-general-metaprogramming
.. [#recoverable-errors] https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html