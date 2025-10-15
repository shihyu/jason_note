# AsRef 和 AsMut

`std::convert` 下面，還有另外兩個 Trait，`AsRef/AsMut`，它們功能是配合泛型，在執行引用操作的時候，進行自動類型轉換。這能夠使一些場景的代碼實現得清晰漂亮，大家方便開發。

## AsRef<T>

`AsRef` 提供了一個方法 `.as_ref()`。

對於一個類型為 `T` 的對象 `foo`，如果 `T` 實現了 `AsRef<U>`，那麼，`foo` 可執行 `.as_ref()` 操作，即 `foo.as_ref()`。操作的結果，我們得到了一個類型為 `&U` 的新引用。

注：

1. 與 `Into<T>` 不同的是，`AsRef<T>` 只是類型轉換，`foo` 對象本身沒有被消耗；
2. `T: AsRef<U>` 中的 `T`，可以接受 資源擁有者（owned）類型，共享引用（shared referrence）類型 ，可變引用（mutable referrence）類型。

下面舉個簡單的例子：

```rust
fn is_hello<T: AsRef<str>>(s: T) {
   assert_eq!("hello", s.as_ref());
}

let s = "hello";
is_hello(s);

let s = "hello".to_string();
is_hello(s);
```

因為 `String` 和 `&str` 都實現了 `AsRef<str>`。


## AsMut<T>

`AsMut<T>` 提供了一個方法 `.as_mut()`。它是 `AsRef<T>` 的可變（mutable）引用版本。

對於一個類型為 `T` 的對象 `foo`，如果 `T` 實現了 `AsMut<U>`，那麼，`foo` 可執行 `.as_mut()` 操作，即 `foo.as_mut()`。操作的結果，我們得到了一個類型為 `&mut U` 的可變（mutable）引用。

注：在轉換的過程中，`foo` 會被可變（mutable）借用。
