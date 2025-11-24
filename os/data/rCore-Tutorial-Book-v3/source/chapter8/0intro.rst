引言
=========================================

本章導讀
-----------------------------------------

到本章開始之前，我們已經完成了組成應用程序執行環境的操作系統的三個重要抽象：進程、地址空間和文件，讓應用程序開發、運行和存儲數據更加方便和靈活。特別是操作系統通過硬件中斷機制，支持分時多任務和搶佔式調度機制。這樣操作系統能強制打斷進程的執行，及時處理I/O交互操作，從而提高整個系統的執行效率。有了進程以後，可以讓操作系統從宏觀層面實現多個應用的 :ref:`併發執行 <term-parallel-concurrency>` ，而併發是通過操作系統不斷地切換進程來達到的。

對於單核處理器而言，在任意一個時刻只會有一個進程被操作系統調度，從而在處理器上執行。到目前為止的併發，僅僅是進程間的併發，而對於一個進程內部，還沒有併發性的體現。而這就是線程（Thread）出現的起因：提高一個進程內的併發性。


.. chyyuu 
   https://en.wikipedia.org/wiki/Per_Brinch_Hansen 關於操作系統併發  Binch Hansen 和 Hoare ??？
	https://en.wikipedia.org/wiki/Thread_(computing) 關於線程
	http://www.serpentine.com/blog/threads-faq/the-history-of-threads/ The history of threads
	https://en.wikipedia.org/wiki/Core_War 我喜歡的一種早期遊戲
	[Dijkstra, 65] Dijkstra, E. W., Cooperating sequential processes, in Programming Languages, Genuys, F. (ed.), Academic Press, 1965.
	[Saltzer, 66] Saltzer, J. H., Traffic control in a multiplexed computer system, MAC-TR-30 (Sc.D. Thesis), July, 1966.
	https://en.wikipedia.org/wiki/THE_multiprogramming_system
	http://www.cs.utexas.edu/users/EWD/ewd01xx/EWD196.PDF
	https://en.wikipedia.org/wiki/Edsger_W._Dijkstra
	https://en.wikipedia.org/wiki/Per_Brinch_Hansen
	https://en.wikipedia.org/wiki/Tony_Hoare
	https://en.wikipedia.org/wiki/Mutual_exclusion
	https://en.wikipedia.org/wiki/Semaphore_(programming)
	https://en.wikipedia.org/wiki/Monitor_(synchronization)
	Dijkstra, Edsger W. The structure of the 'THE'-multiprogramming system (EWD-196) (PDF). E.W. Dijkstra Archive. Center for American History, University of Texas at Austin. (transcription) (Jun 14, 1965)

.. note::

	**Dijkstra 教授團隊設計解決併發問題的THE操作系統**

	早期的計算機硬件沒有內存隔離保護機制，多個程序以任務（task）的形式進行執行，但各個任務之間是依次執行（批處理方式）或相互獨立執行，基本沒有數據共享的情況，所以還沒有形成線程的概念。當多個任務需要共享數據和同步行為時，就需要擴展任務針對共享數據的執行特徵，並建立相應的同步互斥機制。
	
	在1962年，荷蘭的E.W.Dijkstra 教授和他的團隊正在為 Electrologica X8 計算機設計開發了 **THE 操作系統** 。他們觀察到如果多個程序在執行中訪問共享變量，可能會產生衝突和結果不確定。在E.W.Dijkstra 教授在信號量機制的研究中，提出了多個“sequential processes”可以通過信號量機制合作訪問共享變量，避免衝突導致結果不確定。這裡的“sequential processes”的含義就是後續的線程。

	**Dijkstra 教授設計出信號量機制**

	Dijkstra 教授帶領他的小團隊在設計開發THE操作系統的過程中，異步中斷觸發的難以重現的併發錯誤，讓他們在調試操作系統中碰到了困難。這種困難激發了Dijkstra團隊的靈感，他們設計了操作系統的分層結構來避免操作系統的複雜性負擔，同時還設計了信號量機制和對應的P和V操作，來確保線程對共享變量的靈活互斥訪問，並支持線程之間的同步操作。P和V是來自荷蘭語單詞“測試”和“增加”的首字母，是很罕見的非英語來源的操作系統術語。

	**貝爾實驗室Victor A. Vyssotsky提出線程（thread）概念**

	1964年開始設計的Multics操作系統已經有進程的概念，也有多處理器並行處理的GE 645硬件設計，甚至提出了線程（ **thread** ）的概念。1966年，參與Multics開發的MIT博士生 Jerome Howard Saltzer在其博士畢業論文的一個註腳提到貝爾實驗室的Victor A. Vyssotsky用 **thread** 這個名稱來表示處理器（processor）執行程序（program）代碼序列這個過程的抽象概念，Saltzer進一步把"進程（process）"描述為處理器執行程序代碼的當前狀態（即線程）和可訪問的地址空間。但他們並沒有建立類似信號量這樣的有效機制來避免併發帶來的同步互斥問題。

	**Brinch Hansen、Tony Hoare和Dijkstra提出管程機制**

	丹麥的Brinch Hansen，英國的Tony Hoare和Dijkstra並不滿足於信號量來解決操作系統和應用中的併發問題。因為對於複雜一些的同步互斥問題（如哲學家問題），如果使用信號量機制不小心，容易引起死鎖等錯誤。在 1971年的研討會上，他們三人開始討論管程（Monitor）的想法，希望設計一種更高級的併發管理語言結構，便於程序員開發併發程序。在1972年春天，Brinch Hansen 在他寫的“操作系統原理”教科書中，提出了管程的概念，並把這一概念嵌入到了Concurrent Pascal 編程語言中，然後他和他的學生再接再厲，在PDP 11/45計算機上編寫了Concurrent Pascal 編譯器，並用Concurrent Pascal 編寫了Solo操作系統。Brinch Hansen在操作系統和語言級併發處理方面的開創性工作影響了後續的操作系統併發處理機制（如條件變量等）和不少的編程語言併發方案。

	Brinch Hansen的兩句名言：

	  - 寫作是對簡單性的嚴格測試：不可能令人信服地寫出無法理解的想法。
	  - 編程是用清晰的散文寫文章並使它們可執行的藝術

