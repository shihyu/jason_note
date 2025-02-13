# Rust的特點

Rust是一種系統程式設計語言，Rust提供以下功能：

- 零成本抽象
- 錯誤訊息
- 移動語意
- 沒有資料競爭的執行緒
- 模式匹配
- 保證記憶體安全
- 高效的C繫結
- 安全的記憶體空間分配
- 最少的時間

#### 1.零成本抽象

在Rust中，可以新增抽象而不會影響程式碼的執行時效能。它提高了程式碼品質和程式碼的可讀性，而無需任何執行時效能成本。

#### 2.錯誤訊息

在C++程式設計中，與GCC相比，錯誤訊息有了很好的改進。在清晰的情況下，Rust更進一步提高。錯誤訊息顯示為(格式，顏色)，並在程式中建議拼寫錯誤。

#### 3.型別推斷

Rust提供了型別推斷的功能，這意味著它可以自動確定表示式的型別。

#### 4.移動語意

Rust提供此功能，允許在源物件是臨時物件時，通過移動操作替換複製操作。

#### 5.沒有資料爭用的執行緒

資料爭用是兩個或多個執行緒存取同一記憶體位置的條件。由於所有權系統，Rust提供了沒有資料爭用的執行緒功能。所有權系統僅將不同物件的所有者傳輸到不同的執行緒，並且兩個執行緒永遠不能擁有具有寫存取許可權的相同變數。

#### 6.模式匹配

Rust提供了模式匹配的功能。在模式匹配中，Rust中的模式與'match'表示式一起使用，以更好地控制程式的控制流。以下是一些模式的組合：

- 字面量
- 陣列，列舉，結構或元組
- 變數
- 萬用字元
- 預留位置

#### 7.保證記憶體安全

Rust通過使用所有權的概念保證了記憶體安全。所有權是C語言的記憶體控制和java的垃圾收集之間的中間地帶。在Rust程式中，記憶體空間由變數擁有，並由其他變數暫時借用。這允許Rust在編譯時提供記憶體安全性，而不依賴於垃圾收集器。

#### 8.高效的C繫結

Rust提供了「高效C繫結」的功能，這意味著Rust語言能夠在與自身對話時與C語言進行互操作。Rust提供了一個「外部功能介面」來與C API進行通訊，並利用其所有權系統同時保證記憶體安全。

#### 9.安全的記憶體空間分配

在Rust中，記憶體管理是手動的，即程式員可以明確控制分配和釋放記憶體的位置和時間。在C語言中，使用 此運算子將智慧指標返回為 智慧指標是一種特殊的值，用於控制何時釋放物件。智慧指標是「智慧的」，因為它們不僅跟蹤物件的位置，而且還知道如何清理它。`malloc``~``int`
