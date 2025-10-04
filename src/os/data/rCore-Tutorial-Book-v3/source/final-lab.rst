綜合練習
================================================

.. _term-final-lab:

- 本節難度：**對OS的全局理解要求較高**。
- 實驗分為基礎作業實驗和擴展作業實驗(二選一)。

基礎作業
-------------------------------------------------

**在保持 syscall 數量和基本含義不變的情況下，通過對 OS 內部的改進，提升 OS 的質量**。

同學們通過獨立完成前面的實驗後，應該對於操作系統的核心關鍵機制有了較好的瞭解，並知道如何形成一個有進程 / 地址空間 / 文件核心概念的基本功能 OS。但同學自制的 OS 可能還需進一步完善，才能在功能 / 性能 / 可靠性上進一步進化，以使得測試用例的正常運行。

綜合實驗的目的是希望同學們能夠在完成前面實驗的基礎上，站在全局視角，分析之前的測試用例(沒增加新的 syscall 訪問，只是更加全面和深入地測試操作系統的質量和能力)的運行情況，分析和理解自己寫的 OS 是否能比較好地滿足應用需求？如果不滿足應用需求，或者應用導致系統緩慢甚至崩潰，那原因出在哪裡？應該如何修改？修改後的 OS 是否更加完善還是缺陷更多？

實驗要求
+++++++++++++++++++++++++++++++++++++++++++++++++++++

- 實現分支：final。
- 運行 `final測例 <https://github.com/DeathWish5/rCore_tutorial_tests>`_ ，觀察並分析部分測試用例對 OS 造成的不良影響。
- 結合你學到的操作系統課程知識和你的操作系統具體實踐情況，分析你寫的 OS 對 測試用例中 的 app 支持不好的原因，比如：為何沒運行通過，為何死在某處了，為何系統崩潰，為何系統非常緩慢。分析可能的解決方法。(2~4 個，4 個合理的分析就可得到滿分，超過 4 個不額外得分)。
- 更進一步完成編程實現，使其可以通過一些原本 fail 的測例。(1～2 個，超過 2 個不額外得分)。

報告要求
+++++++++++++++++++++++++++++++++++++++++++++++++++++

- 對於失敗測例的現象觀察，原因分析，並提出可能的解決思路(2~4個)。
- 編程實現的具體內容，不需要貼出全部代碼，重要的是描述清楚自己的思路和做法(1~2個)。
- (optional)你對本次實驗的其他看法。

其他說明
+++++++++++++++++++++++++++++++++++++++++++++++++++++

- 注意：編程實現部分的底線是 OS 不崩潰，如果你解決不了問題，就解決出問題的進程。可以通過簡單殺死進程方式保證OS不會死掉。比如不支持某種 corner case，就把觸發該 case 的進程殺掉，如果是這樣，至少完成兩個。會根據報告綜合給分。
- 有些測例屬於非法程序，比如申請過量內存，對於這些程序，殺死進程其實就是正確的做法。參考: `OOM killer <https://docs.memset.com/other/linux-s-oom-process-killer>`_ 。
- 不一定所有的測例都會導致自己實現的 OS 崩潰，與語言和實現都有關係，選擇出問題的測例分析即可。對於沒有出錯的測例，可以選擇性分析自己的 OS 是如何預防這些"刁鑽"測例的。對於測例沒有測到的，也可以分析自己覺得安全 / 高效的實現，只要分析合理及給分。
- 鼓勵針對有趣的測例進行分析！開放思考！

.. note::

    1. **本次實驗的分值與之前 lab 相同，截至是時間為 15 週週末，基礎實驗屬於必做實驗(除非你選擇做擴展作業來代替基礎作業)**。

    2. 在測例中有簡明描述：想測試OS哪方面的質量。同學請量力而行，推薦不要超過上述上限。咱們不要卷。

    3. 對於有特殊要求的同學(比如你覺得上面的實驗太難)，可單獨找助教或老師說出你感興趣或力所能及的實驗內容，得到老師和助教同意後，做你提出的實驗。

    4. **歡迎同學們貢獻新測例，有意義測例經過助教檢查可以寫進報告充當工作量，歡迎打掉框架代碼OS，也歡迎打掉其他同學的OS**。

實驗檢查
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

- 實驗目錄要求

    目錄要求不變（參考 lab1 目錄或者示例代碼目錄結構）。同樣在 os 目錄下 `make run` 之後可以正確加載用戶程序並執行。

    加載的用戶測例位置： `../user/build/elf`。

- 檢查

    可以正確 `make run` 執行，可以正確執行目標用戶測例，並得到預期輸出(詳見測例註釋)。