.. hint::

	**並行與併發的區別**

	可回顧一下 :ref:`並行與併發的解釋 <term-parallel-concurrency>` 。在單處理器情況下，多個進程或線程是併發執行的。


有了進程以後，為什麼還會出現線程（Thread）呢？提高整個系統的並行/併發執行效率是主要的原因。考慮如下情況，對於很多應用（以單一進程的形式運行）而言，邏輯上由多個可並行執行的任務組成，如果其中一個任務被阻塞，將導致整個進程被阻塞，這意味著不依賴該任務的其他任務也被阻塞，然而它們實際上本不應該受到影響。這就降低了系統的併發執行效率。

舉個具體的例子，我們平常用編輯器來編輯文本內容的時候，都會有一個定時自動保存的功能，即把當前文檔內容保存到磁盤上。假設磁盤性能導致編輯器自動保存的過程較慢，並影響到整個進程被阻塞，這就會影響到用戶編輯文檔的人機交互體驗：即用戶只有等到磁盤寫入操作完成後，操作系統重新調度該進程運行，用戶才可繼續編輯文檔。

如果我們把一個進程內的多個可並行執行的任務通過一種更細粒度的方式讓操作系統進行調度，那麼就可以在進程內實現併發執行。在上面的例子中，負責保存文檔內容的任務與負責編輯文檔的任務可以併發執行，不會出現一個被阻塞的任務導致其它任務都阻塞的情況。這種任務就是一種更細粒度的調度對象，也就是我們這裡說的線程。


.. _term-thread-define:

線程定義
~~~~~~~~~~~~~~~~~~~~

簡單地說，線程是進程的組成部分，進程可包含1 -- n個線程，屬於同一個進程的線程共享進程的資源，比如地址空間，打開的文件等。線程基本上由線程ID、執行狀態、當前指令指針(PC)、寄存器集合和棧組成。線程是可以被操作系統或用戶態調度器獨立調度（Scheduling）和分派（Dispatch）的基本單位。

在本章之前，進程是程序的基本執行實體，是程序對某數據集合進行操作的一次執行過程，是系統進行資源（處理器，地址空間和文件等）分配和調度的基本單位。在有了線程後，對進程的定義也要調整了，進程是線程的資源容器，線程成為了程序的基本執行實體。


.. hint::

   **線程與進程的區別**
   
   注：下面的比較是把以線程為調度對象的操作系統作為分析對象：

   * 進程間相互獨立（即資源隔離），同一進程的各線程間共享進程的資源（即資源共享）；
   * 子進程和父進程有不同的地址空間和資源，而多個線程（沒有父子關係）則共享同一所屬進程的地址空間和資源；
   * 每個線程有其自己的執行上下文（線程ID、程序計數器、寄存器集合和執行棧），而進程的執行上下文包括其管理的所有線程的執行上下文和地址空間（故同一進程下的線程間上下文切換比進程間上下文切換要快）；
   * 線程是一個可調度/分派/執行的實體（線程有就緒、阻塞和運行三種基本執行狀態），進程不是可調度/分派/執行的的實體，而是線程的資源容器；
   * 進程間通信需要通過IPC機制（如管道等）， 屬於同一進程的線程間可以共享“即直接讀寫”進程的數據，但需要同步互斥機制的輔助，避免出現數據不一致性以及不確定計算結果的問題。


同步互斥
~~~~~~~~~~~~~~~~~~~~~~

在上面提到了數據不一致性、不確定的計算結果，意味在操作系統的執行過程中，可能存在併發問題，並導致程序或操作系統執行失敗。我們先給出 **線程的數據一致性** 的定義：在單處理器（即只有一個核的CPU）下，如果某線程更新了一個可被其他線程讀到的共享數據，那麼後續其他線程都能讀到這個最新被更新的共享數據。當多個線程共享同一進程的地址空間時，每個線程都可以訪問屬於這個進程的數據（全局變量）。如果每個線程使用到的變量都是其他線程不會讀取或者修改的話，各個線程訪問的變量與預期結果一樣，那麼就不存在一致性問題。如果變量是隻讀的，多個線程讀取該變量與預期結果一致，也不會有一致性問題。

但是，當某些線程在修改變量，而其他線程在讀取這個變量時，由於線程之間的執行順序不能提前預知（取決於操作系統的調度），導致各個線程對同一變量的讀寫操作序列不確定，這就會導致不同線程可能會看到與預期結果不一樣的值，這就出現了數據不一致性的問題，而且每次執行的結果不確定。我們把這種兩個或多個線程在競爭訪問同一資源時，執行結果取決於它們的不可預知的執行順序的情況稱為 **線程的競態條件（race condition）**。競態條件是一種常見的併發問題，可能導致應用程序或操作系統執行失敗。


