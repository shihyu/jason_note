.. rCore-Tutorial-Book-v3 documentation master file, created by
   sphinx-quickstart on Thu Oct 29 22:25:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

rCore-Tutorial-Book 第三版
==================================================

.. toctree::
   :maxdepth: 2
   :caption: Part1 - Just do it!
   :hidden:
   
   chapter0/index
   chapter1/index
   chapter2/index
   chapter3/index
   chapter4/index
   chapter5/index
   chapter6/index
   chapter7/index
   chapter8/index
   chapter9/index

.. toctree::
   :maxdepth: 2
   :caption: Part2 - Do it better!
   :hidden:

.. toctree::
   :maxdepth: 2
   :caption: 附錄
   :hidden:

   final-lab
   appendix-a/index
   appendix-b/index
   appendix-c/index
   appendix-d/index
   appendix-e/index
   appendix-f/index
   terminology

.. toctree::
   :maxdepth: 2
   :caption: 開發註記
   :hidden:

   setup-sphinx
   rest-example
   log

歡迎來到 rCore-Tutorial-Book 第三版！

歡迎參加 `2022年開源操作系統訓練營! <https://learningos.github.io/rust-based-os-comp2022/>`_

.. note::

   :doc:`/log` 



項目簡介
---------------------

這本教程旨在一步一步展示如何 **從零開始** 用 **Rust** 語言寫一個基於 **RISC-V** 架構的 **類 Unix 內核** 。值得注意的是，本項目不僅支持模擬器環境（如 Qemu/terminus 等），還支持在真實硬件平臺 Kendryte K210 上運行（目前主要在 rCore-Tutorial-v3 倉庫的 `k210 <https://github.com/rcore-os/rCore-Tutorial-v3/tree/k210/>`_ 分支上維護）。

導讀
---------------------

請大家先閱讀 :ref:`第零章 <link-chapter0>` ，對於項目的開發背景和操作系統的概念有一個整體把控。
 
在正式進行實驗之前，請先按照第零章章末的 :doc:`/chapter0/5setup-devel-env` 中的說明完成環境配置，再從第一章開始閱讀正文。

.. chyyuu 如果已經對 RISC-V 架構、Rust 語言和內核的知識有較多瞭解，第零章章末的 :doc:`/chapter0/6hardware` 提供了我們採用的真實硬件平臺 Kendryte K210 的一些信息。

項目協作
----------------------

- :doc:`/setup-sphinx` 介紹瞭如何基於 Sphinx 框架配置文檔開發環境，之後可以本地構建並渲染 html 或其他格式的文檔；
- :doc:`/rest-example` 給出了目前編寫文檔才用的 ReStructuredText 標記語言的一些基礎語法及用例；
- `項目的源代碼倉庫 <https://github.com/rcore-os/rCore-Tutorial-v3>`_ && `文檔倉庫 <https://github.com/rcore-os/rCore-Tutorial-Book-v3>`_
- 時間倉促，本項目還有很多不完善之處，歡迎大家積極在每一個章節的評論區留言，或者提交 Issues 或 Pull Requests，讓我們一起努力讓這本書變得更好！
- 歡迎大家加入項目交流 QQ 群，群號：735045051

本項目與其他系列項目的聯繫
----------------------------------------------

隨著 rcore-os 開源社區的不斷發展，目前已經有諸多基於 Rust 語言的操作系統項目，這裡介紹一下這些項目之間的區別和聯繫，讓同學們對它們能有一個整體瞭解並避免混淆。

rcore-os 開源社區大致上可以分為兩類項目：即探索使用 Rust 語言構建 OS 的主幹項目，以及面向初學者的從零開始寫 OS 項目。它們都面向教學用途，但前一類項目參與的開發者更多、更為複雜、功能也更為完善，也會用到更多新的技術；而後一類項目則作為教程項目，儘可能保持簡單易懂，目的為向初學者演示如何從頭開始寫一個 OS 。

主幹項目按照時間順序有這些：最早的是用 Rust 語言實現 linux syscall 的 `rCore <https://github.com/rcore-os/rCore>`_ ，這也是 rcore-os 開源社區的第一個項目。接著，緊跟 Rust 異步編程的浪潮，誕生了使用 Rust 語言重寫 Google Fuchsia 操作系統的 Zircon 內核的 `zCore <https://github.com/rcore-os/zCore>`_ 項目，其中利用了大量 Rust 異步原語實現了超時取消等機制。最新的主幹項目則是探索 OS 模塊化架構的 `arceos <https://github.com/rcore-os/arceos>`_ 。

教程項目則分佈在 rcore-os 和 `LearningOS <https://github.com/LearningOS>`_ 兩個開源社區中。最早的第一版教程是 `rcore_step_by_step <https://github.com/LearningOS/rcore_step_by_step>`_ ，第二版教程是 `rCore_tutorial <https://github.com/rcore-os/rCore_tutorial>`_ ，第三版教程是 `rCore-Tutorial <https://github.com/rcore-os/rCore-Tutorial>`_ ，最新的教程（暫定 v3.6 版本）就是本項目 `rCore-Tutorial-v3 <https://github.com/rcore-os/rCore-Tutorial-v3>`_ 仍在持續更新中。

教程項目均以 rCore 為前綴，是因為它們都是主幹項目 `rCore <https://github.com/rcore-os/rCore>`_ 的簡化版。 "rCore" 這個詞在不同的語境中指代的具體項目也不一樣：如果在討論教程項目的語境，比如以 xv6 和 ucore 以及 ChCore 等項目類比的時候，那麼往往指的是最新的教程項目；相反如果討論的是大規模項目的話，應該指代 `rCore <https://github.com/rcore-os/rCore>`_ 或者其他主幹項目。由於教程項目是由 `rCore <https://github.com/rcore-os/rCore>`_ 簡化來的，所以“大rCore”指的是 `rCore <https://github.com/rcore-os/rCore>`_ 主幹項目，相對的 “小rCore/rCore教程”則指的是最新版的教程項目。

項目進度
-----------------------

- 2020-11-03：環境搭建完成，開始著手編寫文檔。
- 2020-11-13：第一章完成。
- 2020-11-27：第二章完成。
- 2020-12-20：前七章代碼完成。
- 2021-01-10：第三章完成。
- 2021-01-18：加入第零章。
- 2021-01-30：第四章完成。
- 2021-02-16：第五章完成。
- 2021-02-20：第六章完成。
- 2021-03-06：第七章完成。到這裡為止第一版初稿就已經完成了。
- 2021-10-20：第八章代碼於前段時間完成。開始更新前面章節文檔及完成第八章文檔。
- 2021-11-20：更新1~9章，添加第八章（同步互斥），原第八章（外設）改為第九章。
- 2022-01-02：第一章文檔更新完成。
- 2022-01-05：第二章文檔更新完成。
- 2022-01-06：第三章文檔更新完成。
- 2022-01-07：第四章文檔更新完成。
- 2022-01-09：第五章文檔更新完成。