問答作業
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

無

.. _term-chapter8-extended-exercise:

拓展作業(可選)
-------------------------------------------------

給部分同學不同的OS設計與實現的實驗選擇。擴展作業選項(1-14)基於 之前的OS來實現，擴展作業選項(15)是發現目標內核(ucore / rcore os)漏洞。可選內容(有大致難度估計)如下：

1. 實現多核支持，設計多核相關測試用例，並通過已有和新的測試用例(難度：8)
   
   * 某學長的有bug的rcore tutorial參考實現 `https://github.com/xy-plus/rCore-Tutorial-v3/tree/ch7 <https://github.com/xy-plus/rCore-Tutorial-v3/tree/ch7?fileGuid=gXqmevn42YSgQpqo>`_ 

2. 實現slab內存分配算法，通過相關測試用例(難度：7)

   * `https://github.com/tokio-rs/slab <https://github.com/tokio-rs/slab?fileGuid=gXqmevn42YSgQpqo>`_ 

3. 實現新的調度算法，如 CFS、BFS 等，通過相關測試用例(難度：7)
   
   * `https://en.wikipedia.org/wiki/Completely_Fair_Scheduler <https://en.wikipedia.org/wiki/Completely_Fair_Scheduler?fileGuid=gXqmevn42YSgQpqo>`_ 
   * `https://www.kernel.org/doc/html/latest/scheduler/sched-design-CFS.html <https://www.kernel.org/doc/html/latest/scheduler/sched-design-CFS.html?fileGuid=gXqmevn42YSgQpqo>`_ 

4. 實現某種 IO buffer 緩存替換算法，如2Q， LRU-K，LIRS等，通過相關測試用例(難度：6)
   
   * `LIRS: http://web.cse.ohio-state.edu/~zhang.574/lirs-sigmetrics-02.html <http://web.cse.ohio-state.edu/~zhang.574/lirs-sigmetrics-02.html?fileGuid=gXqmevn42YSgQpqo>`_ 
   * `2Q: https://nyuscholars.nyu.edu/en/publications/2q-a-low-overhead-high-performance-buffer-replacement-algorithm <https://nyuscholars.nyu.edu/en/publications/2q-a-low-overhead-high-performance-buffer-replacement-algorithm?fileGuid=gXqmevn42YSgQpqo>`_ 
   * `LRU-K: https://dl.acm.org/doi/10.1145/170036.170081 <https://dl.acm.org/doi/10.1145/170036.170081?fileGuid=gXqmevn42YSgQpqo>`_ 

5. 實現某種頁替換算法，如Clock， 二次機會算法等，通過相關測試用例(難度：6)

6. 實現支持日誌機制的可靠文件系統，可參考OSTEP教材中對日誌文件系統的描述(難度：7)

7. 支持virtio disk的中斷機制，提高IO性能(難度：4)
   
   * `chapter8 https://github.com/rcore-os/rCore-Tutorial-Book-v3/tree/chy <https://github.com/rcore-os/rCore-Tutorial-Book-v3/tree/chy?fileGuid=gXqmevn42YSgQpqo>`_ 
   * `https://github.com/rcore-os/virtio-drivers <https://github.com/rcore-os/virtio-drivers?fileGuid=gXqmevn42YSgQpqo>`_ 
   * `https://github.com/belowthetree/TisuOS <https://github.com/belowthetree/TisuOS?fileGuid=gXqmevn42YSgQpqo>`_ 

8. 支持 virtio framebuffer /鍵盤/鼠標處理，給出demo(推薦類似 pong 的 graphic game)的測試用例(難度：6)
   
   * code: `https://github.com/sgmarz/osblog/tree/pong <https://github.com/sgmarz/osblog/tree/pong?fileGuid=gXqmevn42YSgQpqo>`_ 
   * code: `https://github.com/belowthetree/TisuOS <https://github.com/belowthetree/TisuOS?fileGuid=gXqmevn42YSgQpqo>`_ 
   * `tutorial doc: Talking with our new Operating System by Handling Input Events and Devices <https://blog.stephenmarz.com/2020/08/03/risc-v-os-using-rust-input-devices/?fileGuid=gXqmevn42YSgQpqo>`_ 
   * `tutorial doc: Getting Graphical Output from our Custom RISC-V Operating System in Rust <https://blog.stephenmarz.com/2020/11/11/risc-v-os-using-rust-graphics/?fileGuid=gXqmevn42YSgQpqo>`_ 
   * `tutorial doc: Writing Pong Game in Rust for my OS Written in Rust <https://blog.stephenmarz.com/category/os/?fileGuid=gXqmevn42YSgQpqo>`_ 