出現線程的數據不一致問題和競態條件問題的根本原因是 **調度的不可控性** ：即讀寫共享變量的代碼片段會隨時可能被操作系統調度和切換。先看看如下的偽代碼例子：

.. code-block:: rust
    :linenos:

    //全局共享變量 NUM初始化為 0
    static mut NUM : usize = 0;
    ...

    //主進程中的所有線程都會執行如下的核心代碼
    unsafe { NUM = NUM + 1; }
    ...
    

    //所有線程執行完畢後，主進程顯示num的值
    unsafe {
        println!("NUM = {:?}", NUM);
    }


如果線程的個數為 ``n`` ，那麼最後主進程會顯示的數應該是多少呢？ 也許同學覺得應該也是 ``n`` ，但現實並不是這樣。為了瞭解事實真相，我們首先必須瞭解Rust編譯器對 ``num = num + 1;`` 這一行源代碼生成的彙編代碼序列。

.. code-block:: asm
    :linenos:

    # 假設NUM的地址為 0x1000
    # unsafe { NUM = NUM + 1; } 對應的彙編代碼如下
    addi x6, x0, 0x1000        # addr 100: 計算NUM的地址
                               # 由於時鐘中斷可能會發生線程切換
    ld 	 x5, 0(x6)             # addr 104: 把NUM的值加載到x5寄存器中
                               # 由於時鐘中斷可能會發生線程切換
    addi x5, x5, 1             # addr 108: x5 <- x5 + 1
                               # 由於時鐘中斷可能會發生線程切換
    sd   x5, 0(x6)             # addr 112: 把NUM+1的值寫回到NUM地址中
    

在這個例子中，一行Rust源代碼其實被Rust編譯器生成了四行RISC-V彙編代碼。如果多個線程在操作系統的管理和調度下都執行這段代碼，那麼在上述四行彙編代碼之間（即第4，6，8行的地方）的時刻可能產生時鐘中斷，並導致線程調度和切換。

設有兩個線程，線程A先進入上述彙編代碼區，將要把 ``NUM`` 增加一，為此線程A將 ``NUM`` 的值（假設它這時是 ``0`` ）加載到 ``x5`` 寄存器中，然後執行加一操作，此時 ``x5 = 1`` 。這時時鐘中斷髮生，操作系統將當前正在運行的線程A的上下文（它的程序計數器、寄存器，包括 ``x5`` 等）保存到線程控制塊（在內存中）中。

再接下來，線程B被選中運行，並進入同一段代碼。它也執行了前兩條指令，獲取 ``NUM`` 的值（此時仍為 ``0`` ）並將其放入 ``x5`` 中，線程B繼續執行接下來指令，將 ``x5`` 加一，然後將 ``x5`` 的內容保存到 ``NUM`` （地址 ``0x1000`` ）中。因此，全局變量 ``NUM`` 現在的值是 ``1`` 。

最後又發生一次線程上下文切換，線程A恢復運行，此時的 ``x5=1``，現在線程A準備執行最後一條 ``sd`` 指令，將 ``x5`` 的內容保存到 ``NUM`` （地址 ``0x1000`` ）中，``NUM`` 再次被設置為 ``1`` 。

簡單總結，這兩個線程執行的結果是：增加 ``NUM`` 的代碼被執行兩次，初始值為 ``0`` ，但是結果為 ``1`` 。而我們一般理解這兩個線程執行的“正確”結果應該是全局變量 ``NUM`` 等於  ``2`` 。


.. note::

	**併發相關術語** 　

	- 共享資源（shared resource）：不同的線程/進程都能訪問的變量或數據結構。	
	- 臨界區（critical section）：訪問共享資源的一段代碼。
	- 競態條件（race condition）：多個線程/進程都進入臨界區時，都試圖更新共享的數據結構，導致產生了不期望的結果。
	- 不確定性（indeterminate）： 多個線程/進程在執行過程中出現了競態條件，導致執行結果取決於哪些線程在何時運行，即執行結果不確定，而開發者期望得到的是確定的結果。
	- 原子性（atomic）：一系列操作要麼全部完成，要麼一個都沒執行，不會看到中間狀態。在數據庫領域，具有原子性的一系列操作稱為事務（transaction）。
	- 互斥（mutual exclusion）：一種原子性操作，能保證同一時間只有一個線程進入臨界區，從而避免出現競態條件，併產生確定的預期執行結果。
	- 同步（synchronization）：多個併發執行的進程/線程在一些關鍵點上需要互相等待，這種相互制約的等待稱為進程/線程同步。
	- 死鎖（dead lock）：一個線程/進程集合裡面的每個線程/進程都在等待只能由這個集合中的其他一個線程/進程（包括他自身）才能引發的事件，這種情況就是死鎖。
	- 飢餓（hungry）：指一個可運行的線程/進程儘管能繼續執行，但由於操作系統的調度而被無限期地忽視，導致不能執行的情況。


在後續的章節中，會大量使用上述術語，如果現在還不夠理解，沒關係，隨著後續的一步一步的分析和實驗，相信大家能夠掌握上述術語的實際含義。

