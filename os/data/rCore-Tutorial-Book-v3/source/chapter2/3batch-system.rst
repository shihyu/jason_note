
.. _term-batchos:

實現批處理操作系統
==============================

.. toctree::
   :hidden:
   :maxdepth: 5

本節導讀
-------------------------------

.. 目前本章主要介紹的批處理操作系統--泥盆紀“鄧式魚”操作系統。雖然操作系統實現了批處理執行應用程序的功能，但應用程序和操作系統還是緊耦合在一個單一的執行文件中，還缺少一種類似文件系統那樣的松耦合靈活放置應用程序和加載執行應用程序的機制。這就需要在單一執行文件的情況下，設計一種儘量簡潔的程序放置和加載方式，能夠在批處理操作系統與應用程序之間建立起聯繫的紐帶。這主要包括兩個方面：

從本節開始我們將著手實現批處理操作系統——即泥盆紀“鄧式魚”操作系統。在批處理操作系統中，每當一個應用執行完畢，我們都需要將下一個要執行的應用的代碼和數據加載到內存。在具體實現其批處理執行應用程序功能之前，本節我們首先實現該應用加載機制，也即：在操作系統和應用程序需要被放置到同一個可執行文件的前提下，設計一種儘量簡潔的應用放置和加載方式，使得操作系統容易找到應用被放置到的位置，從而在批處理操作系統和應用程序之間建立起聯繫的紐帶。具體而言，應用放置採用“靜態綁定”的方式，而操作系統加載應用則採用“動態加載”的方式：

- 靜態綁定：通過一定的編程技巧，把多個應用程序代碼和批處理操作系統代碼“綁定”在一起。
- 動態加載：基於靜態編碼留下的“綁定”信息，操作系統可以找到每個應用程序文件二進制代碼的起始地址和長度，並能加載到內存中運行。

這裡與硬件相關且比較困難的地方是如何讓在內核態的批處理操作系統啟動應用程序，且能讓應用程序在用戶態正常執行。本節會講大致過程，而具體細節將放到下一節具體講解。

將應用程序鏈接到內核
--------------------------------------------

在本章中，我們把應用程序的二進制鏡像文件（從 ELF 格式可執行文件剝離元數據，參考 :ref:`前面章節 <content-binary-from-elf>` ）作為內核的數據段鏈接到內核裡面，因此內核需要知道內含的應用程序的數量和它們的位置，這樣才能夠在運行時對它們進行管理並能夠加載到物理內存。

.. 前面章節講過了

    應用程序的二進制鏡像文件是指對編譯器生成的執行文件進行進一步處理（一般用 ``objcopy`` 工具），去掉ELF文件管理信息後的代碼段和數據段的內容。
    比如：

    .. code-block:: shell

        $ gcc -o hello.exe hell.c
        $ objcopy -O binary hello.exe hello.bin
    

在 ``os/src/main.rs`` 中能夠找到這樣一行：

.. code-block:: rust

    global_asm!(include_str!("link_app.S"));

這裡我們引入了一段彙編代碼 ``link_app.S`` ，它一開始並不存在，而是在構建操作系統時自動生成的。當我們使用 ``make run`` 讓系統運行的過程中，這個彙編代碼 ``link_app.S`` 就生成了。我們可以先來看一看 ``link_app.S`` 裡面的內容：

.. code-block:: asm
    :linenos:
    
    # os/src/link_app.S

        .align 3
        .section .data
        .global _num_app
    _num_app:
        .quad 5
        .quad app_0_start
        .quad app_1_start
        .quad app_2_start
        .quad app_3_start
        .quad app_4_start
        .quad app_4_end

        .section .data
        .global app_0_start
        .global app_0_end
    app_0_start:
        .incbin "../user/target/riscv64gc-unknown-none-elf/release/00hello_world.bin"
    app_0_end:

        .section .data
        .global app_1_start
        .global app_1_end
    app_1_start:
        .incbin "../user/target/riscv64gc-unknown-none-elf/release/01store_fault.bin"
    app_1_end:

        .section .data
        .global app_2_start
        .global app_2_end
    app_2_start:
        .incbin "../user/target/riscv64gc-unknown-none-elf/release/02power.bin"
    app_2_end:

        .section .data
        .global app_3_start
        .global app_3_end
    app_3_start:
        .incbin "../user/target/riscv64gc-unknown-none-elf/release/03priv_inst.bin"
    app_3_end:

        .section .data
        .global app_4_start
        .global app_4_end
    app_4_start:
        .incbin "../user/target/riscv64gc-unknown-none-elf/release/04priv_csr.bin"
    app_4_end:

