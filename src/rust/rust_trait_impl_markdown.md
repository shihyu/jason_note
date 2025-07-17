# Rust 中 `trait` 和 `impl` 的差異

## `trait` - 定義能力清單

`trait` 用來定義一組方法的簽名，像是「合約」或「介面」。

```rust
trait CanFly {
    fn fly(&self);        // 只定義方法簽名
    fn land(&self);       // 沒有具體實作
}
```

### 特點
- **定義**：宣告一組方法的簽名
- **用途**：像是「合約」或「介面」，規定什麼能力必須實作
- **內容**：通常只有方法簽名，不包含具體實作

## `impl` - 具體實作

`impl` 用來為特定的結構體實作 trait 的方法。

```rust
impl CanFly for Bird {
    fn fly(&self) {
        println!("用翅膀飛翔！");  // 具體的實作內容
    }
    fn land(&self) {
        println!("降落在樹上！");
    }
}
```

### 特點
- **實作**：為特定的結構體實作 trait 的方法
- **用途**：提供具體的功能代碼
- **內容**：包含完整的方法實作

## 簡單比喻

| 概念 | 比喻 | 說明 |
|------|------|------|
| **trait** | 「會飛的能力清單」 | 規定必須有 `fly()` 方法 |
| **impl** | 「具體怎麼飛」 | 鳥用翅膀飛、飛機用引擎飛 |

## 完整範例

```rust
// trait：定義能力
trait CanSwim {
    fn swim(&self);
}

// 不同的結構體
struct Fish;
struct Bird;

// impl：為 Fish 實作游泳能力
impl CanSwim for Fish {
    fn swim(&self) {
        println!("魚類用鰭游泳！");
    }
}

// impl：為 Bird 實作游泳能力
impl CanSwim for Bird {
    fn swim(&self) {
        println!("鳥類划水游泳！");
    }
}

fn main() {
    let fish = Fish;
    let bird = Bird;
    
    fish.swim();  // 魚類用鰭游泳！
    bird.swim();  // 鳥類划水游泳！
}
```

## 重點總結

> **`trait` 定義「要做什麼」，`impl` 定義「怎麼做」！**

- `trait` 就像是規格書，告訴你需要實作哪些功能
- `impl` 就像是實際的程式碼，告訴你這些功能具體如何運作

這樣的設計讓不同的類型可以用不同的方式實作相同的功能，提供了很大的靈活性。