9. 支持virtio NIC，給出測試用例(難度：7)
   
   * `https://github.com/rcore-os/virtio-drivers <https://github.com/rcore-os/virtio-drivers?fileGuid=gXqmevn42YSgQpqo>`_ 

10. 支持 virtio fs or其他virtio虛擬外設，通過測試用例(難度：5)
    
    * `https://docs.oasis-open.org/virtio/virtio/v1.1/csprd01/virtio-v1.1-csprd01.html <https://docs.oasis-open.org/virtio/virtio/v1.1/csprd01/virtio-v1.1-csprd01.html?fileGuid=gXqmevn42YSgQpqo>`_ 

11. 支持 `testsuits for kernel <https://gitee.com/oscomp/testsuits-for-oskernel#testsuits-for-os-kernel?fileGuid=gXqmevn42YSgQpqo>`_ 中15個以上的syscall，通過相關測試用例(難度：6)
    
    * 大部分與我們實驗涉及的 syscall 類似
    * `https://gitee.com/oscomp/testsuits-for-oskernel#testsuits-for-os-kernel <https://gitee.com/oscomp/testsuits-for-oskernel#testsuits-for-os-kernel?fileGuid=gXqmevn42YSgQpqo>`_ 

12. 支持新文件系統，比如 fat32 或 ext2 等，通過相關測試用例(難度：7)
    
    * `https://github.com/rafalh/rust-fatfs <https://github.com/rafalh/rust-fatfs?fileGuid=gXqmevn42YSgQpqo>`_ 
    * `https://github.com/pi-pi3/ext2-rs <https://github.com/pi-pi3/ext2-rs?fileGuid=gXqmevn42YSgQpqo>`_ 

13. 支持物理硬件(如全志哪吒開發板，K210開發板等)。(難度：7)
    
    * 可找老師要物理硬件開發板和相關開發資料

14. 支持其他處理器(如鯤鵬 ARM64、x64 架構等)。(難度：7)
    
    * 可基於 QEMU 來開發
    * 可找老師要基於其他處理器的物理硬件開發板（如樹莓派等）和相關開發資料


15. 對fork/exec/spawn等進行擴展，並改進shell程序，實現“|”這種經典的管道機制。(難度：4)
    
    * 參考 rcore tutorial 文檔中 chapter7 中內容

16. 向實驗用操作系統發起 fuzzing 攻擊(難度：6)
    
    * 其實助教或老師寫出的OS kernel也是漏洞百出，不堪一擊。我們缺少的僅僅是一個可以方便發現bug的工具。也許同學們能寫出或改造出一個os kernel fuzzing工具來發現並crash它/它們。下面的僅僅是參考，應該還不能直接用，也許能給你一些啟發。
    * `gustave fuzzer for os kernel tutorial <https://github.com/airbus-seclab/gustave/blob/master/doc/tutorial.md?fileGuid=gXqmevn42YSgQpqo>`_ 
    * `gustave fuzzer project <https://github.com/airbus-seclab/gustave?fileGuid=gXqmevn42YSgQpqo>`_ 
    * `paper:  GUSTAVE: Fuzzing OS kernels like simple applications <https://airbus-seclab.github.io/GUSTAVE_thcon/GUSTAVE_thcon.pdf?fileGuid=gXqmevn42YSgQpqo>`_ 

17. **學生自己的想法，但需要告知老師或助教，並得到同意。**

.. note::

    1. 支持 1~3 人組隊，如果確定並組隊完成，請在截止期前通過電子郵件告知助教。成員的具體得分可能會通過與老師和助教的當面交流綜合判斷給出。儘量減少划水與抱大腿。

    2. 根據老師和助教的評價，可獲得額外得分，但不會超過實驗 的滿分(30分)。也就是如果前面實驗有失分，可以通過一個簡單擴展把這部分分數拿回來。

其他說明
+++++++++++++++++++++++++++++++++++++++++++++++++++++

- 不能抄襲其他上課同學的作業，查出後，**所有實驗成績清零**。
- final 擴展作業可代替 final 基礎作業。拓展實驗給分要求會遠低於大實驗，簡單的拓展也可以的得到較高的評價。在完成代碼的同時，也要求寫出有關設計思路，問題及解決方法，實驗分析等內容的實驗報告。
- 完成之前的編程作業也可得滿分。這個擴展作業不是必須要做的，是給有興趣但不想選擇大實驗的同學一個選擇。

實驗檢查
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

完成後當面交流。

問答作業
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

無