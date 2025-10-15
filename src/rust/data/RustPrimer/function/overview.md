# 函數
  儘管rust是一門多範式的編程語言，但rust的編程風格是更偏向於函數式的，函數在rust中是“一等公民”——first-class type。這意味著，函數是可以作為數據在程序中進行傳遞，如：作為函數的參數。跟C、C++一樣，rust程序也有一個唯一的程序入口-main函數。rust的main函數形式如下：
  
  ```rust
fn main() {
  //statements
}
  ```
  
  rust使用 `fn` 關鍵字來聲明和定義函數，`fn` 關鍵字隔一個空格後跟函數名，函數名後跟著一個括號，函數參數定義在括號內。rust使用`snake_case`風格來命名函數，即所有字母小寫並使用下劃線類分隔單詞，如：`foo_bar`。如果函數有返回值，則在括號後面加上箭頭 __->__ ，在箭頭後加上返回值的類型。

  這一章我們將學習以下與函數相關的知識：
  1. [函數參數](arguement.md)
  2. [函數返回值](return_value.md)
  3. [語句和表達式](statement_expression.md)
  4. [高階函數](higher_order_function.md)

> ### 注：本章所有例子均在rustc1.4下編譯通過，且例子中說明的所有的編譯錯誤都是rustc1.4版本給出的。
