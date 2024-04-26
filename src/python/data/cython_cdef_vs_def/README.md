def – 普通的 Python 函數，只用 Python 編譯器
cdef – Cython 專用函數，不能透過純 Python 程式碼使用該函數，必須在 Cython 內使用
cpdef – C 語言和 Python 共用，可以透過 C 語言或者 Python 程式碼使用該函數
