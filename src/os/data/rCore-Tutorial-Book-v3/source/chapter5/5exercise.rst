練習
==============================================

課後練習
-------------------------------

編程題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `*` 實現一個使用nice,fork,exec,spawn等與進程管理相關的系統調用的linux應用程序。
2. `*` 擴展操作系統內核，能夠顯示操作系統切換進程的過程。
3. `*` 請閱讀下列代碼，分析程序的輸出 ``A`` 的數量：( 已知 ``&&`` 的優先級比 ``||`` 高)

    .. code-block:: c

      int main() {
          fork() && fork() && fork() || fork() && fork() || fork() && fork();
          printf("A");
          return 0;
      }

    如果給出一個 ``&&`` ``||`` 的序列，如何設計一個程序來得到答案？
4. `**` 在本章操作系統中實現本章提出的某一種調度算法（RR調度除外）。
5. `***` 擴展操作系統內核，支持多核處理器。
6. `***` 擴展操作系統內核，支持在內核態響應並處理中斷。
 
問答題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `*` 如何查看Linux操作系統中的進程？
2. `*` 簡單描述一下進程的地址空間中有哪些數據和代碼。
3. `*` 進程控制塊保存哪些內容？
4. `*` 進程上下文切換需要保存哪些內容？
5. `**` fork 為什麼需要在父進程和子進程提供不同的返回值？
6. `**` fork + exec 的一個比較大的問題是 fork 之後的內存頁/文件等資源完全沒有使用就廢棄了，針對這一點，有什麼改進策略？
7. `**` 其實使用了6的策略之後，fork + exec 所帶來的無效資源的問題已經基本被解決了，但是近年來fork 還是在被不斷的批判，那麼到底是什麼正在"殺死"fork？可以參考 `論文 <https://www.microsoft.com/en-us/research/uploads/prod/2019/04/fork-hotos19.pdf>`_ 。
8. `**` 請閱讀下列代碼，並分析程序的輸出，假定不發生運行錯誤，不考慮行緩衝，不考慮中斷：

    .. code-block:: c

      int main(){
          int val = 2;

          printf("%d", 0);
          int pid = fork();
          if (pid == 0) {
              val++;
              printf("%d", val);
          } else {
              val--;
              printf("%d", val);
              wait(NULL);
          }
          val++;
          printf("%d", val);
          return 0;
      }

    如果 fork() 之後主程序先運行，則結果如何？如果 fork() 之後 child 先運行，則結果如何？
9. `**` 為什麼子進程退出後需要父進程對它進行 wait，它才能被完全回收？
10. `**` 有哪些可能的時機導致進程切換？
11. `**` 請描述在本章操作系統中實現本章提出的某一種調度算法（RR調度除外）的簡要實現步驟。
12.  `*` 非搶佔式的調度算法，以及搶佔式的調度算法，他們的優點各是什麼？
13. `**` 假設我們簡單的將進程分為兩種：前臺交互（要求短時延）、後臺計算（計算量大）。下列進程/或進程組分別是前臺還是後臺？a) make 編譯 linux; b) vim 光標移動; c) firefox 下載影片; d) 某遊戲處理玩家點擊鼠標開槍; e) 播放交響樂歌曲; f) 轉碼一個電影視頻。除此以外，想想你日常應用程序的運行，它們哪些是前臺，哪些是後臺的？
14. `**` RR 算法的時間片長短對系統性能指標有什麼影響？
15. `**` MLFQ 算法並不公平，惡意的用戶程序可以愚弄 MLFQ 算法，大幅擠佔其他進程的時間。（MLFQ 的規則：“如果一個進程，時間片用完了它還在執行用戶計算，那麼 MLFQ 下調它的優先級”）你能舉出一個例子，使得你的用戶程序能夠擠佔其他進程的時間嗎？
16. `***` 多核執行和調度引入了哪些新的問題和挑戰？

實驗練習1
-------------------------------

實驗練習包括實踐作業和問答作業兩部分。實驗練習1和實驗練習2可以選一個完成。

實踐作業
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

進程創建
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

大家一定好奇過為啥進程創建要用 fork + execve 這麼一個奇怪的系統調用，就不能直接搞一個新進程嗎？思而不學則殆，我們就來試一試！這章的編程練習請大家實現一個完全 DIY 的系統調用 spawn，用以創建一個新進程。

