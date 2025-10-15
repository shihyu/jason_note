# FFI


FFI([Foreign Function Interface](https://en.wikipedia.org/wiki/Foreign_function_interface))是用來與其它語言交互的接口，在有些語言裡面稱為語言綁定(language bindings)，Java 裡面一般稱為 JNI(Java Native Interface) 或 JNA(Java Native Access)。由於現實中很多程序是由不同編程語言寫的，必然會涉及到跨語言調用，比如 A 語言寫的函數如果想在 B 語言裡面調用，這時一般有兩種解決方案：一種是將函數做成一個服務，通過進程間通信([IPC](https://en.wikipedia.org/wiki/Inter-process_communication))或網絡協議通信([RPC](https://en.wikipedia.org/wiki/Remote_procedure_call), [RESTful](https://en.wikipedia.org/wiki/Representational_state_transfer)等)；另一種就是直接通過 FFI 調用。前者需要至少兩個獨立的進程才能實現，而後者直接將其它語言的接口內嵌到本語言中，所以調用效率比前者高。

當前的系統編程領域大部分被 C/C++ 佔領，而 Rust 定位為系統編程語言，少不了與現有的 C/C++ 代碼交互，另外為了給那些"慢"腳本語言調用，Rust 必然得對 FFI 有完善的支持，本章我們就來談談 Rust 的 FFI 系統。