為了解決數據不一致問題和競態條件問題，操作系統需要提供一些保障機制（比如互斥、同步等），無論操作系統如何調度（當然需要是正常情況下的調度）這些對共享數據進行讀寫的線程，各個線程都能得到預期的共享數據的正確訪問結果。操作系統中常見的同步互斥機制包括：互斥鎖（Mutex Lock）、信號量（Semaphore）、條件變量（Conditional Variable）等。

互斥鎖
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

互斥鎖是操作系統中用於保護共享資源的機制。互斥鎖能夠確保在任何時候只有一個線程訪問共享資源，從而避免資源競爭導致的數據不一致的問題。可以使用Rust標準庫中的 std::sync::Mutex 類型來實現互斥鎖。下面是一個使用互斥鎖保護共享變量的示例：


.. code-block:: Rust
    :linenos:

	use std::sync::{Arc, Mutex};
	use std::thread;

	fn main() {
		// 創建一個可變的整數並將其包裝在 Mutex 中
		let data = Arc::new(Mutex::new(0));

		// 創建兩個線程，並傳遞 `data` 的 Arc 實例給它們
		let data_clone = data.clone();
		let handle1 = thread::spawn(move || {
			let mut data = data_clone.lock().unwrap();
			*data += 1;
		});

		let data_clone = data.clone();
		let handle2 = thread::spawn(move || {
			let mut data = data_clone.lock().unwrap();
			*data += 1;
		});

		// 等待兩個線程結束
		handle1.join().unwrap();
		handle2.join().unwrap();

		// 輸出結果
		println!("Result: {}", *data.lock().unwrap());
	}

在上面的代碼中，兩個線程都會嘗試訪問 data 變量，但是因為它被包裝在了 Mutex 中，所以只有一個線程能夠獲取鎖並訪問變量。在獲取互斥鎖的時候，線程會被掛起，直到另一個線程釋放了鎖。最終的輸出結果是 `2`。




條件變量
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

條件變量是操作系統中的一種同步原語，可用於在多個線程之間進行協作，即允許一個線程在另一個線程完成某些操作之前等待。條件變量與互斥鎖經常一起使用，以保證在同一時刻只有一個線程在訪問共享資源。

在 Rust 中，條件變量是由 std::sync::Condvar 結構體表示的。條件變量需要配合互斥體（由 std::sync::Mutex 結構體表示）使用，因為條件變量用於在互斥體保護的條件下通知等待的線程。

.. code-block:: Rust
    :linenos:

	fn main() {
		use std::sync::{Arc, Condvar, Mutex};
		use std::thread;

		let pair = Arc::new((Mutex::new(false), Condvar::new()));
		let pair2 = Arc::clone(&pair);

		// Inside of our lock, spawn a new thread, and then wait for it to start.
		thread::spawn(move || {
			let (lock, cvar) = &*pair2;
			let mut started = lock.lock().unwrap();
			*started = true;
			// We notify the condvar that the value has changed.
			cvar.notify_one();
		});

		// Wait for the thread to start up.
		let (lock, cvar) = &*pair;
		let mut started = lock.lock().unwrap();
		while !*started {
			started = cvar.wait(started).unwrap();
		}
	}

這是一個使用 Rust 中的條件變量（Condvar）和互斥鎖（Mutex）來同步兩個線程進行協作的示例。在這個示例中，新線程通過更改布爾值並通知條件變量來發送信號，而主線程則使用條件變量來等待信號。首先，它定義了一個元組 (Mutex<bool>, Condvar)，並使用 Arc（原子引用計數）將其包裝在一個可共享的指針中。這個指針有兩個副本，因此兩個線程都可以訪問這個元組。然後，它啟動了一個新的線程，並在這個線程內部使用互斥鎖來更改共享的布爾值。最後，它使用條件變量來等待這個布爾值被更改，然後退出循環。

信號量
~~~~~~~~~~~~~~~~~~~~~

信號量是操作系統中的一種同步原語，用於在多個線程或進程之間共享資源時進行互斥訪問。它通常是一個整數值，用於計數指定數量的資源可用。當一個線程需要使用資源時，它會執行信號量的 `acquire` 操作，如果信號量的值小於等於零，則線程將被掛起，（直到信號量的值變為正數，則會被喚醒）；否則將信號量的值減一，操作正常返回。另一方面，當一個線程完成使用資源後，它可以執行信號量的 `release` 操作，將信號量的值加一，並喚醒一個或所有掛起的線程。Rust 標準庫中沒有信號量類型，但我們可以用Mutex和Condvar來構造信號量類型。 

.. code-block:: Rust
    :linenos:

	use std::sync::{Condvar, Mutex};

	pub struct Semaphore {
		condvar: Condvar,
		counter: Mutex<isize>,
	}

	impl Semaphore {
		pub fn new(var: isize) -> Semaphore {
			Semaphore {
				condvar: Condvar::new(),
				counter: Mutex::new(var),
			}
		}
		pub fn acquire(&self) {
			// gain access to the atomic integer
			let mut count = self.counter.lock().unwrap();

			// wait so long as the value of the integer <= 0
			while *count <= 0 {
				count = self.condvar.wait(count).unwrap();
			}

			// decrement our count to indicate that we acquired
			// one of the resources
			*count -= 1;
		}
		pub fn release(&self) {
			// gain access to the atomic integer
			let mut count = self.counter.lock().unwrap();

			// increment its value
			*count += 1;

			// notify one of the waiting threads
			self.condvar.notify_one();
		}
	}