spawn 系統調用定義( `標準spawn看這裡 <https://man7.org/linux/man-pages/man3/posix_spawn.3.html>`_ )：

.. code-block:: rust

    fn sys_spawn(path: *const u8) -> isize

- syscall ID: 400
- 功能：新建子進程，使其執行目標程序。 
- 說明：成功返回子進程id，否則返回 -1。  
- 可能的錯誤： 
    - 無效的文件名。
    - 進程池滿/內存不足等資源錯誤。  

TIPS：雖然測例很簡單，但提醒讀者 spawn **不必** 像 fork 一樣複製父進程的地址空間。

實驗要求
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- 實現分支：ch5-lab
- 實驗目錄要求不變
- 通過所有測例

  在 os 目錄下 ``make run TEST=1`` 加載所有測例， ``test_usertest`` 打包了所有你需要通過的測例，你也可以通過修改這個文件調整本地測試的內容。

challenge: 支持多核。

問答作業
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(1) fork + exec 的一個比較大的問題是 fork 之後的內存頁/文件等資源完全沒有使用就廢棄了，針對這一點，有什麼改進策略？

(2) [選做，不佔分]其實使用了題(1)的策略之後，fork + exec 所帶來的無效資源的問題已經基本被解決了，但是近年來 fork 還是在被不斷的批判，那麼到底是什麼正在"殺死"fork？可以參考 `論文 <https://www.microsoft.com/en-us/research/uploads/prod/2019/04/fork-hotos19.pdf>`_ 。

(3) 請閱讀下列代碼，並分析程序的輸出，假定不發生運行錯誤，不考慮行緩衝：
    
    .. code-block:: c 

      int main(){
          int val = 2;
          
          printf("%d", 0);
          int pid = fork();
          if (pid == 0) {
              val++;
              printf("%d", val);
          } else {
              val--;
              printf("%d", val);
              wait(NULL);
          }
          val++;
          printf("%d", val);
          return 0;
      } 


    如果 fork() 之後主程序先運行，則結果如何？如果 fork() 之後 child 先運行，則結果如何？


(4) 請閱讀下列代碼，分析程序的輸出 ``A`` 的數量：( 已知 ``&&`` 的優先級比 ``||`` 高)

    .. code-block:: c 

      int main() {
          fork() && fork() && fork() || fork() && fork() || fork() && fork();
          printf("A");
          return 0; 
      }

    [選做，不佔分] 更進一步，如果給出一個 ``&&`` ``||`` 的序列，如何設計一個程序來得到答案？

實驗練習的提交報告要求
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* 簡單總結本次實驗與上個實驗相比你增加的東西。（控制在5行以內，不要貼代碼）
* 完成問答問題
* (optional) 你對本次實驗設計及難度的看法。



實驗練習2
--------------------------------------

實踐作業
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

stride 調度算法
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ch3 中我們實現的調度算法十分簡單。現在我們要為我們的 os 實現一種帶優先級的調度算法：stride 調度算法。

算法描述如下:

(1) 為每個進程設置一個當前 stride，表示該進程當前已經運行的“長度”。另外設置其對應的 pass 值（只與進程的優先權有關係），表示對應進程在調度後，stride 需要進行的累加值。

(2) 每次需要調度時，從當前 runnable 態的進程中選擇 stride 最小的進程調度。對於獲得調度的進程 P，將對應的 stride 加上其對應的步長 pass。

(3) 一個時間片後，回到上一步驟，重新調度當前 stride 最小的進程。

可以證明，如果令 P.pass = BigStride / P.priority 其中 P.priority 表示進程的優先權（大於 1），而 BigStride 表示一個預先定義的大常數，則該調度方案為每個進程分配的時間將與其優先級成正比。證明過程我們在這裡略去，有興趣的同學可以在網上查找相關資料。

其他實驗細節：

- stride 調度要求進程優先級 :math:`\geq 2`，所以設定進程優先級 :math:`\leq 1` 會導致錯誤。
- 進程初始 stride 設置為 0 即可。
- 進程初始優先級設置為 16。

為了實現該調度算法，內核還要增加 set_prio 系統調用

.. code-block:: rust
   
   // syscall ID：140
   // 設置當前進程優先級為 prio
   // 參數：prio 進程優先級，要求 prio >= 2
   // 返回值：如果輸入合法則返回 prio，否則返回 -1
   fn sys_set_priority(prio: isize) -> isize;