可以看到第 15 行開始的五個數據段分別插入了五個應用程序的二進制鏡像，並且各自有一對全局符號 ``app_*_start, app_*_end`` 指示它們的開始和結束位置。而第 3 行開始的另一個數據段相當於一個 64 位整數數組。數組中的第一個元素表示應用程序的數量，後面則按照順序放置每個應用程序的起始地址，最後一個元素放置最後一個應用程序的結束位置。這樣每個應用程序的位置都能從該數組中相鄰兩個元素中得知。這個數組所在的位置同樣也由全局符號 ``_num_app`` 所指示。

這個文件是在 ``cargo build`` 的時候，由腳本 ``os/build.rs`` 控制生成的。有興趣的同學可以參考其代碼。

找到並加載應用程序二進制碼
-----------------------------------------------

能夠找到並加載應用程序二進制碼的應用管理器 ``AppManager`` 是“鄧式魚”操作系統的核心組件。我們在 ``os`` 的 ``batch`` 子模塊中實現一個應用管理器，它的主要功能是：

- 保存應用數量和各自的位置信息，以及當前執行到第幾個應用了。
- 根據應用程序位置信息，初始化好應用所需內存空間，並加載應用執行。

應用管理器 ``AppManager`` 結構體定義如下：

.. code-block:: rust
    
    // os/src/batch.rs

    struct AppManager {
        num_app: usize,
        current_app: usize,
        app_start: [usize; MAX_APP_NUM + 1],
    }


這裡我們可以看出，上面提到的應用管理器需要保存和維護的信息都在 ``AppManager`` 裡面。這樣設計的原因在於：我們希望將 ``AppManager`` 實例化為一個全局變量，使得任何函數都可以直接訪問。但是裡面的 ``current_app`` 字段表示當前執行的是第幾個應用，它是一個可修改的變量，會在系統運行期間發生變化。因此在聲明全局變量的時候，採用 ``static mut`` 是一種比較簡單自然的方法。但是在 Rust 中，任何對於 ``static mut`` 變量的訪問控制都是 unsafe 的，而我們要在編程中儘量避免使用 unsafe ，這樣才能讓編譯器負責更多的安全性檢查。因此，我們需要考慮如何在儘量避免觸及 unsafe 的情況下仍能聲明並使用可變的全局變量。 

.. _rust-ownership-model:

.. note::

    **Rust Tips：Rust 所有權模型和借用檢查**

    我們這裡簡單介紹一下 Rust 的所有權模型。它可以用一句話來概括： **值** （Value）在同一時間只能被綁定到一個 **變量** （Variable）上。這裡，“值”指的是儲存在內存中固定位置，且格式屬於某種特定類型的數據；而變量就是我們在 Rust 代碼中通過 ``let`` 聲明的局部變量或者函數的參數等，變量的類型與值的類型相匹配。在這種情況下，我們稱值的 **所有權** （Ownership）屬於它被綁定到的變量，且變量可以作為訪問/控制綁定到它上面的值的一個媒介。變量可以將它擁有的值的所有權轉移給其他變量，或者當變量退出其作用域之後，它擁有的值也會被銷燬，這意味著值佔用的內存或其他資源會被回收。

    有些場景下，特別是在函數調用的時候，我們並不希望將當前上下文中的值的所有權轉移到其他上下文中，因此類似於 C/C++ 中的按引用傳參， Rust 可以使用 ``&`` 或 ``&mut`` 後面加上值被綁定到的變量的名字來分別生成值的不可變引用和可變引用，我們稱這些引用分別不可變/可變 **借用** (Borrow) 它們引用的值。顧名思義，我們可以通過可變引用來修改它借用的值，但通過不可變引用則只能讀取而不能修改。這些引用同樣是需要被綁定到變量上的值，只是它們的類型是引用類型。在 Rust 中，引用類型的使用需要被編譯器檢查，但在數據表達上，和 C 的指針一樣它只記錄它借用的值所在的地址，因此在內存中它隨平臺不同僅會佔據 4 字節或 8 字節空間。
    
    無論值的類型是否是引用類型，我們都定義值的 **生存期** （Lifetime）為代碼執行期間該值必須持續合法的代碼區域集合（見 [#rust-nomicon-lifetime]_ ），大概可以理解為該值在代碼中的哪些地方被用到了：簡單情況下，它可能等同於擁有它的變量的作用域，也有可能是從它被綁定開始直到它的擁有者變量最後一次出現或是它被解綁。
    
    當我們使用 ``&`` 和 ``&mut`` 來借用值的時候，則我們編寫的代碼必須滿足某些約束條件，不然無法通過編譯：

    - 不可變/可變引用的生存期不能 **超出** （Outlive）它們借用的值的生存期，也即：前者必須是後者的子集；
    - 同一時間，借用同一個值的不可變和可變引用不能共存；
    - 同一時間，借用同一個值的不可變引用可以存在多個，但可變引用只能存在一個。

    這是為了 Rust 內存安全而設計的重要約束條件。第一條很好理解，如果值的生存期未能完全覆蓋借用它的引用的生存期，就會在某一時刻發生值已被銷燬而我們仍然嘗試通過引用來訪問該值的情形。反過來說，顯然當值合法時引用才有意義。最典型的例子是 **懸垂指針** （Dangling Pointer）問題：即我們嘗試在一個函數中返回函數中聲明的局部變量的引用，並在調用者函數中試圖通過該引用訪問已被銷燬的局部變量，這會產生未定義行為並導致錯誤。第二、三條的主要目的則是為了避免通過多個引用對同一個值進行的讀寫操作產生衝突。例如，當對同一個值的讀操作和寫操作在時間上相互交錯時（即不可變/可變引用的生存期部分重疊），讀操作便有可能讀到被修改到一半的值，通常這會是一個不合法的值從而導致程序無法正確運行。這可能是由於我們在編程上的疏忽，使得我們在讀取一個值的時候忘記它目前正處在被修改到一半的狀態，一個可能的例子是在 C++ 中正對容器進行迭代訪問的時候修改了容器本身。也有可能被歸結為 **別名** （Aliasing）問題，例如在 C 函數中有兩個指針參數，如果它們指向相同的地址且編譯器沒有注意到這一點就進行過激的優化，將會使得編譯結果偏離我們期望的語義。
    
    上述約束條件要求借用同一個值的不可變引用和不可變/可變引用的生存期相互隔離，從而能夠解決這些問題。Rust 編譯器會在編譯時使用 **借用檢查器** （Borrow Checker）檢查這些約束條件是否被滿足：其具體做法是儘可能精確的估計引用和值的生存期並將它們進行比較。隨著 Rust 語言的愈發完善，其估計的精確度也會越來越高，使得程序員能夠更容易通過借用檢查。引用相關的借用檢查發生在編譯期，因此我們可以稱其為編譯期借用檢查。

    相對的，對值的借用方式運行時可變的情況下，我們可以使用 Rust 內置的數據結構將借用檢查推遲到運行時，這可以稱為運行時借用檢查，它的約束條件和編譯期借用檢查一致。當我們想要發起借用或終止借用時，只需調用對應數據結構提供的接口即可。值的借用狀態會佔用一部分額外內存，運行時還會有額外的代碼對借用合法性進行檢查，這是為滿足借用方式的靈活性產生的必要開銷。當無法通過借用檢查時，將會產生一個不可恢復錯誤，導致程序打印錯誤信息並立即退出。具體來說，我們通常使用 ``RefCell`` 包裹可被借用的值，隨後調用 ``borrow`` 和 ``borrow_mut`` 便可發起借用並獲得一個對值的不可變/可變借用的標誌，它們可以像引用一樣使用。為了終止借用，我們只需手動銷燬這些標誌或者等待它們被自動銷燬。 ``RefCell`` 的詳細用法請參考 [#rust-refcell]_ 。

.. _term-interior-mutability:

如果單獨使用 ``static`` 而去掉 ``mut`` 的話，我們可以聲明一個初始化之後就不可變的全局變量，但是我們需要 ``AppManager`` 裡面的內容在運行時發生變化。這涉及到 Rust 中的 **內部可變性** （Interior Mutability），也即在變量自身不可變或僅在不可變借用的情況下仍能修改綁定到變量上的值。我們可以通過用上面提到的 ``RefCell`` 來包裹 ``AppManager`` ，這樣 ``RefCell`` 無需被聲明為 ``mut`` ，同時被包裹的 ``AppManager`` 也能被修改。但是，我們能否將 ``RefCell`` 聲明為一個全局變量呢？讓我們寫一小段代碼試一試：

.. code-block:: rust

    // https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=18b0f956b83e6a8a408215edcfcb6d01
    use std::cell::RefCell;
    static A: RefCell<i32> = RefCell::new(3);
    fn main() {
        *A.borrow_mut() = 4;
        println!("{}", A.borrow());
    }

這段代碼無法通過編譯，其錯誤是：

.. code-block::

    error[E0277]: `RefCell<i32>` cannot be shared between threads safely
    --> src/main.rs:2:1
    |
    2 | static A: RefCell<i32> = RefCell::new(3);
    | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ `RefCell<i32>` cannot be shared between threads safely
    |
    = help: the trait `Sync` is not implemented for `RefCell<i32>`
    = note: shared static variables must have a type that implements `Sync`

    For more information about this error, try `rustc --explain E0277`.

Rust 編譯器提示我們 ``RefCell<i32>`` 未被標記為 ``Sync`` ，因此 Rust 編譯器認為它不能被安全的在線程間共享，也就不能作為全局變量使用。這可能會令人迷惑，這只是一個單線程程序，因此它不會有任何線程間共享數據的行為，為什麼不能通過編譯呢？事實上，Rust 對於併發安全的檢查較為粗糙，當聲明一個全局變量的時候，編譯器會默認程序員會在多線程上使用它，而並不會檢查程序員是否真的這樣做。如果一個變量實際上僅會在單線程上使用，那 Rust 會期待我們將變量分配在棧上作為局部變量而不是全局變量。目前我們的內核僅支持單核，也就意味著只有單線程，那麼我們可不可以使用局部變量來繞過這個錯誤呢？

很可惜，在這裡和後面章節的很多場景中，有些變量無法作為局部變量使用。這是因為後面內核會併發執行多條控制流，這些控制流都會用到這些變量。如果我們最初將變量分配在某條控制流的棧上，那麼我們就需要考慮如何將變量傳遞到其他控制流上，由於控制流的切換等操作並非常規的函數調用，我們很難將變量傳遞出去。因此最方便的做法是使用全局變量，這意味著在程序的任何地方均可隨意訪問它們，自然也包括這些控制流。

除了 ``Sync`` 的問題之外，看起來 ``RefCell`` 已經非常接近我們的需求了，因此我們在 ``RefCell`` 的基礎上再封裝一個 ``UPSafeCell`` ，它名字的含義是：允許我們在 *單核* 上安全使用可變全局變量。

.. code-block:: rust
    
    // os/src/sync/up.rs

    pub struct UPSafeCell<T> {
        /// inner data
        inner: RefCell<T>,
    }

    unsafe impl<T> Sync for UPSafeCell<T> {}

    impl<T> UPSafeCell<T> {
        /// User is responsible to guarantee that inner struct is only used in
        /// uniprocessor.
        pub unsafe fn new(value: T) -> Self {
            Self { inner: RefCell::new(value) }
        }
        /// Panic if the data has been borrowed.
        pub fn exclusive_access(&self) -> RefMut<'_, T> {
            self.inner.borrow_mut()
        }
    }

``UPSafeCell`` 對於 ``RefCell`` 簡單進行封裝，它和 ``RefCell`` 一樣提供內部可變性和運行時借用檢查，只是更加嚴格：調用 ``exclusive_access`` 可以得到它包裹的數據的獨佔訪問權。因此當我們要訪問數據時（無論讀還是寫），需要首先調用 ``exclusive_access`` 獲得數據的可變借用標記，通過它可以完成數據的讀寫，在操作完成之後我們需要銷燬這個標記，此後才能開始對該數據的下一次訪問。相比 ``RefCell`` 它不再允許多個讀操作同時存在。

這段代碼裡面出現了兩個 ``unsafe`` ：

- 首先 ``new`` 被聲明為一個 ``unsafe`` 函數，是因為我們希望使用者在創建一個 ``UPSafeCell`` 的時候保證在訪問 ``UPSafeCell`` 內包裹的數據的時候始終不違背上述模式：即訪問之前調用 ``exclusive_access`` ，訪問之後銷燬借用標記再進行下一次訪問。這隻能依靠使用者自己來保證，但我們提供了一個保底措施：當使用者違背了上述模式，比如訪問之後忘記銷燬就開啟下一次訪問時，程序會 panic 並退出。
- 另一方面，我們將 ``UPSafeCell`` 標記為 ``Sync`` 使得它可以作為一個全局變量。這是 unsafe 行為，因為編譯器無法確定我們的 ``UPSafeCell`` 能否安全的在多線程間共享。而我們能夠向編譯器做出保證，第一個原因是目前我們內核僅運行在單核上，因此無需在意任何多核引發的數據競爭/同步問題；第二個原因則是它基於 ``RefCell`` 提供了運行時借用檢查功能，從而滿足了 Rust 對於借用的基本約束進而保證了內存安全。

.. chyyuu  這裡還是要提提為何sync吧？

.. chyyuu     **為什麼對於 static mut 的訪問是 unsafe 的**     **為什麼要將 AppManager 標記為 Sync**     可以參考附錄A：Rust 快速入門的併發章節。

.. 為了解決上述矛盾，我們設計實現了 ``UPSafeCell<T>`` ，通過封裝 ``RefCell<T>`` 來提供 **內部可變性** (Interior Mutability)，所謂的內部可變性就是指在我們只能拿到 ``<T>`` 類型變量的不可變借用的情況下（即同樣也只能拿到其中的字段 ``current_app`` 的不可變借用），依然可以通過 ``RefCell`` 來修改 ``AppManager`` 裡面的字段。使用 ``RefCell::borrow_mut`` 可以拿到 ``RefCell`` 裡面內容的可變借用， ``RefCell`` 會在運行時維護當前它管理的對象的已有借用狀態，並在訪問對象時進行運行時借用檢查。所以 ``RefCell::borrow_mut`` 就是我們實現內部可變性的關鍵。此外，為了讓 ``AppManager`` 能被直接全局實例化，我們需要將其通過 ``UPSafeCell<T>`` 標記為 ``Sync`` 。 ``UPSafeCell<T>`` 的實現如下所示：

這樣，我們就以儘量少的 unsafe code 來初始化 ``AppManager`` 的全局實例 ``APP_MANAGER`` ：

.. code-block:: rust

    // os/src/batch.rs

    lazy_static! {
        static ref APP_MANAGER: UPSafeCell<AppManager> = unsafe { UPSafeCell::new({
            extern "C" { fn _num_app(); }
            let num_app_ptr = _num_app as usize as *const usize;
            let num_app = num_app_ptr.read_volatile();
            let mut app_start: [usize; MAX_APP_NUM + 1] = [0; MAX_APP_NUM + 1];
            let app_start_raw: &[usize] =  core::slice::from_raw_parts(
                num_app_ptr.add(1), num_app + 1
            );
            app_start[..=num_app].copy_from_slice(app_start_raw);
            AppManager {
                num_app,
                current_app: 0,
                app_start,
            }
        })};
    }

初始化的邏輯很簡單，就是找到 ``link_app.S`` 中提供的符號 ``_num_app`` ，並從這裡開始解析出應用數量以及各個應用的起始地址。注意其中對於切片類型的使用能夠很大程度上簡化編程。

這裡我們使用了外部庫 ``lazy_static`` 提供的 ``lazy_static!`` 宏。要引入這個外部庫，我們需要加入依賴：

.. code-block:: toml

    # os/Cargo.toml

    [dependencies]
    lazy_static = { version = "1.4.0", features = ["spin_no_std"] }

``lazy_static!`` 宏提供了全局變量的運行時初始化功能。一般情況下，全局變量必須在編譯期設置一個初始值，但是有些全局變量依賴於運行期間才能得到的數據作為初始值。這導致這些全局變量需要在運行時發生變化，即需要重新設置初始值之後才能使用。如果我們手動實現的話有諸多不便之處，比如需要把這種全局變量聲明為 ``static mut`` 並衍生出很多 unsafe 代碼 。這種情況下我們可以使用 ``lazy_static!`` 宏來幫助我們解決這個問題。這裡我們藉助 ``lazy_static!`` 聲明瞭一個 ``AppManager`` 結構的名為 ``APP_MANAGER`` 的全局實例，且只有在它第一次被使用到的時候，才會進行實際的初始化工作。

因此，藉助我們設計的 ``UPSafeCell<T>`` 和外部庫 ``lazy_static!``，我們就能使用盡量少的 unsafe 代碼完成可變全局變量的聲明和初始化，且一旦初始化完成，在後續的使用過程中便不再觸及 unsafe 代碼。

``AppManager`` 的方法中， ``print_app_info/get_current_app/move_to_next_app`` 都相當簡單直接，需要說明的是 ``load_app``：

.. code-block:: rust
    :linenos:

    unsafe fn load_app(&self, app_id: usize) {
        if app_id >= self.num_app {
            panic!("All applications completed!");
        }
        println!("[kernel] Loading app_{}", app_id);
        // clear app area
        core::slice::from_raw_parts_mut(
            APP_BASE_ADDRESS as *mut u8,
            APP_SIZE_LIMIT
        ).fill(0);
        let app_src = core::slice::from_raw_parts(
            self.app_start[app_id] as *const u8,
            self.app_start[app_id + 1] - self.app_start[app_id]
        );
        let app_dst = core::slice::from_raw_parts_mut(
            APP_BASE_ADDRESS as *mut u8,
            app_src.len()
        );
        app_dst.copy_from_slice(app_src);
        // memory fence about fetching the instruction memory
        asm!("fence.i");
    }


這個方法負責將參數 ``app_id`` 對應的應用程序的二進制鏡像加載到物理內存以 ``0x80400000`` 起始的位置，這個位置是批處理操作系統和應用程序之間約定的常數地址，回憶上一小節中，我們也調整應用程序的內存佈局以同一個地址開頭。第 7 行開始，我們首先將一塊內存清空，然後找到待加載應用二進制鏡像的位置，並將它複製到正確的位置。它本質上是把數據從一塊內存複製到另一塊內存，從批處理操作系統的角度來看，是將操作系統數據段的一部分數據（實際上是應用程序）複製到了一個可以執行代碼的內存區域。在這一點上也體現了馮諾依曼計算機的 *代碼即數據* 的特徵。

.. _term-dcache:
.. _term-icache:

注意在第 21 行我們在加載完應用代碼之後插入了一條奇怪的彙編指令 ``fence.i`` ，它起到什麼作用呢？我們知道緩存是存儲層級結構中提高訪存速度的很重要一環。而 CPU 對物理內存所做的緩存又分成 **數據緩存** (d-cache) 和 **指令緩存** (i-cache) 兩部分，分別在 CPU 訪存和取指的時候使用。在取指的時候，對於一個指令地址， CPU 會先去 i-cache 裡面看一下它是否在某個已緩存的緩存行內，如果在的話它就會直接從高速緩存中拿到指令而不是通過總線訪問內存。通常情況下， CPU 會認為程序的代碼段不會發生變化，因此 i-cache 是一種只讀緩存。但在這裡，OS 將修改會被 CPU 取指的內存區域，這會使得 i-cache 中含有與內存中不一致的內容。因此， OS 在這裡必須使用取指屏障指令 ``fence.i`` ，它的功能是保證 **在它之後的取指過程必須能夠看到在它之前的所有對於取指內存區域的修改** ，這樣才能保證 CPU 訪問的應用代碼是最新的而不是 i-cache 中過時的內容。至於硬件是如何實現 ``fence.i`` 這條指令的，這一點每個硬件的具體實現方式都可能不同，比如直接清空 i-cache 中所有內容或者標記其中某些內容不合法等等。

.. warning:: 

   **模擬器與真機的不同之處**

   至少在 Qemu 模擬器的默認配置下，各類緩存如 i-cache/d-cache/TLB 都處於機制不完全甚至完全不存在的狀態。目前在 Qemu 平臺上，即使我們不加上刷新 i-cache 的指令，大概率也是能夠正常運行的。但在 K210 物理計算機上，如果沒有執行彙編指令 ``fence.i`` ，就會產生由於指令緩存的內容與對應內存中指令不一致導致的錯誤異常。

``batch`` 子模塊對外暴露出如下接口：

- ``init`` ：調用 ``print_app_info`` 的時候第一次用到了全局變量 ``APP_MANAGER`` ，它也是在這個時候完成初始化；
- ``run_next_app`` ：批處理操作系統的核心操作，即加載並運行下一個應用程序。當批處理操作系統完成初始化或者一個應用程序運行結束或出錯之後會調用該函數。我們下節再介紹其具體實現。

.. [#rust-nomicon-lifetime] https://doc.rust-lang.org/nomicon/lifetimes.html
.. [#rust-refcell] https://doc.rust-lang.org/stable/std/cell/struct.RefCell.html