我們構造的 `Semaphore` 類型包含了三個方法：

- `new(var)` 方法創建一個信號量，並初始化信號量值 `counter`的為 `var`；
- `acquire()` 方法將信號量值減一，如果信號量的值已經為零，則線程通過條件變量 `condvar` 的 `wait` 操作將自己掛起；
- `release()` 方法將信號量值加一，並通過條件變量 `condvar` 的 `notify_one` 操作喚醒一個掛起線程。


有了信號量，我們就可以建立使用信號量的示例程序，該程序創建了三個線程，每個線程都會調用 acquire 方法獲取信號量，然後輸出一條消息，最後在信號量上調用 release 方法釋放信號量。


.. code-block:: Rust
    :linenos:

	use std::sync::Arc;
	use std::thread;
	fn main() {
		//let sem = Semaphore::new(1);
		// 創建信號量，並設置允許同時訪問的線程數為 2。
		let semaphore = Arc::new(Semaphore::new(2));

		// 創建三個線程。
		let threads = (0..3)
			.map(|i| {
				let semaphore = semaphore.clone();
				thread::spawn(move || {
					// 在信號量上調用 acquire 方法獲取信號量。
					semaphore.acquire();

					// 輸出消息。
					println!("Thread {}: acquired semaphore", i);

					// 模擬執行耗時操作。
					thread::sleep(std::time::Duration::from_secs(1));

					// 在信號量上調用 release 方法釋放信號量。
					println!("Thread {}: releasing semaphore", i);
					semaphore.release();
				})
			})
			.collect::<Vec<_>>();

		// 等待所有線程完成。
		for thread in threads {
			thread.join().unwrap();
		}
	}