tips: 可以使用優先級隊列比較方便的實現 stride 算法，但是我們的實驗不考察效率，所以手寫一個簡單粗暴的也完全沒問題。

實驗要求
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- 完成分支: ch3-lab

- 實驗目錄要求不變

- 通過所有測例
  
  lab3 有 3 類測例，在 os 目錄下執行 ``make run TEST=1`` 檢查基本 ``sys_write`` 安全檢查的實現， ``make run TEST=2`` 檢查 ``set_priority`` 語義的正確性， ``make run TEST=3`` 檢查 stride 調度算法是否滿足公平性要求，
  六個子程序運行的次數應該大致與其優先級呈正比，測試通過標準是 :math:`\max{\frac{runtimes}{prio}}/ \min{\frac{runtimes}{prio}} < 1.5`.

challenge: 實現多核，可以並行調度。

實驗約定
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

在第三章的測試中，我們對於內核有如下僅僅為了測試方便的要求，請調整你的內核代碼來符合這些要求：

- 用戶棧大小必須為 4096，且按照 4096 字節對齊。這一規定可以在實驗4開始刪除，僅僅為通過 lab2 測例設置。

問答作業
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

stride 算法深入

    stride 算法原理非常簡單，但是有一個比較大的問題。例如兩個 pass = 10 的進程，使用 8bit 無符號整形儲存 stride， p1.stride = 255, p2.stride = 250，在 p2 執行一個時間片後，理論上下一次應該 p1 執行。

    - 實際情況是輪到 p1 執行嗎？為什麼？

    我們之前要求進程優先級 >= 2 其實就是為了解決這個問題。可以證明，**在不考慮溢出的情況下**, 在進程優先級全部 >= 2 的情況下，如果嚴格按照算法執行，那麼 STRIDE_MAX – STRIDE_MIN <= BigStride / 2。

    - 為什麼？嘗試簡單說明（傳達思想即可，不要求嚴格證明）。

    已知以上結論，**考慮溢出的情況下**，我們可以通過設計 Stride 的比較接口，結合 BinaryHeap 的 pop 接口可以很容易的找到真正最小的 Stride。
    
    - 請補全如下 ``partial_cmp`` 函數（假設永遠不會相等）。

    .. code-block:: rust

        use core::cmp::Ordering;

        struct Stride(u64);

        impl PartialOrd for Stride {
            fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                // ...
            }
        }

        impl PartialEq for Person {
            fn eq(&self, other: &Self) -> bool {
                false
            }
        }

    例如使用 8 bits 存儲 stride, BigStride = 255, 則:

    - (125 < 255) == false
    - (129 < 255) == true
    

實驗練習的提交報告要求
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- 簡單總結與上次實驗相比本次實驗你增加的東西（控制在5行以內，不要貼代碼）。
- 完成問答問題。
- (optional) 你對本次實驗設計及難度/工作量的看法，以及有哪些需要改進的地方，歡迎暢所欲言。

參考信息
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
如果有興趣進一步瞭解 stride 調度相關內容，可以嘗試看看：

- `作者 Carl A. Waldspurger 寫這個調度算法的原論文 <https://people.cs.umass.edu/~mcorner/courses/691J/papers/PS/waldspurger_stride/waldspurger95stride.pdf>`_
- `作者 Carl A. Waldspurger 的博士生答辯slide <http://www.waldspurger.org/carl/papers/phd-mit-slides.pdf>`_ 
- `南開大學實驗指導中對Stride算法的部分介紹 <https://nankai.gitbook.io/ucore-os-on-risc-v64/lab6/tiao-du-suan-fa-kuang-jia#stride-suan-fa>`_
- `NYU OS課關於Stride Scheduling的Slide <https://cs.nyu.edu/~rgrimm/teaching/sp08-os/stride.pdf>`_

如果有興趣進一步瞭解用戶態線程實現的相關內容，可以嘗試看看：

- `user-multitask in rv64 <https://github.com/chyyuu/os_kernel_lab/tree/v4-user-std-multitask>`_
- `綠色線程 in x86 <https://github.com/cfsamson/example-greenthreads>`_
- `x86版綠色線程的設計實現 <https://cfsamson.gitbook.io/green-threads-explained-in-200-lines-of-rust/>`_
- `用戶級多線程的切換原理 <https://blog.csdn.net/qq_31601743/article/details/97514081?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-1.control&dist_request_id=&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-1.control>`_
