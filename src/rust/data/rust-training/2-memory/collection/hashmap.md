
## 基本用法
hashmap的基本用法

```
use std::collections::HashMap;
fn main() {
    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);
    println!("{:?}", scores);
}
```

輸出
```shell
{"Yellow": 50, "Blue": 10}
```

也可以使用兩個vec

```shell
use std::collections::HashMap;
fn main() {
    let teams = vec![String::from("Blue"), String::from("Yellow")];
    let initial_scores = vec![10, 50];
    let scores: HashMap<_, _> = teams.iter().zip(initial_scores.iter()).collect();
    println!("{:?}", scores);
}
```

### hashmap的所有權
當 country 被 insert 到 hashmap 時，它的所有權會轉移到 hashmap中。
如果我們想要在 hashmap 之外使用 country，需要使用引用。

```shell
use std::collections::HashMap;
fn main() {
    let country = String::from("China");
    let score = 100;

    let mut scores = HashMap::new();
    scores.insert(&country, score);
    println!("{:?}", country);
}
```

## 循環遍歷

```shell
use std::collections::HashMap;
fn main() {
    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);
    for (key, value) in &scores {
        println!("{}: {}", key, value);
    }
}
```

## 使用場景：使用hashmap統計字符串出現次數

```shell
use std::collections::HashMap;
fn main() {
    let text = "hello world wonderful world";
    let mut map = HashMap::new();
    for word in text.split_whitespace() {
        let count = map.entry(word).or_insert(0);
        *count += 1;
    }    
    println!("{:?}", map);    
}
```

```shell
{"wonderful": 1, "hello": 1, "world": 2}
```