這段代碼創建了一個名為 `semaphore` 的信號量，並設置允許併發操作的線程數為 2。然後創建了三個線程，在每個線程中，首先調用信號量的 `acquire`` 方法來嘗試獲取信號量。如果獲取了信號量，就可以輸出一條消息，並模擬執行一些耗時操作，最後調用信號量的 `release` 方法來釋放信號量，從而讓其他線程有機會獲取信號量並繼續執行。該示例運行的結果如下所示：

.. code-block:: console

	Thread 0: acquired semaphore
	Thread 1: acquired semaphore
	Thread 0: releasing semaphore
	Thread 1: releasing semaphore
	Thread 2: acquired semaphore
	Thread 2: releasing semaphore


上述的示例都是在用戶態實現的應用程序，其中的Thread、Mutex和Condvar需要應用程序所在的操作系統（這裡就是Linux）提供相應的支持。在本章中，我們會在自己寫的操作系統中實現Thread、Mutex、Condvar和Semaphore 機制，從而對同步互斥的原理有更加深入的瞭解，對應操作系統如何支持這些同步互斥底層機制有全面的掌握。

實踐體驗
-----------------------------------------

獲取本章代碼：

.. code-block:: console

   $ git clone https://github.com/rcore-os/rCore-Tutorial-v3.git
   $ cd rCore-Tutorial-v3
   $ git checkout ch8

在 qemu 模擬器上運行本章代碼：

.. code-block:: console

   $ cd os
   $ make run

內核初始化完成之後就會進入shell程序，我們可以體會一下線程的創建和執行過程。在這裡我們運行一下本章的測例 ``threads`` ：

.. code-block::

	>> threads
	aaa....bbb...ccc...
	thread#1 exited with code 1
	thread#2 exited with code 2
	thread#3 exited with code 3
	main thread exited.
	Shell: Process 2 exited with code 0
	>> 

它會有4個線程在執行，等前3個線程執行完畢後，主線程退出，導致整個進程退出。

此外，在本章的操作系統支持通過互斥來執行“哲學家就餐問題”這個應用程序：

.. code-block::

	>> phil_din_mutex
	time cost = 7273
	'-' -> THINKING; 'x' -> EATING; ' ' -> WAITING
	#0: -------                 xxxxxxxx----------       xxxx-----  xxxxxx--xxx
	#1: ---xxxxxx--      xxxxxxx----------    x---xxxxxx
	#2: -----          xx---------xx----xxxxxx------------        xxxx
	#3: -----xxxxxxxxxx------xxxxx--------    xxxxxx--   xxxxxxxxx
	#4: ------         x------          xxxxxx--    xxxxx------   xx
	#0: -------                 xxxxxxxx----------       xxxx-----  xxxxxx--xxx
	>>


我們可以看到5個代表“哲學家”的線程通過操作系統的 **Mutex** 互斥機制在進行“THINKING”、“EATING”、“WAITING”的日常生活。沒有哲學家由於拿不到筷子而飢餓，也沒有相鄰的兩個哲學家同時拿到同一個筷子。


.. note::

	**哲學家就餐問題** 　

	計算機科學家Dijkstra提出並解決的哲學家就餐問題是經典的進程同步互斥問題。哲學家就餐問題描述如下：

	有5個哲學家共用一張圓桌，分別坐在周圍的5張椅子上，在圓桌上有5個碗和5只筷子，他們的生活方式是交替地進行思考和進餐。平時，每個哲學家進行思考，飢餓時便試圖拿起其左右最靠近他的筷子，只有在他拿到兩隻筷子時才能進餐。進餐完畢，放下筷子繼續思考。


本章代碼樹
-----------------------------------------
達科塔盜龍操作系統 -- Thread&Coroutine OS的總體結構如下圖所示：

.. image:: ../../os-lectures/lec11/figs/thread-coroutine-os-detail.png
   :align: center
   :scale: 20 %
   :name: thread-coroutine-os-detail
   :alt: 達科塔盜龍操作系統 -- Thread&Coroutine OS總體結構

從上圖中可以看到，Thread&Coroutine OS 增加了在用戶態管理的用戶態線程/用戶態協程，以及在內核態管理的用戶態線程。對於用戶態管理的用戶態線程和協程，新增了一個運行在用戶態的 `Thread/Coroutine Manager` 運行時庫（Runtime Lib），這個不需要改動操作系統內核。 而對於內核態管理的用戶態線程，則需要新增線程控制塊（Thread Control Block, TCB）結構，把之前進程控制塊（Process Control Block, PCB）中與執行相關的內容剝離給了線程控制塊。同時，進一步重構進程控制塊，把線程控制塊列表作為進程控制塊中的一部分資源，這樣一個進程控制塊就可以管理多個線程了。最後還提供與線程相關的系統調用，如創建線程、等待線程結束等，以支持多線程應用的執行。

這裡，我們可以把進程、線程和協程中的控制流執行看出是一種任務（Task）的執行過程，如下圖所示：

.. image:: ../../os-lectures/lec11/figs/task-abstracts.png
   :align: center
   :scale: 10 %
   :name: task-abstracts
   :alt: 進程、線程和協程中的控制流抽象--任務（Task）

在上圖中，可以看出進程包含線程（即有棧協程），線程包含無棧協程，形成一個層次包含關係。而與它們執行相關的重點是切換控制流，即任務切換，關鍵就是保存於恢復任務上下文，任務上下文的核心部分就是每個任務所分時共享的硬件寄存器內容。對於無棧協程，切換這些寄存器就夠了；對於擁有獨立棧的線程而言，還需進一步切換線程棧；如果是擁有獨立地址空間的進程而言，那還需進一步切換地址空間（即切換頁表）。


進一步增加了同步互斥機制的慈母龍操作系統 -- SyncMutexOS的總體結構如下圖所示：

.. image:: ../../os-lectures/lec12/figs/syncmutex-os-detail.png
   :align: center
   :scale: 20 %
   :name: ipc-os-detail
   :alt: 慈母龍操作系統 -- SyncMutexOS總體結構

在上圖中，可以看出在進程控制塊中，增加了互斥鎖（Mutex）、信號量（Semaphore）和條件變量（Condvar）這三種資源，並提供了與這三種同步互斥資源相關的系統調用。這樣多線程應用就可以使用這三種同步互斥機制來解決各種同步互斥問題，如生產者消費者問題、哲學家問題、讀者寫者問題等。


位於 ``ch8`` 分支上的慈母龍操作系統 -- SyncMutexOS的源代碼如下所示：

.. code-block::
   :linenos:

	.
	├── ...
	├── os
	│   ├── ...
	│   └── src
	│       ├── ...
	│       ├── sync (新增：同步互斥子模塊 sync)
	│       │   ├── mod.rs
	│       │   ├── condvar.rs（條件變量實現）
	│       │   ├── mutex.rs （互斥鎖實現）
	│       │   └── semaphore.rs （信號量實現） 
	│       ├── syscall
	│       │   ├── ...
	│       │   ├── mod.rs（增加與線程/同步互斥相關的系統調用定義）
	│       │   ├── sync.rs（增加與同步互斥相關的系統調用具體實現）
	│       │   └── thread.rs（增加與線程相關的系統調用具體實現）
	│       ├── task (重構進程管理子模塊，以支持線程)
	│       │   ├── ...
	│       │   ├── process.rs（包含線程控制塊的進程控制塊）
	│       │   └── task.rs（線程控制塊）
	│       ├── timer.rs （增加支持線程睡眠一段時間的功能）
	│       └── trap
	│           ├── context.rs
	│           ├── mod.rs
	│           └── trap.S
	└── user
	    ├── ...
		├── src
		│   ├── bin (新增各種多線程/協程/同步互斥測試用例)
		│   │   ├── ...
		│   │   ├── early_exit2.rs（多線程測例）
		│   │   ├── early_exit.rs（多線程測例）
		│   │   ├── eisenberg.rs （面向n個線程的Eisenberg&McGuire 軟件同步互斥示例）
		│   │   ├── mpsc_sem.rs（基於信號量的生產者消費者問題示例）
		│   │   ├── peterson.rs（面向2個線程的Peterson軟件同步互斥示例）
		│   │   ├── phil_din_mutex.rs（基於互斥鎖的哲學家就餐問題示例）
		│   │   ├── race_adder_arg.rs（具有競態條件錯誤情況的多線程累加計算示例）
		│   │   ├── race_adder_atomic.rs（基於原子變量的多線程累加計算示例）
		│   │   ├── race_adder_loop.rs（具有競態條件錯誤情況的多線程累加計算示例）
		│   │   ├── race_adder_mutex_blocking.rss（基於可睡眠互斥鎖的多線程累加計算示例）
		│   │   ├── race_adder_mutex_spin.rs（基於忙等互斥鎖的多線程累加計算示例）
		│   │   ├── race_adder.rs（具有競態條件錯誤情況的多線程累加計算示例）
		│   │   ├── stackful_coroutine.rs（用戶態多線程（有棧協程）管理運行時庫和多線程示例）
		│   │   ├── stackless_coroutine.rs（用戶態無棧協程管理運行時庫和多協程示例）
		│   │   ├── sync_sem.rs（基於信號量的多線程同步示例）
		│   │   ├── test_condvar.rs（基於條件變量和互斥鎖的多線程同步示例）
		│   │   ├── threads_arg.rs（帶參數的多線程示例）
		│   │   ├── threads.rs（無參數的多線程示例）
		│   │   └── usertests.rs（運行所有應用的示例）
		│   └── ...

本章代碼導讀
-----------------------------------------------------

在本章實現支持多線程的達科塔盜龍操作系統 -- Thread&Coroutine OS過程中，需要考慮如下一些關鍵點：線程的總體結構、管理線程執行的線程控制塊數據結構、以及對線程管理相關的重要函數：線程創建和線程切換。這些關鍵點既可以在用戶態實現，也可在內核態實現。


線程設計與實現
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在  :doc:`./1thread` 一節中講述了設計實現用戶態線程管理運行時庫的過程，這其實是第三章中 :ref:`任務切換的設計與實現 <term-task-switch-impl>` 和 :ref:`協作式調度 <term-coop-impl>` 的一種更簡單的用戶態實現。首先是要構建多線程的基本執行環境，即定義線程控制塊數據結構，包括線程執行狀態、線程執行上下文（使用的通用寄存器集合）等。然後是要實現線程創建和線程切換這兩個關鍵函數。這兩個函數的關鍵就是構建線程的上下文和切換線程的上下文。當線程啟動後，不會被搶佔，所以需要線程通過 `yield_task` 函數主動放棄處理器，從而把處理器控制權交還給用戶態線程管理運行時庫，讓其選擇其他處於就緒態的線程執行。

在  :doc:`./1thread-kernel` 一節中講述了在操作系統內部設計實現內核態線程管理的實現過程，這其實基於第三章中 :ref:`任務切換的設計與實現 <term-task-switch-impl>` 和 :ref:`搶佔式調度 <term-preempt-sched>` 的進一步改進實現。這涉及到對進程的重構，把以前的線程管理相關數據結構轉移到線程控制塊中，並把線程作為一種資源，放在進程控制塊中。這樣與線程相關的關鍵部分包括：

- 任務控制塊 TaskControlBlock ：表示線程的核心數據結構
- 任務管理器 TaskManager ：管理線程集合的核心數據結構
- 處理器管理結構 Processor ：用於線程調度，維護線程的處理器狀態
- 線程切換：涉及特權級切換和線程上下文切換

進程控制塊和線程控制塊的主要部分如下所示：

.. code-block:: Rust
    :linenos:

	// os/src/task/tasks.rs
	// 線程控制塊
	pub struct TaskControlBlock {
		pub process: Weak<ProcessControlBlock>, //線程所屬的進程控制塊
		pub kstack: KernelStack,//任務（線程）的內核棧
		inner: UPSafeCell<TaskControlBlockInner>,
	}
	pub struct TaskControlBlockInner {
		pub res: Option<TaskUserRes>,  //任務（線程）用戶態資源
		pub trap_cx_ppn: PhysPageNum,//trap上下文地址
		pub task_cx: TaskContext,//任務（線程）上下文
		pub task_status: TaskStatus,//任務（線程）狀態
		pub exit_code: Option<i32>,//任務（線程）退出碼
	}
	// os/src/task/process.rs
	// 進程控制塊
	pub struct ProcessControlBlock {
		pub pid: PidHandle,  //進程ID
		inner: UPSafeCell<ProcessControlBlockInner>,
	}
	pub struct ProcessControlBlockInner {
		pub tasks: Vec<Option<Arc<TaskControlBlock>>>, //線程控制塊列表
		...
	}

接下來就是相關的線程管理功能的設計與實現了。首先是線程創建，即當一個進程執行中發出系統調用 `sys_thread_create`` 後，操作系統就需要在當前進程控制塊中創建一個線程控制塊，並在線程控制塊中初始化各個成員變量，建立好進程和線程的關係等，關鍵要素包括：

