內核態的線程管理
=========================================

本節導讀
-----------------------------------------

在上一節介紹瞭如何在用戶態實現對多線程的管理，讓同學對多線程的實際運行機制：創建線程、切換線程等有了一個比較全面的認識。由於在用戶態進行線程管理，帶了的一個潛在不足是沒法讓線程管理運行時直接切換線程，只能等當前運行的線程主動讓出處理器使用權後，線程管理運行時才能切換檢查。而我們的操作系統運行在處理器內核態，如果擴展一下對線程的管理，那就可以基於時鐘中斷來直接打斷當前用戶態線程的運行，實現對線程的調度和切換等。

本節參考上一節的用戶態線程管理機制，結合之前的操作系統實現：具有UNIX操作系統基本功能的 “迅猛龍” 操作系統，進化為更加迅捷的 “達科塔盜龍” [#dak]_ 操作系統，我們首先分析如何擴展現有的進程，以支持線程管理。然後設計線程的總體結構、管理線程執行的線程控制塊數據結構、以及對線程管理相關的重要函數：線程創建和線程切換。並最終合併到現有的進程管理機制中。本節的內容能幫助我們理解進程和線程的關係，二者在設計思想與具體實現上的差異，為後續支持各種併發機制打下基礎。


.. note::

   **為何要在這裡才引入線程**

   學生對進程有一定了解後，再來理解線程也會更加容易。因為從對程序執行的控制流進行調度和切換上看，本章講解的線程調度與切換操作是之前講解的進程調度與切換的一個子集。另外，在這裡引入線程的一個重要原因是為了便於引入併發。沒在進程階段引入併發這個專題的原因是，進程主要的目的是隔離，而線程的引入強調了共享，即屬於同一進程的多個線程可共享進程的資源，這樣就必須要解決同步問題了。


線程概念
---------------------------------------------

這裡會結合與進程的比較來說明線程的概念。到本章之前，我們看到了進程這一抽象，操作系統讓進程擁有相互隔離的虛擬的地址空間，讓進程感到在獨佔一個虛擬的處理器。其實這只是操作系統通過時分複用和空分複用技術來讓每個進程複用有限的物理內存和物理CPU。而線程是在進程內的一個新的抽象。在沒有線程之前，一個進程在一個時刻只有一個執行點（即程序計數器 PC 寄存器保存的要執行指令的指針以及棧的位置）。線程的引入把進程內的這個單一執行點給擴展為多個執行點，即在進程中存在多個線程，每個線程都有一個執行點。而且這些線程共享進程的地址空間，所以可以不必採用相對比較複雜的進程間通信機制（一般需要內核的介入）也可以很方便地直接訪問進程內的數據進行協作。

在線程的具體運行過程中，需要有程序計數器寄存器來記錄當前的執行位置，需要有一組通用寄存器記錄當前的指令的操作數據，需要有一個棧作為線程執行過程的函數調用棧保存局部變量等內容，這就形成了線程上下文的主體部分。這樣如果兩個線程運行在一個處理器上，就需要採用類似兩個進程運行在一個處理器上的調度/切換管理機制，即需要在一定時刻進行線程切換，並進行線程上下文的保存與恢復。這樣在一個進程中的多線程可以獨立運行，取代了進程，成為操作系統調度的基本單位。

由於把進程的結構進行了細化，通過線程來表示對處理器的虛擬化，使得進程成為了管理線程的容器。在進程中的線程沒有父子關係，大家都是兄弟，但還是有個老大。這個代表老大的線程其實就是創建進程（比如通過 ``fork`` 系統調用創建進程）時建立的第一個線程，我們稱之為主線程。類似於進程標識符（PID），每個線程都有一個在所屬進程內生效的線程標識符（TID），同進程下的兩個線程有著不同的 TID ，可以用來區分它們。主線程由於最先被創建，它的 TID 固定為 ``0`` 。


.. chyyuu 需要有一個thread的結構圖


通用操作系統多線程應用程序示例
-----------------------------------------------------

當創建一個進程的時候，如果是基於 ``fork`` 系統調用的話，子進程會和父進程一樣從系統調用返回後的下一條指令開始執行；如果是基於 ``exec`` 系統調用的話，子進程則會從新加載程序的入口點開始執行。而對於線程的話，除了主線程仍然從程序入口點（一般是 ``main`` 函數）開始執行之外，每個線程的生命週期都與程序中的一個函數的一次執行綁定。也就是說，線程從該函數入口點開始執行，當函數返回之後，線程也隨之退出。因此，在創建線程的時候我們需要提供程序中的一個函數讓線程來執行這個函數。

我們用 C 語言中的線程 API 來舉例說明。在 C 語言中，常用的線程接口為 pthread 系列 API，這裡的 pthread 意為 POSIX thread 即 POSIX 線程。這組 API 被很多不同的內核實現所支持，基於它實現的應用很容易在不同的平臺間移植。pthread 創建線程的接口 ``pthread_create`` 如下：

.. code-block:: c

    #include <pthread.h>

    int pthread_create(pthread_t *restrict thread,
                      const pthread_attr_t *restrict attr,
                      void *(*start_routine)(void *),
                      void *restrict arg);

其中：

- 第一個參數為一個類型為 ``pthread_t`` 的線程結構體的指針。在實際創建線程之前我們首先要創建並初始化一個 ``pthread_t`` 的實例，它與線程一一對應，線程相關的操作都要通過它來進行。
- 通過第二個參數我們可以對要創建的線程進行一些配置，比如內核應該分配給這個線程多少棧空間。簡單起見我們這裡不展開。
- 第三個參數為一個函數指針，表示創建的線程要執行哪個函數。觀察函數簽名可以知道該函數的參數和返回值類型均被要求為一個 ``void *`` ，這樣是為了兼容各種不同的線程函數，因為 ``void *`` 可以和各種類型的指針相互轉換。在聲明函數的時候要遵循這個約定，但實現的時候我們常常需要首先將 ``void *`` 轉化為具體類型的指針。
- 第四個參數為傳給線程執行的函數的參數，類型為 ``void *`` ，和函數簽名中的約定一致。需要這個參數的原因是：方便區分，我們常常會讓很多線程執行同一個函數，但可以傳給它們不同的參數，以這種手段來對它們進行區分。

讓我們來看一個例子：

.. code-block:: c
    :linenos:

    #include <stdio.h>
    #include <pthread.h>

    typedef struct {
            int x;
            int y;
    } FuncArguments;

    void *func(void *arg) {
            FuncArguments *args = (FuncArguments*)arg;
            printf("x=%d,y=%d\n", args->x, args->y);
    }

    void main() {
            pthread_t t0, t1, t2;
            FuncArguments args[3] = {{1, 2}, {3, 4}, {5, 6}};
            pthread_create(&t0, NULL, func, &args[0]);
            pthread_create(&t1, NULL, func, &args[1]);
            pthread_create(&t2, NULL, func, &args[2]);
            pthread_join(t0, NULL);
            pthread_join(t1, NULL);
            pthread_join(t2, NULL);
            return;
    }

- 第 4~7 行我們聲明線程函數接受的參數類型為一個名為 ``FuncArguments`` 的結構體，內含 ``x`` 和 ``y`` 兩個字段。
- 第 15 行我們創建並默認初始化三個 ``pthread_t`` 實例 ``t0`` 、 ``t1`` 和 ``t2`` ，分別代表我們接下來要創建的三個線程。
- 第 16 行在主線程的棧上給出三個線程接受的參數。
- 第 9~12 行實現線程運行的函數 ``func`` ，可以看到它的函數簽名符合要求。它實際接受的參數類型應該為我們之前定義的 ``FuncArguments`` 類型的指針，但是在函數簽名中是一個 ``void *`` ，所以在第 10 行我們首先進行類型轉換得到 ``FuncArguments*`` ，而後才能訪問 ``x`` 和 ``y`` 兩個字段並打印出來。
- 第 17~19 行使用 ``pthread_create`` 創建三個線程，分別綁定到 ``t0~t2`` 三個 ``pthread_t`` 實例上。它們均執行 ``func`` 函數，但接受的參數有所不同。

編譯運行，一種可能的輸出為：

.. code-block::

    x=1,y=2
    x=5,y=6
    x=3,y=4

從中可以看出，線程的實際執行順序不一定和我們創建它們的順序相同。在創建完三個線程之後，同時存在四個線程，即創建的三個線程和主線程，它們的執行順序取決於操作系統如何調度它們。這可能導致主線程先於我們創建的線程結束，在一些內核實現中，這種情況下整個進程直接退出，於是我們創建的線程也直接被刪除，未正常返回，沒有達到我們期望的效果。為了解決這個問題，我們可以使用 ``pthread_join`` 函數來使主線程等待某個線程退出之後再繼續向下執行。其函數簽名為：

.. code-block:: c

    #include <pthread.h>

    int pthread_join(pthread_t thread, void **retval);

我們需要傳入線程對應的 ``pthread_t`` 實例來等待一個線程退出。另一個參數 ``retval`` 是用來捕獲線程函數的返回值，我們這裡不展開。上面代碼片段的第 20~22 行我們便要求主線程依次等待我們創建的三個線程退出之後再退出，這樣主線程就不會影響到其他線程的執行。

在開發 Rust 多線程應用的時候，我們也可以使用標準庫 ``std::thread`` 中提供的 API 來創建、管理或結束線程。其中：

- ``std::thread::spawn`` 類似於 ``pthread_create`` ，可以創建一個線程，它會返回一個 ``JoinHandle`` 代表創建的線程；
- ``std::thread::JoinHandle::join`` 類似於 ``pthread_join`` ，用來等待調用 ``join`` 的 ``JoinHandle`` 對應的線程結束。

下面使用 Rust 重寫上面基於 C 語言的多線程應用：

.. code-block:: rust
    :linenos:

    use std::thread;
    struct FuncArguments {
        x: i32,
        y: i32,
    }
    fn func(args: FuncArguments) -> i32 {
        println!("x={},y={}", args.x, args.y);
        args.x + args.y
    }
    fn main() {
        let v = vec![
            thread::spawn(|| func(FuncArguments {x: 1, y: 2})),
            thread::spawn(|| func(FuncArguments {x: 3, y: 4})),
            thread::spawn(|| func(FuncArguments {x: 5, y: 6})),
        ];
        for handle in v {
            println!("result={}", handle.join().unwrap());
        }
    }

可以看到，相比 C 語言，在 Rust 實現中無需進行繁瑣的類型轉換，直接正常將參數傳入 ``thread::spawn`` 所需的閉包中即可。同時使用 ``handle.join`` 即可接收線程函數的返回值。一種可能的運行結果如：

.. code-block::

    x=1,y=2
    result=3
    x=3,y=4
    x=5,y=6
    result=7
    result=11

從中可以觀察到主線程和我們創建的線程在操作系統的調度下交錯運行。

為了在 “達科塔盜龍” [#dak]_ 操作系統中實現類似 Linux 操作系統的多線程支持，我們需要建立精簡的線程模型和相關係統調用，並圍繞這兩點來改進操作系統。

線程模型與重要系統調用
----------------------------------------------

目前，我們只介紹本章實現的內核中採用的一種非常簡單的線程模型。這個線程模型有如下特徵：

- 線程有三種狀態：就緒態、運行態和阻塞態（阻塞態是本章後面併發部分的重點概念，到時會詳細講解）；
- 同進程下的所有線程共享所屬進程的地址空間和其他共享資源（如文件等）；
- 線程可被操作系統調度來分時佔用 CPU 執行；
- 線程可以動態創建和退出；
- 同進程下的多個線程不像進程一樣存在父子關係，但有一個特殊的主線程在它所屬進程被創建的時候產生，應用程序的 ``main`` 函數就運行在這個主線程上。當主線程退出後，整個進程立即退出，也就意味著不論進程下的其他線程處於何種狀態也隨之立即退出；
- 線程可通過系統調用獲得操作系統的服務。注意線程和進程兩個系列的系統調用不能混用。

我們實現的線程模型建立在進程的地址空間抽象之上：同進程下的所有線程共享該進程的地址空間，包括代碼段和數據段。從邏輯上來說某些段是由所有線程共享的（比如包含代碼中的全局變量的全局數據段），而某些段是由某個線程獨佔的（比如操作系統為每個線程分配的棧），通常情況下程序員會遵循這種約定。然而，線程之間並不能嚴格做到隔離。舉例來說，一個線程訪問另一個線程的棧這種行為並不會被操作系統和硬件禁止。這也體現了線程和進程的不同：線程的誕生是為了方便共享，而進程更強調隔離。

此外，線程模型還需要操作系統支持一些重要的系統調用：創建線程、等待線程結束等來支持靈活的多線程應用。接下來我們介紹這些系統調用的基本功能和設計思路。

線程的創建
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在我們的內核中，通過 ``thread_create`` 系統調用可以創建一個從屬於當前進程的線程。類似於 C 標準庫中的 ``pthread_create`` ，我們也需要傳入線程運行的函數的入口地址和函數接受的參數。不同之處在於： pthread 系列 API 中基於 ``pthread_t`` 實例對線程進行控制，而我們則是用線程的線程標識符（TID, Thread Identifier）來區分不同線程並對指定線程進行控制，這一點類似於進程的控制方式。因此，在沒有出錯的情況下，我們的 ``thread_create`` 系統調用會返回創建的線程的 TID 。具體系統調用原型如下：

.. code-block:: rust
   :linenos:

   /// 功能：當前進程創建一個新的線程
   /// 參數：entry 表示線程的入口函數地址，arg 表示傳給線程入口函數參數
   /// 返回值：創建的線程的 TID
   /// syscall ID: 1000
   pub fn sys_thread_create(entry: usize, arg: usize) -> isize; 

內核會為每個線程分配一組專屬於該線程的資源：用戶棧、Trap 上下文還有內核棧，前面兩個在進程地址空間中，內核棧在內核地址空間中。這樣這些線程才能相對獨立地被調度和執行。相比於創建進程的 ``fork`` 系統調用，創建線程無需建立新的地址空間，這是二者之間最大的不同。另外屬於同一進程中的線程之間沒有父子關係，這一點也與進程不一樣。

.. 當進程調用 ``thread_create`` 系統調用後，內核會在這個進程內部創建一個新的線程，這個線程能夠訪問到進程所擁有的代碼段，堆和其他數據段。但內核會給這個新線程分配一個它專有的用戶態棧，這樣每個線程才能相對獨立地被調度和執行。另外，由於用戶態進程與內核之間有各自獨立的頁表，所以二者需要有一個跳板頁 ``TRAMPOLINE`` 來處理用戶態切換到內核態的地址空間平滑轉換的事務。所以當出現線程後，在進程中的每個線程也需要有一個獨立的跳板頁 ``TRAMPOLINE`` 來完成同樣的事務。

簡單線程管理
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

類似 ``getpid`` ，我們新增了一個 ``gettid`` 的系統調用可以獲取當前線程的 TID，其 syscall ID 為1001 。由於比較簡單，在這裡不再贅述。

線程退出及資源回收
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在 C/Rust 語言實現的多線程應用中，當線程執行的函數返回之後線程會自動退出，在編程的時候無需對函數做任何特殊處理。其實現原理是當函數返回之後，會自動跳轉到用戶態一段預先設置好的代碼，在這段代碼中通過系統調用實現線程退出操作。在這裡，我們為了讓實現更加簡單，約定線程函數需要在返回之前通過 ``exit`` 系統調用退出。這裡 ``exit`` 系統調用的含義發生了變化：從進程退出變成線程退出。

內核在收到線程發出的 ``exit`` 系統調用後，會回收線程佔用的用戶態資源，包括用戶棧和 Trap 上下文等。線程佔用的內核態資源（包括內核棧等）則需要在進程內使用 ``waittid`` 系統調用來回收，這樣該線程佔用的資源才能被完全回收。 ``waittid`` 的系統調用原型如下：

.. code-block:: rust
    :linenos:

    /// 功能：等待當前進程內的一個指定線程退出
    /// 參數：tid 表示指定線程的 TID
    /// 返回值：如果線程不存在，返回-1；如果線程還沒退出，返回-2；其他情況下，返回結束線程的退出碼
    /// syscall ID: 1002
    pub fn sys_waittid(tid: usize) -> i32;  

``waittid`` 基本上就是把我們比較熟悉的 ``waitpid`` 的操作對象從進程換成了線程，使用方法也和 ``waitpid`` 比較像。它像 ``pthread_join`` 一樣能起到一定的同步作用，也能夠徹底回收一個線程的資源。一般情況下進程/主線程要負責通過 ``waittid`` 來等待它創建出來的線程（不是主線程）結束並回收它們在內核中的資源（如線程的內核棧、線程控制塊等）。如果進程/主線程先調用了 ``exit`` 系統調用來退出，那麼整個進程（包括所屬的所有線程）都會退出，而對應父進程會通過 ``waitpid`` 回收子進程剩餘還沒被回收的資源。

進程相關的系統調用
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在引入了線程機制後，進程相關的重要系統調用： ``fork`` 、 ``exec`` 、 ``waitpid`` 雖然在接口上沒有變化，但在它要完成的功能上需要有一定的擴展。首先，需要注意到把以前進程中與處理器執行相關的部分拆分到線程中。這樣，在通過 ``fork`` 創建進程其實也意味著要單獨建立一個主線程來使用處理器，併為以後創建新的線程建立相應的線程控制塊向量。相對而言， ``exec`` 和 ``waitpid`` 這兩個系統調用要做的改動比較小，還是按照與之前進程的處理方式來進行。

而且，為了實現更加簡單，我們要求每個應用對於 **線程和進程兩個系列的系統調用只能使用其中之一** 。比如說，使用了進程系列的 ``fork`` 就不能使用線程系列的 ``thread_create`` ，這是因為很難定義如何 ``fork`` 一個多線程的進程。類似的，可以發現要將進程和線程模型融合起來需要做很多額外的工作。如果做了上述要求的話，我們就可以對進程-線程的融合模型進行簡化。如果涉及到父子進程的交互，那麼這些進程只會有一個主線程，基本等價於之前的進程模型；如果使用 ``thread_create`` 創建了新線程，那麼我們只需考慮多個線程在這一個進程內的交互。因此，總體上看，進程相關的這三個系統調用還是保持了已有的進程操作的語義，並沒有由於引入了線程，而帶來大的變化。

應用程序示例
----------------------------------------------

我們剛剛介紹了 ``thread_create/waittid`` 兩個重要系統調用，我們可以藉助它們和之前實現的系統調用開發出功能更為靈活的應用程序。下面我們通過描述一個多線程應用程序 ``threads`` 的開發過程，來展示這些系統調用的使用方法。


系統調用封裝
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

同學可以在 ``user/src/syscall.rs`` 中看到以 ``sys_*`` 開頭的系統調用的函數原型，它們後續還會在 ``user/src/lib.rs`` 中被封裝成方便應用程序使用的形式。如 ``sys_thread_create`` 被封裝成 ``thread_create`` ，而 ``sys_waittid`` 被封裝成 ``waittid``  ：   



.. code-block:: rust
    :linenos:

    // user/src/lib.rs

    pub fn thread_create(entry: usize, arg: usize) -> isize {
        sys_thread_create(entry, arg)
    }

    pub fn waittid(tid: usize) -> isize {
        loop {
            match sys_waittid(tid) {
                -2 => { yield_(); }
                exit_code => return exit_code,
            }
        }
    }

``waittid`` 等待一個線程標識符的值為 tid 的線程結束。在具體實現方面，我們看到當 ``sys_waittid`` 返回值為 -2 ，即要等待的線程存在但它卻尚未退出的時候，主線程調用 ``yield_`` 主動交出 CPU 使用權，待下次 CPU 使用權被內核交還給它的時候再次調用 ``sys_waittid`` 查看要等待的線程是否退出。這樣做是為了減小 CPU 資源的浪費以及儘可能簡化內核的實現。


多線程應用程序
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

多線程應用程序 -- ``threads`` 開始執行後，先調用 ``thread_create`` 創建了三個線程，加上進程自帶的主線程，其實一共有四個線程。每個線程在打印了 1000 個字符後，會執行 ``exit`` 退出。進程通過 ``waittid`` 等待這三個線程結束後，最終結束進程的執行。下面是多線程應用程序 -- ``threads`` 的源代碼：

.. code-block:: rust
    :linenos:

    //usr/src/bin/threads.rs

    #![no_std]
    #![no_main]

    #[macro_use]
    extern crate user_lib;
    extern crate alloc;

    use user_lib::{thread_create, waittid, exit};
    use alloc::vec::Vec;

    pub fn thread_a() -> ! {
        for _ in 0..1000 { print!("a"); }
        exit(1)
    }

    pub fn thread_b() -> ! {
        for _ in 0..1000 { print!("b"); }
        exit(2) 
    }

    pub fn thread_c() -> ! {
        for _ in 0..1000 { print!("c"); }
        exit(3)
    }

    #[no_mangle]
    pub fn main() -> i32 {
        let mut v = Vec::new();
        v.push(thread_create(thread_a as usize, 0));
        v.push(thread_create(thread_b as usize, 0));
        v.push(thread_create(thread_c as usize, 0));
        for tid in v.iter() {
            let exit_code = waittid(*tid as usize);
            println!("thread#{} exited with code {}", tid, exit_code);
        }
        println!("main thread exited.");
        0
    }

另一個名為 ``threads_arg`` 的應用和 ``threads`` 的功能相同，其不同在於利用 ``thread_create`` 可以傳參的特性，從而只需編寫一個線程函數。

.. code-block:: rust
    :linenos:

    #![no_std]
    #![no_main]

    #[macro_use]
    extern crate user_lib;
    extern crate alloc;

    use alloc::vec::Vec;
    use user_lib::{exit, thread_create, waittid};

    struct Argument {
        pub ch: char,
        pub rc: i32,
    }

    fn thread_print(arg: *const Argument) -> ! {
        let arg = unsafe { &*arg };
        for _ in 0..1000 {
            print!("{}", arg.ch);
        }
        exit(arg.rc)
    }

    #[no_mangle]
    pub fn main() -> i32 {
        let mut v = Vec::new();
        let args = [
            Argument { ch: 'a', rc: 1 },
            Argument { ch: 'b', rc: 2 },
            Argument { ch: 'c', rc: 3 },
        ];
        for arg in args.iter() {
            v.push(thread_create(
                thread_print as usize,
                arg as *const _ as usize,
            ));
        }
        for tid in v.iter() {
            let exit_code = waittid(*tid as usize);
            println!("thread#{} exited with code {}", tid, exit_code);
        }
        println!("main thread exited.");
        0
    }

這裡傳給創建的三個線程的參數放在主線程的棧上，在 ``thread_create`` 的時候提供的是對應參數的地址。參數會決定每個線程打印的字符和線程的返回碼。

線程管理的核心數據結構
-----------------------------------------------

為了實現線程機制，我們需要將操作系統的 CPU 資源調度單位（也即“任務”）從之前的進程改為線程。這意味著調度器需要考慮更多的因素，比如當一個線程時間片用盡交出 CPU 使用權的時候，切換到同進程下還是不同進程下的線程的上下文切換開銷往往有很大不同，可能影響到是否需要切換頁表。不過我們為了實現更加簡單，仍然採用 Round-Robin 調度算法，將所有線程一視同仁，不考慮它們屬於哪個進程。

本章之前，進程管理的三種核心數據結構和一些軟/硬件資源如下：

第一個數據結構是任務（進程）控制塊 ``TaskControlBlock`` ，可以在 ``os/src/task/task.rs`` 中找到。它除了記錄當前任務的狀態之外，還包含如下資源：

- 進程標識符 ``pid`` ；
- 內核棧 ``kernel_stack`` ；
- 進程地址空間 ``memory_set`` ；
- 進程地址空間中的用戶棧和 Trap 上下文（進程控制塊中相關字段為 ``trap_cx_ppn`` ）；
- 文件描述符表 ``fd_table`` ；
- 信號相關的字段。

這些資源的生命週期基本上與進程的生命週期相同。但是在有了線程之後，我們需要將一些與代碼執行相關的資源分離出來，讓它們與相關線程的生命週期綁定。

第二個數據結構是任務管理器 ``TaskManager`` ，可以在 ``os/src/task/manager.rs`` 中找到。它實質上是我們內核的調度器，可以決定一個任務時間片用盡或退出之後接下來執行哪個任務。

第三個數據結構是處理器管理結構 ``Processor`` ，可以在 ``os/src/task/processor.rs`` 中找到。它維護了處理器當前在執行哪個任務，在處理系統調用的時候我們需要依據這裡的記錄來確定系統調用的發起者是哪個任務。

本章的變更如下：

- 進程控制塊由之前的 ``TaskControlBlock`` 變成新增的 ``ProcessControlBlock`` （簡稱 PCB ），我們在其中保留進程的一些信息以及由進程下所有線程共享的一些資源。 PCB 可以在 ``os/src/task/process.rs`` 中找到。任務控制塊 ``TaskControlBlock`` 則變成用來描述線程的線程控制塊，包含線程的信息以及線程獨佔的資源。
- 在資源管理方面，本章之前在 ``os/src/task/pid.rs`` 可以看到與進程相關的一些 RAII 風格的軟/硬件資源，包括進程描述符 ``PidHandle`` 以及內核棧 ``KernelStack`` ，其中內核棧被分配在內核地址空間中且其位置由所屬進程的進程描述符決定。本章將 ``pid.rs`` 替換為 ``id.rs`` ，仍然保留 ``PidHandle`` 和 ``KernelStack`` 兩種資源，不過 ``KernelStack`` 變為一種線程獨佔的資源，我們可以在線程控制塊 ``TaskControlBlock`` 中找到它。此外，我們還在 ``id.rs`` 中新增了 ``TaskUserRes`` 表示每個線程獨佔的用戶態資源，還有一個各類資源的通用分配器 ``RecycleAllocator`` 。
- CPU 資源調度單位仍為任務控制塊 ``TaskControlBlock`` 不變。因此，基於任務控制塊的任務控制器 ``TaskManager`` 和處理器管理結構 ``Processor`` 也基本不變，只有某些接口有小幅修改。

.. 為了在現有進程管理的基礎上實現線程管理，我們需要改進一些數據結構包含的內容及接口。基本思路就是把進程中與處理器相關的部分分拆出來，形成線程相關的部分。
.. 本節將按照如下順序來進行介紹：

.. - 任務控制塊 ``TaskControlBlock`` ：表示線程的核心數據結構。
.. - 任務管理器 ``TaskManager`` ：管理線程集合的核心數據結構。
.. - 處理器管理結構 ``Processor`` ：用於線程調度，維護當前時刻處理器的狀態。

接下來依次對它們進行介紹。

通用資源分配器及線程相關的軟硬件資源
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在 ``os/src/task/id.rs`` 中，我們將之前的 ``PidAllocator`` 改造為通用的資源分配器 ``RecycleAllocator`` 用來分配多種不同的資源。這些資源均為 RAII 風格，可以在被 drop 掉之後自動進行資源回收：

- 進程描述符 ``PidHandle`` ；
- 線程獨佔的線程資源組 ``TaskUserRes`` ，其中包括線程描述符；
- 線程獨佔的內核棧 ``KernelStack`` 。

通用資源分配器 ``RecycleAllocator`` 的實現如下：

.. code-block:: rust
    :linenos:

    // os/src/task/id.rs

    pub struct RecycleAllocator {
        current: usize,
        recycled: Vec<usize>,
    }

    impl RecycleAllocator {
        pub fn new() -> Self {
            RecycleAllocator {
                current: 0,
                recycled: Vec::new(),
            }
        }
        pub fn alloc(&mut self) -> usize {
            if let Some(id) = self.recycled.pop() {
                id
            } else {
                self.current += 1;
                self.current - 1
            }
        }
        pub fn dealloc(&mut self, id: usize) {
            assert!(id < self.current);
            assert!(
                !self.recycled.iter().any(|i| *i == id),
                "id {} has been deallocated!",
                id
            );
            self.recycled.push(id);
        }
    }

分配與回收的算法與之前的 ``PidAllocator`` 一樣，不過分配的內容從 PID 變為一個非負整數的通用標識符，可以用來表示多種不同資源。這個通用整數標識符可以直接用作進程的 PID 和進程內一個線程的 TID 。下面是 PID 的全局分配器 ``PID_ALLOCATOR`` ：

.. code-block:: rust

    // os/src/task/id.rs

    lazy_static! {
        static ref PID_ALLOCATOR: UPSafeCell<RecycleAllocator> =
            unsafe { UPSafeCell::new(RecycleAllocator::new()) };
    }

    pub fn pid_alloc() -> PidHandle {
        PidHandle(PID_ALLOCATOR.exclusive_access().alloc())
    }

    impl Drop for PidHandle {
        fn drop(&mut self) {
            PID_ALLOCATOR.exclusive_access().dealloc(self.0);
        }
    }

調用 ``pid_alloc`` 可以從全局 PID 分配器中分配一個 PID 並構成一個 RAII 風格的 ``PidHandle`` 。當 ``PidHandle`` 被回收的時候則會自動調用 ``drop`` 方法在全局 PID 分配器將對應的 PID 回收。

對於 TID 而言，每個進程控制塊中都有一個給進程內的線程分配資源的通用分配器：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 12

    // os/src/task/process.rs

    pub struct ProcessControlBlock {
        // immutable
        pub pid: PidHandle,
        // mutable
        inner: UPSafeCell<ProcessControlBlockInner>,
    }

    pub struct ProcessControlBlockInner {
        ...
        pub task_res_allocator: RecycleAllocator,
        ...
    }

    impl ProcessControlBlockInner {
        pub fn alloc_tid(&mut self) -> usize {
            self.task_res_allocator.alloc()
        }

        pub fn dealloc_tid(&mut self, tid: usize) {
            self.task_res_allocator.dealloc(tid)
        }
    }

可以看到進程控制塊中有一個名為 ``task_res_allocator`` 的通用分配器，同時還提供了 ``alloc_tid`` 和 ``dealloc_tid`` 兩個接口來分別在創建線程和銷燬線程的時候分配和回收 TID 。除了 TID 之外，每個線程都有自己獨立的用戶棧和 Trap 上下文，且它們在所屬進程的地址空間中的位置可由 TID 計算得到。參考新的進程地址空間如下圖所示：

.. image:: app-as-full-with-threads.png
    :align: center
    :width: 600px

可以看到，在低地址空間中，在放置完應用 ELF 的所有段之後，會預留 4KiB 的空間作為保護頁，得到地址 ``ustack_base`` ，這部分實現可以參考創建應用地址空間的 ``MemorySet::from_elf`` ， ``ustack_base`` 即為其第二個返回值。接下來從 ``ustack_base`` 開始按照 TID 從小到大的順序向高地址放置線程的用戶棧，兩兩之間預留一個保護頁放置棧溢出。在高地址空間中，最高的虛擬頁仍然作為跳板頁，跳板頁中放置的是隻讀的代碼，因此線程之間可以共享。然而，每個線程需要有自己的 Trap 上下文，於是我們在跳板頁的下面向低地址按照 TID 從小到大的順序放置線程的 Trap 上下文。也就是說，只要知道線程的 TID ，我們就可以計算出線程在所屬進程地址空間內的用戶棧和 Trap 上下文的位置，計算方式由下面的代碼給出：

.. code-block:: rust

    // os/src/config.rs

    pub const TRAMPOLINE: usize = usize::MAX - PAGE_SIZE + 1;
    pub const TRAP_CONTEXT_BASE: usize = TRAMPOLINE - PAGE_SIZE;

    // os/src/task/id.rs

    fn trap_cx_bottom_from_tid(tid: usize) -> usize {
        TRAP_CONTEXT_BASE - tid * PAGE_SIZE
    }

    fn ustack_bottom_from_tid(ustack_base: usize, tid: usize) -> usize {
        ustack_base + tid * (PAGE_SIZE + USER_STACK_SIZE)
    }

線程的 TID 、用戶棧和 Trap 上下文均和線程的生命週期相同，因此我們可以將它們打包到一起統一進行分配和回收。這就形成了名為 ``TaskUserRes`` 的線程資源集合，它可以在任務（線程）控制塊 ``TaskControlBlock`` 中找到：

.. code-block:: rust
    :linenos:

    // os/src/task/id.rs

    pub struct TaskUserRes {
        pub tid: usize,
        pub ustack_base: usize,
        pub process: Weak<ProcessControlBlock>,
    }

    impl TaskUserRes {
        pub fn new(
            process: Arc<ProcessControlBlock>,
            ustack_base: usize,
            alloc_user_res: bool,
        ) -> Self {
            let tid = process.inner_exclusive_access().alloc_tid();
            let task_user_res = Self {
                tid,
                ustack_base,
                process: Arc::downgrade(&process),
            };
            if alloc_user_res {
                task_user_res.alloc_user_res();
            }
            task_user_res
        }

        /// 在進程地址空間中實際映射線程的用戶棧和 Trap 上下文。
        pub fn alloc_user_res(&self) {
            let process = self.process.upgrade().unwrap();
            let mut process_inner = process.inner_exclusive_access();
            // alloc user stack
            let ustack_bottom = ustack_bottom_from_tid(self.ustack_base, self.tid);
            let ustack_top = ustack_bottom + USER_STACK_SIZE;
            process_inner.memory_set.insert_framed_area(
                ustack_bottom.into(),
                ustack_top.into(),
                MapPermission::R | MapPermission::W | MapPermission::U,
            );
            // alloc trap_cx
            let trap_cx_bottom = trap_cx_bottom_from_tid(self.tid);
            let trap_cx_top = trap_cx_bottom + PAGE_SIZE;
            process_inner.memory_set.insert_framed_area(
                trap_cx_bottom.into(),
                trap_cx_top.into(),
                MapPermission::R | MapPermission::W,
            );
        }
    }

``TaskUserRes`` 中記錄了進程分配的 TID ，用來計算線程用戶棧位置的 ``ustack_base`` 。我們還需要所屬進程的弱引用，因為 ``TaskUserRes`` 中的資源都在進程控制塊中，特別是其中的用戶棧和 Trap 上下文需要在進程地址空間 ``MemorySet`` 中進行映射。因此我們需要進程控制塊來完成實際的資源分配和回收。

在使用 ``TaskUserRes::new`` 新建的時候進程控制塊會分配一個 TID 用於初始化，但並不一定調用 ``TaskUserRes::alloc_user_res`` 在進程地址空間中實際對用戶棧和 Trap 上下文進行映射，這要取決於 ``new`` 參數中的 ``alloc_user_res`` 是否為真。舉例來說，在 ``fork`` 子進程並創建子進程的主線程的時候，就不必再分配一次用戶棧和 Trap 上下文，因為子進程拷貝了父進程的地址空間，這些內容已經被映射過了。因此這個時候 ``alloc_user_res`` 為假。其他情況下則需要進行映射。

當線程退出之後， ``TaskUserRes`` 會隨著線程控制塊一起被回收，意味著進程分配給它的資源也會被回收：

.. code-block:: rust
    :linenos:

    // os/src/task/id.rs

    impl TaskUserRes {
        fn dealloc_user_res(&self) {
            // dealloc tid
            let process = self.process.upgrade().unwrap();
            let mut process_inner = process.inner_exclusive_access();
            // dealloc ustack manually
            let ustack_bottom_va: VirtAddr = ustack_bottom_from_tid(self.ustack_base, self.tid).into();
            process_inner
                .memory_set
                .remove_area_with_start_vpn(ustack_bottom_va.into());
            // dealloc trap_cx manually
            let trap_cx_bottom_va: VirtAddr = trap_cx_bottom_from_tid(self.tid).into();
            process_inner
                .memory_set
                .remove_area_with_start_vpn(trap_cx_bottom_va.into());
        }
        pub fn dealloc_tid(&self) {
            let process = self.process.upgrade().unwrap();
            let mut process_inner = process.inner_exclusive_access();
            process_inner.dealloc_tid(self.tid);
        }
    }

    impl Drop for TaskUserRes {
        fn drop(&mut self) {
            self.dealloc_tid();
            self.dealloc_user_res();
        }
    }

可以看到我們依次調用 ``dealloc_tid`` 和 ``dealloc_user_res`` 使進程控制塊回收掉當前 TID 並在進程地址空間中解映射線程用戶棧和 Trap 上下文。

接下來是內核棧 ``KernelStack`` 。與之前一樣它是從內核高地址空間的跳板頁下面開始分配，每兩個內核棧中間用一個保護頁隔開，因此總體地址空間佈局和之前相同。不同的則是它的位置不再與 PID 或者 TID 掛鉤，而是與一種新的內核棧標識符有關。我們需要新增一個名為 ``KSTACK_ALLOCATOR`` 的通用資源分配器來對內核棧標識符進行分配。

.. code-block:: rust
    :linenos:

    // os/src/task/id.rs

    lazy_static! {
        static ref KSTACK_ALLOCATOR: UPSafeCell<RecycleAllocator> =
            unsafe { UPSafeCell::new(RecycleAllocator::new()) };
    }

    pub struct KernelStack(pub usize);

    /// Return (bottom, top) of a kernel stack in kernel space.
    pub fn kernel_stack_position(kstack_id: usize) -> (usize, usize) {
        let top = TRAMPOLINE - kstack_id * (KERNEL_STACK_SIZE + PAGE_SIZE);
        let bottom = top - KERNEL_STACK_SIZE;
        (bottom, top)
    }

    pub fn kstack_alloc() -> KernelStack {
        let kstack_id = KSTACK_ALLOCATOR.exclusive_access().alloc();
        let (kstack_bottom, kstack_top) = kernel_stack_position(kstack_id);
        KERNEL_SPACE.exclusive_access().insert_framed_area(
            kstack_bottom.into(),
            kstack_top.into(),
            MapPermission::R | MapPermission::W,
        );
        KernelStack(kstack_id)
    }

    impl Drop for KernelStack {
        fn drop(&mut self) {
            let (kernel_stack_bottom, _) = kernel_stack_position(self.0);
            let kernel_stack_bottom_va: VirtAddr = kernel_stack_bottom.into();
            KERNEL_SPACE
                .exclusive_access()
                .remove_area_with_start_vpn(kernel_stack_bottom_va.into());
            KSTACK_ALLOCATOR.exclusive_access().dealloc(self.0);
        }
    }

``KSTACK_ALLOCATOR`` 分配/回收的是內核棧標識符 ``kstack_id`` ，基於它可以用 ``kernel_stack_position`` 函數計算出內核棧在內核地址空間中的位置。進而， ``kstack_alloc`` 和 ``KernelStack::drop`` 分別在內核地址空間中通過映射/解映射完成內核棧的分配和回收。

於是，我們就將通用資源分配器和三種軟硬件資源的分配和回收機制介紹完了，這也是線程機制中最關鍵的一個部分。

進程和線程控制塊
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在引入線程機制之後，線程就代替進程成為了 CPU 資源的調度單位——任務。因此，代碼執行有關的一些內容被分離到任務（線程）控制塊中，其中包括線程狀態、各類上下文和線程獨佔的一些資源等。線程控制塊 ``TaskControlBlock`` 是內核對線程進行管理的核心數據結構。在內核看來，它就等價於一個線程。

.. code-block:: rust
    :linenos:

    // os/src/task/task.rs

    pub struct TaskControlBlock {
        // immutable
        pub process: Weak<ProcessControlBlock>,
        pub kstack: KernelStack,
        // mutable
        inner: UPSafeCell<TaskControlBlockInner>,
    }

    pub struct TaskControlBlockInner {
        pub res: Option<TaskUserRes>,
        pub trap_cx_ppn: PhysPageNum,
        pub task_cx: TaskContext,
        pub task_status: TaskStatus,
        pub exit_code: Option<i32>,
    }

線程控制塊中的不變量有所屬進程的弱引用和自身的內核棧。在可變的 inner 裡面則保存了線程資源集合 ``TaskUserRes`` 和 Trap 上下文。任務上下文 ``TaskContext`` 仍然保留在線程控制塊中，這樣才能正常進行線程切換。此外，還有線程狀態 ``TaskStatus`` 和線程退出碼 ``exit_code`` 。

進程控制塊中則保留進程內所有線程共享的資源：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 18, 19

    // os/src/task/process.rs

    pub struct ProcessControlBlock {
        // immutable
        pub pid: PidHandle,
        // mutable
        inner: UPSafeCell<ProcessControlBlockInner>,
    }

    pub struct ProcessControlBlockInner {
        pub is_zombie: bool,
        pub memory_set: MemorySet,
        pub parent: Option<Weak<ProcessControlBlock>>,
        pub children: Vec<Arc<ProcessControlBlock>>,
        pub exit_code: i32,
        pub fd_table: Vec<Option<Arc<dyn File + Send + Sync>>>,
        pub signals: SignalFlags,
        pub tasks: Vec<Option<Arc<TaskControlBlock>>>,
        pub task_res_allocator: RecycleAllocator,
        ... // 其他同步互斥相關資源
    }

其中 ``pid`` 為進程標識符，它在進程創建後的整個生命週期中不再變化。可變的 inner 中的變化如下：

- 第 18 行在進程控制塊裡面設置一個向量保存進程下所有線程的任務控制塊。其佈局與文件描述符表比較相似，可以看成一組可以拓展的線程控制塊插槽；
- 第 19 行是進程為進程內的線程分配資源的通用資源分配器 ``RecycleAllocator`` 。

任務管理器與處理器管理結構
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

任務管理器 ``TaskManager`` 和處理器管理結構 ``Processor`` 分別在 ``task/manager.rs`` 和 ``task/processor.rs`` 中。它們的接口和功能和之前基本上一致，但是由於任務控制塊 ``TaskControlBlock`` 和進程控制塊 ``ProcessControlBlock`` 和之前章節的語義不同，部分接口略有改動。讓我們再總體回顧一下它們對外提供的接口：

.. code-block:: rust

    // os/src/task/manager.rs

    /// 全局變量：
    /// 1. 全局任務管理器 TASK_MANAGER
    /// 2. 全局 PID-進程控制塊映射 PID2TCB

    /// 將線程加入就緒隊列
    pub fn add_task(task: Arc<TaskControlBlock>);
    /// 將線程移除出就緒隊列
    pub fn remove_task(task: Arc<TaskControlBlock>);
    /// 從就緒隊列中選出一個線程分配 CPU 資源
    pub fn fetch_task() -> Option<Arc<TaskControlBlock>>;
    /// 根據 PID 查詢進程控制塊
    pub fn pid2process(pid: usize) -> Option<Arc<ProcessControlBlock>>;
    /// 增加一對 PID-進程控制塊映射
    pub fn insert_into_pid2process(pid: usize, process: Arc<ProcessControlBlock>);
    /// 刪除一對 PID-進程控制塊映射
    pub fn remove_from_pid2process(pid: usize);

    // os/src/task/processor.rs

    /// 全局變量：當前處理器管理結構 PROCESSOR

    /// CPU 的調度主循環
    pub fn run_tasks();
    /// 取出當前處理器正在執行的線程
    pub fn take_current_task() -> Option<Arc<TaskControlBlock>>;
    /// 當前線程控制塊/進程控制塊/進程地址空間satp/線程Trap上下文
    pub fn current_task() -> Option<Arc<TaskControlBlock>>;
    pub fn current_process() -> Arc<ProcessControlBlock>;
    pub fn current_user_token() -> usize;
    pub fn current_trap_cx() -> &'static mut TrapContext;
    /// 當前線程Trap上下文在進程地址空間中的地址
    pub fn current_trap_cx_user_va() -> usize;
    /// 當前線程內核棧在內核地址空間中的地址
    pub fn current_kstack_top() -> usize;
    /// 將當前線程的內核態上下文保存指定位置，並切換到調度主循環
    pub fn schedule(switched_task_cx_ptr: *mut TaskContext);

.. 線程管理的結構是線程管理器，即任務管理器，位於 ``os/src/task/manager.rs`` 中，其數據結構和方法與之前章節中進程的任務管理器完全一樣，只不過管理單位從之前的任務（進程）換成了線程。而處理器管理結構 ``Processor`` 負責維護 CPU 狀態、調度和特權級切換等事務。其數據結構與之前章節中進程的處理器管理結構完全一樣。但在相關方法上面，由於多個線程有各自的用戶棧和跳板頁，所以有些不同，下面會進一步分析。

.. chyyuu 加一個taskmanager,processor的鏈接???

線程管理機制的設計與實現
-----------------------------------------------

在上述線程模型和內核數據結構的基礎上，我們還需完成線程管理的基本實現，從而構造出一個完整的“達科塔盜龍”操作系統。這裡將從如下幾個角度分析如何實現線程管理：

- 線程生命週期管理
- 線程執行中的調度和特權級切換

線程生命週期管理
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

線程生命週期管理包括線程從創建到退出的整個過程以及過程中的資源分配與回收。

線程創建
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

線程創建有兩種方式：第一種是在創建進程的時候默認為這個進程創建一個主線程（創建進程又分為若干種方式）；第二種是通過 ``thread_create`` 系統調用在當前進程內創建一個新的線程。

創建進程的第一種方式是調用 ``ProcessControlBlock::new`` 創建初始進程 ``INITPROC`` ：

.. code-block:: rust
    :linenos:

    // os/src/task/process.rs

    impl ProcessControlBlock {
        pub fn new(elf_data: &[u8]) -> Arc<Self> {
            // memory_set with elf program headers/trampoline/trap context/user stack
            let (memory_set, ustack_base, entry_point) = MemorySet::from_elf(elf_data);
            // allocate a pid
            let pid_handle = pid_alloc();
            // create PCB
            let process = ...;
            // create a main thread, we should allocate ustack and trap_cx here
            let task = Arc::new(TaskControlBlock::new(
                Arc::clone(&process),
                ustack_base,
                true,
            ));
            // prepare trap_cx of main thread
            let task_inner = task.inner_exclusive_access();
            let trap_cx = task_inner.get_trap_cx();
            let ustack_top = task_inner.res.as_ref().unwrap().ustack_top();
            let kstack_top = task.kstack.get_top();
            drop(task_inner);
            *trap_cx = TrapContext::app_init_context(
                entry_point,
                ustack_top,
                KERNEL_SPACE.exclusive_access().token(),
                kstack_top,
                trap_handler as usize,
            );
            // add main thread to the process
            let mut process_inner = process.inner_exclusive_access();
            process_inner.tasks.push(Some(Arc::clone(&task)));
            drop(process_inner);
            insert_into_pid2process(process.getpid(), Arc::clone(&process));
            // add main thread to scheduler
            add_task(task);
            process
        }
    }

    // os/src/task/mod.rs

    lazy_static! {
        pub static ref INITPROC: Arc<ProcessControlBlock> = {
            let inode = open_file("initproc", OpenFlags::RDONLY).unwrap();
            let v = inode.read_all();
            ProcessControlBlock::new(v.as_slice())
        };
    }

其中的要點在於：

- 第 10 和 12 行分別創建進程 PCB 和主線程的 TCB ；
- 第 18~29 行獲取所需的信息並填充主線程的 Trap 上下文；
- 第 32 行將主線程插入到進程的線程列表中。因為此時該列表為空，只需直接 ``push`` 即可；
- 第 34 行維護 PID-進程控制塊映射。
- 第 36 行將主線程加入到任務管理器使得它可以被調度。

創建進程的第二種方式是 ``fork`` 出新進程：

.. code-block:: rust
    :linenos:

    // os/src/task/process.rs

    impl ProcessControlBlock {
        /// Only support processes with a single thread.
        pub fn fork(self: &Arc<Self>) -> Arc<Self> {
            let mut parent = self.inner_exclusive_access();
            assert_eq!(parent.thread_count(), 1);
            // clone parent's memory_set completely including trampoline/ustacks/trap_cxs
            let memory_set = MemorySet::from_existed_user(&parent.memory_set);
            // alloc a pid
            let pid = pid_alloc();
            // copy fd table
            let mut new_fd_table: Vec<Option<Arc<dyn File + Send + Sync>>> = Vec::new();
            for fd in parent.fd_table.iter() {
                ...
            }
            // create child process pcb
            let child = ...;
            // add child
            parent.children.push(Arc::clone(&child));
            // create main thread of child process
            let task = Arc::new(TaskControlBlock::new(
                Arc::clone(&child),
                parent
                    .get_task(0)
                    .inner_exclusive_access()
                    .res
                    .as_ref()
                    .unwrap()
                    .ustack_base(),
                // here we do not allocate trap_cx or ustack again
                // but mention that we allocate a new kstack here
                false,
            ));
            // attach task to child process
            let mut child_inner = child.inner_exclusive_access();
            child_inner.tasks.push(Some(Arc::clone(&task)));
            drop(child_inner);
            // modify kstack_top in trap_cx of this thread
            let task_inner = task.inner_exclusive_access();
            let trap_cx = task_inner.get_trap_cx();
            trap_cx.kernel_sp = task.kstack.get_top();
            drop(task_inner);
            insert_into_pid2process(child.getpid(), Arc::clone(&child));
            // add this thread to scheduler
            add_task(task);
            child
        }
    }

- 第 18 行創建子進程的 PCB ，並在第 20 行將其加入到當前進程的子進程列表中。
- 第 22~34 行創建子進程的主線程控制塊，注意它繼承了父進程的 ``ustack_base`` ，並且不用重新分配用戶棧和 Trap 上下文。在第 37 行將主線程加入到子進程中。
- 子進程的主線程基本上繼承父進程的主線程 Trap 上下文，但是其中的內核棧地址需要修改，見第 42 行。
- 第 44 行將子進程插入到 PID-進程控制塊映射中。第 46 行將子進程的主線程加入到任務管理器中。

``exec`` 也是進程模型中的重要操作，它雖然並不會創建新的進程但會替換進程的地址空間。在引入線程機制後，其實現也需要更新，但原理與前面介紹的類似，由於篇幅原因不再贅述，感興趣的同學可自行了解。

第二種創建線程的方式是通過 ``thread_create`` 系統調用。重點是需要了解創建線程控制塊，在線程控制塊中初始化各個成員變量，建立好進程和線程的關係等。只有建立好這些成員變量，才能給線程建立一個靈活方便的執行環境。這裡列出支持線程正確運行所需的重要的執行環境要素：

- 線程的用戶態棧：確保在用戶態的線程能正常執行函數調用；
- 線程的內核態棧：確保線程陷入內核後能正常執行函數調用；
- 線程共享的跳板頁和線程獨佔的 Trap 上下文：確保線程能正確的進行用戶態與內核態間的切換；
- 線程的任務上下文：線程在內核態的寄存器信息，用於線程切換。

線程創建的具體實現如下：

.. code-block:: rust
    :linenos:

    // os/src/syscall/thread.rs

    pub fn sys_thread_create(entry: usize, arg: usize) -> isize {
        let task = current_task().unwrap();
        let process = task.process.upgrade().unwrap();
        // create a new thread
        let new_task = Arc::new(TaskControlBlock::new(
            Arc::clone(&process),
            task.inner_exclusive_access().res.as_ref().unwrap().ustack_base,
            true,
        ));
        // add new task to scheduler
        add_task(Arc::clone(&new_task));
        let new_task_inner = new_task.inner_exclusive_access();
        let new_task_res = new_task_inner.res.as_ref().unwrap();
        let new_task_tid = new_task_res.tid;
        let mut process_inner = process.inner_exclusive_access();
        // add new thread to current process
        let tasks = &mut process_inner.tasks;
        while tasks.len() < new_task_tid + 1 {
            tasks.push(None);
        }
        tasks[new_task_tid] = Some(Arc::clone(&new_task));
        let new_task_trap_cx = new_task_inner.get_trap_cx();
        *new_task_trap_cx = TrapContext::app_init_context(
            entry,
            new_task_res.ustack_top(),
            kernel_token(),
            new_task.kstack.get_top(),
            trap_handler as usize,
        );
        (*new_task_trap_cx).x[10] = arg;
        new_task_tid as isize
    }


上述代碼主要完成了如下事務：

- 第 4~5 行，找到當前正在執行的線程 ``task`` 和此線程所屬的進程 ``process`` 。
- 第 7~11 行，調用 ``TaskControlBlock::new`` 方法，創建一個新的線程 ``new_task`` ，在創建過程中，建立與進程 ``process`` 的所屬關係，分配了線程資源組 ``TaskUserRes`` 和其他資源。
- 第 13 行，把線程掛到調度隊列中。
- 第 19~22 行，把線程接入到所屬進程的線程列表 ``tasks`` 中。
- 第 25~32 行，初始化位於該線程在用戶態地址空間中的 Trap 上下文：設置線程的函數入口點和用戶棧，使得第一次進入用戶態時能從指定位置開始正確執行；設置好內核棧和陷入函數指針 ``trap_handler`` ，保證在 Trap 的時候用戶態的線程能正確進入內核態。

線程退出
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

線程可以通過 ``sys_exit`` 系統調用退出：

.. code-block:: rust

    // os/src/syscall/process.rs

    pub fn sys_exit(exit_code: i32) -> ! {
        exit_current_and_run_next(exit_code);
        panic!("Unreachable in sys_exit!");
    }

無論當前線程是否是主線程，都會調用 ``exit_current_and_run_next`` 。如果是主線程，將會導致整個進程退出，從而其他線程也會退出；否則的話，只有當前線程會退出。下面是具體實現：

.. code-block:: rust
    :linenos:

    // os/src/task/mod.rs

    pub fn exit_current_and_run_next(exit_code: i32) {
        let task = take_current_task().unwrap();
        let mut task_inner = task.inner_exclusive_access();
        let process = task.process.upgrade().unwrap();
        let tid = task_inner.res.as_ref().unwrap().tid;
        // record exit code
        task_inner.exit_code = Some(exit_code);
        task_inner.res = None;
        // here we do not remove the thread since we are still using the kstack
        // it will be deallocated when sys_waittid is called
        drop(task_inner);
        drop(task);
        // however, if this is the main thread of current process
        // the process should terminate at once
        if tid == 0 {
            let pid = process.getpid();
            ...
            remove_from_pid2process(pid);
            let mut process_inner = process.inner_exclusive_access();
            // mark this process as a zombie process
            process_inner.is_zombie = true;
            // record exit code of main process
            process_inner.exit_code = exit_code;

            {
                // move all child processes under init process
                let mut initproc_inner = INITPROC.inner_exclusive_access();
                for child in process_inner.children.iter() {
                    child.inner_exclusive_access().parent = Some(Arc::downgrade(&INITPROC));
                    initproc_inner.children.push(child.clone());
                }
            }

            // deallocate user res (including tid/trap_cx/ustack) of all threads
            // it has to be done before we dealloc the whole memory_set
            // otherwise they will be deallocated twice
            let mut recycle_res = Vec::<TaskUserRes>::new();
            for task in process_inner.tasks.iter().filter(|t| t.is_some()) {
                let task = task.as_ref().unwrap();
                // if other tasks are Ready in TaskManager or waiting for a timer to be
                // expired, we should remove them.
                //
                // Mention that we do not need to consider Mutex/Semaphore since they
                // are limited in a single process. Therefore, the blocked tasks are
                // removed when the PCB is deallocated.
                remove_inactive_task(Arc::clone(&task));
                let mut task_inner = task.inner_exclusive_access();
                if let Some(res) = task_inner.res.take() {
                    recycle_res.push(res);
                }
            }
            // dealloc_tid and dealloc_user_res require access to PCB inner, so we
            // need to collect those user res first, then release process_inner
            // for now to avoid deadlock/double borrow problem.
            drop(process_inner);
            recycle_res.clear();

            let mut process_inner = process.inner_exclusive_access();
            process_inner.children.clear();
            // deallocate other data in user space i.e. program code/data section
            process_inner.memory_set.recycle_data_pages();
            // drop file descriptors
            process_inner.fd_table.clear();
            // Remove all tasks except for the main thread itself.
            while process_inner.tasks.len() > 1 {
                process_inner.tasks.pop();
            }
        }
        drop(process);
        // we do not have to save task context
        let mut _unused = TaskContext::zero_init();
        schedule(&mut _unused as *mut _);
    }

- 第 4 行將當前線程從處理器管理結構 ``PROCESSOR`` 中移除，隨後在第 9 行在線程控制塊中記錄退出碼並在第 10 行回收當前線程的線程資源組 ``TaskUserRes`` 。
- 第 17~68 行針對當前線程是所屬進程主線程的情況退出整個進程和其他的所有線程（此時主線程已經在上一步中被移除）。其判斷條件為第 17 行的當前線程 TID 是否為 0 ，這是主線程的特徵。具體來說：
- 第 20~25 行更新 PID-進程控制塊映射，將進程標記為殭屍進程然後記錄進程退出碼， **進程退出碼即為其主線程退出碼** 。
- 第 29~33 行將子進程掛到初始進程 INITPROC 下面。
- 第 36~58 行回收所有線程的 ``TaskUserRes`` ，為了保證進程控制塊的獨佔訪問，我們需要先將所有的線程的 ``TaskUserRes`` 收集到向量 ``recycle_res`` 中。在第 57 行獨佔訪問結束後，第 58 行通過清空 ``recycle_res`` 自動回收所有的 ``TaskUserRes`` 。
- 第 60~65 行依次清空子進程列表、回收進程地址空間中用於存放數據的物理頁幀、清空文件描述符表。注意我們在回收物理頁幀之前必須將 ``TaskUserRes`` 清空，不然相關物理頁幀會被回收兩次。目前這種回收順序並不是最好的實現，同學可以想想看有沒有更合適的實現。
- 第 66~69 行移除除了主線程之外的所有線程。目前線程控制塊中，只有內核棧資源還未回收，但我們此時無法回收主線程的內核棧，因為當前的流程還是在這個內核棧上跑的，所以這裡要繞過主線程。等到整個進程被父進程通過 ``waitpid`` 回收的時候，主線程的內核棧會被一起回收。

這裡特別需要注意的是在第 48 行，主線程退出的時候可能有一些線程處於就緒狀態等在任務管理器 ``TASK_MANAGER`` 的隊列中，我們需要及時調用 ``remove_inactive_task`` 函數將它們從隊列中移除，不然將導致它們的引用計數不能成功歸零並回收資源，最終導致內存溢出。相關測例如 ``early_exit.rs`` ，請同學思考我們的內核能否正確處理這種情況。



等待線程結束
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

如果調用 ``sys_exit`` 退出的不是進程的主線程，那麼 ``sys_exit`` 之後該線程的資源並沒有被完全回收，這一點和進程比較像。我們還需要另一個線程調用 ``waittid`` 系統調用才能收集該線程的退出碼並徹底回收該線程的資源：

.. code-block:: rust
    :linenos:

    // os/src/syscall/thread.rs

    /// thread does not exist, return -1
    /// thread has not exited yet, return -2
    /// otherwise, return thread's exit code
    pub fn sys_waittid(tid: usize) -> i32 {
        let task = current_task().unwrap();
        let process = task.process.upgrade().unwrap();
        let task_inner = task.inner_exclusive_access();
        let mut process_inner = process.inner_exclusive_access();
        // a thread cannot wait for itself
        if task_inner.res.as_ref().unwrap().tid == tid {
            return -1;
        }
        let mut exit_code: Option<i32> = None;
        let waited_task = process_inner.tasks[tid].as_ref();
        if let Some(waited_task) = waited_task {
            if let Some(waited_exit_code) = waited_task.inner_exclusive_access().exit_code {
                exit_code = Some(waited_exit_code);
            }
        } else {
            // waited thread does not exist
            return -1;
        }
        if let Some(exit_code) = exit_code {
            // dealloc the exited thread
            process_inner.tasks[tid] = None;
            exit_code
        } else {
            // waited thread has not exited
            -2
        }
    }

- 第 12~14 行，如果是線程等自己，返回錯誤.
- 第 17~24 行，如果找到 ``tid`` 對應的退出線程，則收集該退出線程的退出碼 ``exit_tid`` ，否則返回錯誤（退出線程不存在）。
- 第 25~32 行，如果退出碼存在，則在第 27 行從進程的線程向量中將被等待的線程刪除。這意味著該函數返回之後，被等待線程的 TCB 的引用計數將被歸零從而相關資源被完全回收。否則，返回錯誤（線程還沒退出）。

線程執行中的特權級切換和調度切換
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在特權級切換方面，注意到在創建每個線程的時候，我們都正確設置了其用戶態線程函數入口地址、用戶棧、內核棧以及一些相關信息，於是第一次返回用戶態之後能夠按照我們的期望正確執行。後面在用戶態和內核態間切換沿用的是前面的 Trap 上下文保存與恢復機制，本章並沒有修改。有需要的同學可以回顧第二章和第四章的有關內容。

在線程切換方面，我們將任務上下文移至線程控制塊中並依然沿用第三章的任務切換機制。同時，線程調度算法我們仍然採取第三章中時間片輪轉的 Round-Robin 算法。

因此，這裡我們就不再重複介紹這兩種機制了。


.. [#dak] 達科塔盜龍是一種生存於距今6700萬-6500萬年前白堊紀晚期的獸腳類馳龍科恐龍，它主打的並不是霸王龍的力量路線，而是利用自己修長的後肢來提高敏捷度和奔跑速度。它全身幾乎都長滿了羽毛，可能會滑翔或者其他接近飛行行為的行動模式。
