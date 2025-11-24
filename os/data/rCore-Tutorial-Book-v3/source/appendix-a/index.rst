附錄 A：Rust 系統編程入門
=============================

.. toctree::
   :hidden:
   :maxdepth: 4


.. .. note::

..     **Rust 語法卡片：外部符號引用**

..     extern "C" 可以引用一個外部的 C 函數接口（這意味著調用它的時候要遵從目標平臺的 C 語言調用規範）。但我們這裡只是引用位置標誌
..     並將其轉成 usize 獲取它的地址。由此可以知道 ``.bss`` 段兩端的地址。

..     **Rust 語法卡片：迭代器與閉包**

..     代碼第 7 行用到了 Rust 的迭代器與閉包的語法，它們在很多情況下能夠提高開發效率。如同學感興趣的話也可以將其改寫為等價的 for 
..     循環實現。

.. .. _term-raw-pointer:
.. .. _term-dereference:
.. .. warning::

..     **Rust 語法卡片：Unsafe**

..     代碼第 8 行，我們將 ``.bss`` 段內的一個地址轉化為一個 **裸指針** (Raw Pointer)，並將它指向的值修改為 0。這在 C 語言中是
..     一種司空見慣的操作，但在 Rust 中我們需要將他包裹在 unsafe 塊中。這是因為，Rust 認為對於裸指針的 **解引用** (Dereference) 
..     是一種 unsafe 行為。

..     相比 C 語言，Rust 進行了更多的語義約束來保證安全性（內存安全/類型安全/併發安全），這在編譯期和運行期都有所體現。但在某些時候，
..     尤其是與底層硬件打交道的時候，在 Rust 的語義約束之內沒法滿足我們的需求，這個時候我們就需要將超出了 Rust 語義約束的行為包裹
..     在 unsafe 塊中，告知編譯器不需要對它進行完整的約束檢查，而是由程序員自己負責保證它的安全性。當代碼不能正常運行的時候，我們往往也是
..     最先去檢查 unsafe 塊中的代碼，因為它沒有受到編譯器的保護，出錯的概率更大。

..     C 語言中的指針相當於 Rust 中的裸指針，它無所不能但又太過於靈活，程序員對其不謹慎的使用常常會引起很多內存不安全問題，最常見的如
..     懸垂指針和多次回收的問題，Rust 編譯器沒法確認程序員對它的使用是否安全，因此將其劃到 unsafe Rust 的領域。在 safe Rust 中，我們
..     有引用 ``&/&mut`` 以及各種功能各異的智能指針 ``Box<T>/RefCell<T>/Rc<T>`` 可以使用，只要按照 Rust 的規則來使用它們便可藉助
..     編譯器在編譯期就解決很多潛在的內存不安全問題。

Rust編程相關
--------------------------------

- `OS Tutorial Summer of Code 2020：Rust系統編程入門指導 <https://github.com/rcore-os/rCore/wiki/os-tutorial-summer-of-code-2020#step-0-%E8%87%AA%E5%AD%A6rust%E7%BC%96%E7%A8%8B%E5%A4%A7%E7%BA%A67%E5%A4%A9>`_
- `Stanford 新開的一門很值得學習的 Rust 入門課程 <https://reberhardt.com/cs110l/spring-2020/>`_
- `一份簡單的 Rust 入門介紹 <https://zhuanlan.zhihu.com/p/298648575>`_
- `《RustOS Guide》中的 Rust 介紹部分 <https://simonkorl.gitbook.io/r-z-rustos-guide/dai-ma-zhi-qian/ex1>`_
- `一份簡單的Rust宏編程新手指南 <http://blog.hubwiz.com/2020/01/30/rust-macro/>`_


Rust系統編程pattern
---------------------------------

- `Arc<Mutex<_>> in Rust <https://aeshirey.github.io/code/2020/12/23/arc-mutex-in-rust.html>`_
- `Understanding Closures in Rust <https://medium.com/swlh/understanding-closures-in-rust-21f286ed1759>`_
- `Closures in Rust <https://zhauniarovich.com/post/2020/2020-12-closures-in-rust/>`_
