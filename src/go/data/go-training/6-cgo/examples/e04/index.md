CGO 的 C 虛擬包提供了一組函數、用於 Go 語言和 C 語言之間數組和字符串的雙向轉換。

## 拷貝轉換
拷貝轉換的原理是通過克隆的方式在 Go 語言和 C 語言的環境之中拷貝數據。會涉及到內存分配和拷貝的開銷。

```cgo
C.CString(string) *C.char
```
輸入的 Go 字符串，克隆一個 C 語言格式的字符串；返回的字符串由 C 語言的 malloc 函數分配，不使用時需要通過 C 語言的 free 函數釋放。

```cgo
func C.CBytes([]byte) unsafe.Pointer
```
C.CBytes 函數的功能和 C.CString 類似，用於從輸入的 Go 語言字節切片克隆一個 C 語言版本的字節數組，同樣返回的數組需要在合適的時候釋放。

```cgo
func C.GoString(*C.char) string
```
C.GoString 用於將從 NULL 結尾的 C 語言字符串克隆一個 Go 語言字符串。

```cgo
func C.GoBytes(unsafe.Pointer, C.int) []byte
```
C.GoBytes 用於從 C 語言數組，克隆一個 Go 語言字節切片。

## Go訪問C語言，reflect包轉換
reflect 包提供了類型信息，可以在 Go 語言中直接訪問 C 語言的內存空間
這個訪問過程相當於指針類型強制轉換，沒有內存拷貝的開銷。
參見 main.go

## C訪問Go語言
在 C 語言中可以通過 GoString 和 GoSlice 來訪問 Go 語言的字符串和切片