- 線程的用戶態棧：確保在用戶態的線程能正常執行函數調用
- 線程的內核態棧：確保線程陷入內核後能正常執行函數調用
- 線程的跳板頁：確保線程能正確的進行用戶態<–>內核態切換
- 線程上下文：即線程用到的寄存器信息，用於線程切換

創建線程的主要代碼如下所示：

.. code-block:: Rust
    :linenos:

	pub fn sys_thread_create(entry: usize, arg: usize) -> isize {
		// 創建新線程
		let new_task = Arc::new(TaskControlBlock::new(...
		// 把線程加到就緒調度隊列中
		add_task(Arc::clone(&new_task));
		// 把線程控制塊加入到進程控制塊中
		let tasks = &mut process_inner.tasks;
		tasks[new_task_tid] = Some(Arc::clone(&new_task));
		//建立trap/task上下文
		*new_task_trap_cx = TrapContext::app_init_context(
			entry,
			new_task_res.ustack_top(),
			kernel_token(),
		... 

而關於線程切換和線程調度這兩部分在之前已經介紹過。線程切換與第三章中介紹的特權級上下文切換和任務上下文切換的設計與實現是一致的，線程執行中的調度切換過程與第六章中介紹的進程調度機制是一致的。這裡就不再進一步贅述了。

同步互斥機制的設計實現
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在實現支持同步互斥機制的慈母龍操作系統 -- SyncMutexOS中，包括三種同步互斥機制，在  :doc:`./2lock` 一節中講述了互斥鎖的設計與實現，在  :doc:`./3semaphore` 一節中講述了信號量的設計與實現，在  :doc:`./4condition-variable` 一節中講述了條件變量的設計與實現。無論哪種同步互斥機制，都需要確保操作系統任意搶佔線程，調度和切換線程的執行，都可以保證線程執行的互斥需求和同步需求，從而能夠得到可預測和可重現的共享資源訪問結果。這三種用於多線程的同步互斥機制所對應的內核數據結構都在進程控制塊中，以進程資源的形式存在。

.. code-block:: Rust
    :linenos:

	// 進程控制塊內部結構
	pub struct ProcessControlBlockInner {
		...
		pub mutex_list: Vec<Option<Arc<dyn Mutex>>>,     // 互斥鎖列表
		pub semaphore_list: Vec<Option<Arc<Semaphore>>>, // 信號量列表
		pub condvar_list: Vec<Option<Arc<Condvar>>>,     // 條件變量列表
	}

在互斥鎖的設計實現中，設計了一個更底層的 `UPSafeCell<T>` 類型，用於支持在單核處理器上安全地在線程間共享可變全局變量。這個類型大致結構如下所示：

.. code-block:: Rust
    :linenos:

	pub struct UPSafeCell<T> { //允許在單核上安全使用可變全局變量
		inner: RefCell<T>,  //提供內部可變性和運行時借用檢查
	}
	unsafe impl<T> Sync for UPSafeCell<T> {} //聲明支持全局變量安全地在線程間共享
	impl<T> UPSafeCell<T> {
		pub unsafe fn new(value: T) -> Self {
			Self { inner: RefCell::new(value) }
		}
		pub fn exclusive_access(&self) -> RefMut<'_, T> {
			self.inner.borrow_mut()  //得到它包裹的數據的獨佔訪問權
		}
	}

並基於此設計了 `Mutex` 互斥鎖類型，可進一步細化為忙等型互斥鎖和睡眠型互斥鎖，二者的大致結構如下所示：

.. code-block:: Rust
    :linenos:

	pub struct MutexSpin {
		locked: UPSafeCell<bool>,  //locked是被UPSafeCell包裹的布爾全局變量
	}
	pub struct MutexBlocking {
		inner: UPSafeCell<MutexBlockingInner>,
	}
	pub struct MutexBlockingInner {
		locked: bool,
		wait_queue: VecDeque<Arc<TaskControlBlock>>, //等待獲取鎖的線程等待隊列
	}

在上述代碼片段的第9行，可以看到掛在睡眠型互斥鎖上的線程，會被放入到互斥鎖的等待隊列 `wait_queue` 中。 `Mutex` 互斥鎖類型實現了 `lock` 和 `unlock` 兩個方法完成獲取鎖和釋放鎖操作。而系統調用 `sys_mutex_create` 、 `sys_mutex_lock` 、 `sys_mutex_unlock` 這幾個系統調用，是提供給多線程應用程序實現互斥鎖的創建、獲取鎖和釋放鎖的同步互斥操作。

信號量 `Semaphore` 類型的大致結構如下所示：

.. code-block:: Rust
    :linenos:

	pub struct Semaphore {
		pub inner: UPSafeCell<SemaphoreInner>, //UPSafeCell包裹的內部可變結構
	}

	pub struct SemaphoreInner {
		pub count: isize, //信號量的計數值
		pub wait_queue: VecDeque<Arc<TaskControlBlock>>, //信號量的等待隊列
	}

在上述代碼片段的第7行，可以看到掛在信號量上的線程，會被放入到信號量的等待隊列 `wait_queue` 中。信號量 `Semaphore` 類型實現了 `up` 和 `down` 兩個方法完成獲取獲取信號量和釋放信號量的操作。而系統調用 `sys_semaphore_create` 、 `sys_semaphore_up` 、 `sys_semaphore_down` 這幾個系統調用，是提供給多線程應用程序實現信號量的創建、獲取和釋放的同步互斥操作。


條件變量 `Condvar` 類型的大致結構如下所示：


.. code-block:: Rust
    :linenos:

	pub struct Condvar {
		pub inner: UPSafeCell<CondvarInner>, //UPSafeCell包裹的內部可變結構
	}

	pub struct CondvarInner {
		pub wait_queue: VecDeque<Arc<TaskControlBlock>>,//等待隊列
	}

在上述代碼片段的第6行，可以看到掛在條件變量上的線程，會被放入到條件變量的等待隊列 `wait_queue` 中。條件變量 `Condvar` 類型實現了 `wait` 和 `signal` 兩個方法完成獲取等待條件變量和通知信號量的操作。而系統調用 `sys_condvar_create` 、 `sys_condvar_wait` 、 `sys_condvar_signal` 這幾個系統調用，是提供給多線程應用程序實現條件變量的創建、等待和通知的同步互斥操作。	

同學可能會注意到，上述的睡眠型互斥鎖、信號量和條件變量的數據結構幾乎相同，都會把掛起的線程放到等待隊列中。但是它們的具體實現還是有區別的，這需要同學瞭解這三種同步互斥機制的操作原理，再看看它們的方法對的設計與實現：互斥鎖的lock和unlock、信號量的up和down、條件變量的wait和signal，就可以看到它們的具體區別了。
