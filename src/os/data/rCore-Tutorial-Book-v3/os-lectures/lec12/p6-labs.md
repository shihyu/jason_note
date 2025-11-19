---
marp: true
theme: default
paginate: true
_paginate: false
header: ''
footer: ''
backgroundColor: white
---

<!-- theme: gaia -->
<!-- _class: lead -->

# 第十二講 同步與互斥

## 第六節 支持同步互斥的OS(SMOS)


---
### 實踐：SMOS
- **進化目標**
- 總體思路
- 歷史背景
- 實踐步驟
- 程序設計

![bg right:65% 100%](figs/thread-coroutine-os-detail.png)


---
### 實踐：SMOS -- 以往目標
提高性能、簡化開發、加強安全、支持數據持久保存、支持應用的靈活性，支持進程間交互，支持線程和協程
- TCOS：支持線程和協程  ； IPC OS：進程間交互
- Filesystem OS：支持數據持久保存
- Process OS: 增強進程管理和資源管理
- Address Space OS: 隔離APP訪問的內存地址空間
- multiprog & time-sharing OS: 讓APP共享CPU資源
- BatchOS： 讓APP與OS隔離，加強系統安全，提高執行效率
- LibOS: 讓APP與HW隔離，簡化應用訪問硬件的難度和複雜性

---
### 實踐：SMOS -- 進化目標
在多線程中支持對共享資源的同步互斥訪問
- 互斥鎖機制
- 信號量機制
- 管程與條件變量機制


---
### 實踐：SMOS 
### 同學的進化目標
- 理解同步互斥的各種機制
- 理解用同步互斥機制解決同步互斥問題
- 會寫支持線程間同步互斥的OS


<!-- 慈母龍英文名(maiasaura)的含義是“好媽媽蜥蜴”。1979年在美國蒙大拿，科學家們發現了一些恐龍窩，其中有小恐龍的骨架。於是他們把這種恐龍命名為慈母龍。。 -->

![bg right 80%](figs/maiasaura.png)

---
### 實踐：SMOS
- 進化目標
- **總體思路**
    - **同步互斥**
- 歷史背景
- 實踐步驟
- 程序設計

![bg right:70% 100%](figs/syncmutex-os-key-structures.png)

---
### 實踐：SMOS
- 進化目標
- **總體思路**
    - **同步互斥**
- 歷史背景
- 實踐步驟
- 程序設計

![bg right:70% 100%](figs/syncmutex-os-detail.png)


---
### 實踐：SMOS
歷史背景
- 1963年前後，當時的數學家 Edsger Dijkstra和他的團隊正在為Electrologica X8計算機開發一個操作系統（THE多道程序系統）的過程中，提出了信號（Semaphore）是一種變量或抽象數據類型，用於控制多個線程對共同資源的訪問。
- Brinch Hansen(1973)和Hoare(1974)結合操作系統和Concurrent Pascal編程語言，提出了一種高級同步原語，稱為管程(monitor)。一個管程是一個由過程（procedures，Pascal語言的術語，即函數）、共享變量等組成的集合。線程可調用管程中的過程。

---
### 實踐步驟
```
git clone https://github.com/rcore-os/rCore-Tutorial-v3.git
cd rCore-Tutorial-v3
git checkout ch8
```
包含了多個同步互斥相關的多線程應用程序
```
user/src/bin/
├──  mpsc_sem.rs          # 基於信號量的生產者消費者問題
├──  phil_din_mutex.rs    # 基於互斥鎖的哲學家問題
├──  race_adder_*.rs      # 各種方式的全局變量累加問題
├──  sync_sem.rs          # 基於信號量的同步操作
├──  test_condvar.rs      # 基於條件變量的同步操作
```

---
### 實踐步驟
內核代碼的主要改進部分
```
os/src/
├── sync
│   ├── condvar.rs        //條件變量
│   ├── mod.rs 
│   ├── mutex.rs          //互斥鎖
│   ├── semaphore.rs      //信號量
│   └── up.rs
├── syscall
│   ├── sync.rs //增加了互斥鎖、信號量和條件變量相關係統調用
├── task
│   ├── process.rs //進程控制塊增加了互斥鎖、信號量和條件變量
├── timer.rs     // 添加與定時相關的TimerCondVar類條件變量
```

---
### 實踐步驟
比如執行哲學家問題的應用程序，展示了5個哲學家用5把叉子進行思考/進餐/休息的過程。
```
Rust user shell
>> phil_din_mutex
time cost = 7271
'-' -> THINKING; 'x' -> EATING; ' ' -> WAITING
#0: -------                 xxxxxxxx----------       xxxx-----  xxxxxx--xxx
#1: ---xxxxxx--      xxxxxxx----------    x---xxxxxx
#2: -----          xx---------xx----xxxxxx------------        xxxx
#3: -----xxxxxxxxxx------xxxxx--------    xxxxxx--   xxxxxxxxx
#4: ------         x------          xxxxxx--    xxxxx------   xx
#0: -------                 xxxxxxxx----------       xxxx-----  xxxxxx--xxx
>>
```

---
### 實踐步驟
全局變量累加問題的多線程應用 `race_adder.rs`
```
A           //全局變量 
A=A+1       //多個線程對A進行累加 
```
多個線程執行上述代碼，真的會出現Race Condition（競爭條件）嗎？

- 併發、無序的線程在使用有限、獨佔、不可搶佔的資源而產生矛盾稱為競爭（Race）
- 多個線程無序競爭不能被同時訪問的資源而出現執行出錯的問題，稱為競爭條件（Race Condition）

---
### 實踐步驟
全局變量累加問題的多線程應用 `race_adder.rs`
```rust
pub fn main() -> i32 {
    let start = get_time();
    let mut v = Vec::new();
    for _ in 0..THREAD_COUNT {
        v.push(thread_create(f as usize, 0) as usize);  // f函數是線程主體
    }
    let mut time_cost = Vec::new();
    for tid in v.iter() {
        time_cost.push(waittid(*tid));
    }
    println!("time cost is {}ms", get_time() - start);
    assert_eq!(unsafe { A }, PER_THREAD * THREAD_COUNT); //比較累計值A
    0
}
```


---
### 實踐步驟
全局變量累加問題的多線程應用 `race_adder.rs`
```rust
unsafe fn f() -> ! {
    let mut t = 2usize;
    for _ in 0..PER_THREAD {    
        let a = &mut A as *mut usize;    // “緩慢執行”A=A+1 
        let cur = a.read_volatile();     // “緩慢執行”A=A+1
        for _ in 0..500 {  t = t * t % 10007; } // 增加切換概率
        a.write_volatile(cur + 1);      // “緩慢執行”A=A+1
    }
    exit(t as i32)
}
```
---
### 實踐步驟
全局變量累加問題的多線程應用 `race_adder.rs`
```
>> race_adder
time cost is 31ms
Panicked at src/bin/race_adder.rs:40, assertion failed: `(left == right)`
  left: `15788`,
 right: `16000`
[kernel] Aborted, SIGABRT=6
```
每次都會執行都會出現Race Condition（競爭條件）！


---
### 實踐步驟
基於原子操作的全局變量累加問題的多線程應用 `race_adder_atomic.rs`
```rust
unsafe fn f() -> ! {
    for _ in 0..PER_THREAD {
        while OCCUPIED
            .compare_exchange(false, true, Ordering::Relaxed, Ordering::Relaxed)
            .is_err()  {  yield_(); }           // 基於CAS操作的近似spin lock操作
        let a = &mut A as *mut usize;           // “緩慢執行”A=A+1 
        let cur = a.read_volatile();            // “緩慢執行”A=A+1 
        for _ in 0..500 { t = t * t % 10007; }  // 增加切換概率
        a.write_volatile(cur + 1);              // “緩慢執行”A=A+1 
        OCCUPIED.store(false, Ordering::Relaxed);  // unlock操作
    }
    ...
```
---
### 實踐步驟
基於原子操作的全局變量累加問題的多線程應用 `race_adder_atomic.rs`

```
>> race_adder_atomic
time cost is 29ms
>> race_adder_loop
```
可以看到，執行速度快，且正確。

---
### 實踐步驟
基於互斥鎖的多線程應用 `race_adder_mutex_[spin|block]`
```rust
unsafe fn f() -> ! {
    let mut t = 2usize;
    for _ in 0..PER_THREAD {
        mutex_lock(0); //lock(id)
        let a = &mut A as *mut usize;   // “緩慢執行”A=A+1 
        let cur = a.read_volatile();    // “緩慢執行”A=A+1 
        for _ in 0..500 {  t = t * t % 10007; } // 增加切換概率
        a.write_volatile(cur + 1);      // “緩慢執行”A=A+1 
        mutex_unlock(0); //unlock(id)
    }
    exit(t as i32)
}
```
---
### 實踐步驟
基於互斥鎖的全局變量累加問題的多線程應用 `race_adder_mutex_spin`
```
>> race_adder_mutex_spin  
time cost is 249ms
# 執行系統調用，且進行在就緒隊列上的取出/插入/等待操作
```

基於互斥鎖的全局變量累加問題的多線程應用 `race_adder_mutex_block`
```
>> race_adder_mutex_blocking
time cost is 919ms  
# 執行系統調用，且進行在就緒隊列+等待隊列上的取出/插入/等待操作
```

---
###  程序設計
spin mutex和 block mutex 的核心數據結構： `UPSafeCell`
```rust
pub struct UPSafeCell<T> { //允許在單核上安全使用可變全局變量
    inner: RefCell<T>,  //提供內部可變性和運行時借用檢查
}
unsafe impl<T> Sync for UPSafeCell<T> {} //聲明支持全局變量安全地在線程間共享
impl<T> UPSafeCell<T> {
    pub unsafe fn new(value: T) -> Self {
        Self { inner: RefCell::new(value) }
    }
    pub fn exclusive_access(&self) -> RefMut<'_, T> {
        self.inner.borrow_mut()  //得到它包裹的數據的獨佔訪問權
    }
}
```

---
###  程序設計
spin mutex和 block mutex 的核心數據結構
```rust
pub struct MutexSpin {
    locked: UPSafeCell<bool>,  //locked是被UPSafeCell包裹的布爾全局變量
}
pub struct MutexBlocking {
    inner: UPSafeCell<MutexBlockingInner>,
}
pub struct MutexBlockingInner {
    locked: bool,
    wait_queue: VecDeque<Arc<TaskControlBlock>>, //等待獲取鎖的線程等待隊列
}
```


 ---
###  程序設計
spin mutex的相關函數
```rust
pub trait Mutex: Sync + Send { //Send表示跨線程 move，Sync表示跨線程share data
    fn lock(&self);
    fn unlock(&self);
}

    fn unlock(&self) {
        let mut locked = self.locked.exclusive_access(); //獨佔訪問locked
        *locked = false; //
    }
```

---
###  程序設計
spin mutex的相關函數
```rust
impl Mutex for MutexSpin {
    fn lock(&self) {
        loop {
            let mut locked = self.locked.exclusive_access(); //獨佔訪問locked
            if *locked {
                drop(locked);
                suspend_current_and_run_next(); //把當前線程放到就緒隊列末尾
                continue;
            } else {
                *locked = true; //得到鎖了，可以繼續進入臨界區執行
                return;
        ...
 ```   


---
###  程序設計
block mutex的相關函數
```rust
impl Mutex for MutexBlocking {
    fn lock(&self) {
        let mut mutex_inner = self.inner.exclusive_access(); //獨佔訪問mutex_inner
        if mutex_inner.locked {
            //把當前線程掛到此lock相關的等待隊列中
            mutex_inner.wait_queue.push_back(current_task().unwrap());
            drop(mutex_inner);
            //把當前線程從就緒隊列中取出，設置為阻塞態，切換到另一就緒線程執行
            block_current_and_run_next();
        } else {
            mutex_inner.locked = true; //得到鎖了，可以繼續進入臨界區執行
        }
    }
```


---
###  程序設計
block mutex的相關函數
```rust
    fn unlock(&self) {
        let mut mutex_inner = self.inner.exclusive_access();
        assert!(mutex_inner.locked);
        //從等待隊列中取出線程，並放入到就緒隊列中
        if let Some(waking_task) = mutex_inner.wait_queue.pop_front() {
            add_task(waking_task); 
        } else {
            mutex_inner.locked = false; //釋放鎖
        }
    }
```
---
### 實踐步驟
基於信號量的多線程應用 `sync_sem`
```rust
pub fn main() -> i32 {
    // create semaphores
    assert_eq!(semaphore_create(0) as usize, SEM_SYNC);
    // create threads
    let threads = vec![
        thread_create(first as usize, 0),
        thread_create(second as usize, 0),
    ];
    // wait for all threads to complete
    for thread in threads.iter() {
        waittid(*thread as usize);
    }
...
```

---
### 實踐步驟
基於信號量的多線程應用 `sync_sem`
```rust
unsafe fn first() -> ! {
    sleep(10);
    println!("First work and wakeup Second");
    semaphore_up(SEM_SYNC);
    exit(0)
}
unsafe fn second() -> ! {
    println!("Second want to continue,but need to wait first");
    semaphore_down(SEM_SYNC);
    println!("Second can work now");
    exit(0)
}
```

---
### 實踐步驟
基於信號量的多線程應用 `sync_sem`
```
>> sync_sem
Second want to continue,but need to wait first
First work and wakeup Second
Second can work now
sync_sem passed!
```
- 信號量初值設為0
- semaphore_down() ：線程會掛起/阻塞（suspend/block）
- semaphore_up()：會喚醒掛起的線程

---
###  程序設計
semaphore的核心數據結構
```rust
pub struct Semaphore {
    pub inner: UPSafeCell<SemaphoreInner>, //UPSafeCell包裹的內部可變結構
}

pub struct SemaphoreInner {
    pub count: isize, //信號量的計數值
    pub wait_queue: VecDeque<Arc<TaskControlBlock>>, //信號量的等待隊列
}
```

---
###  程序設計
semaphore的相關函數
```rust
    pub fn down(&self) {
        let mut inner = self.inner.exclusive_access();
        inner.count -= 1; //信號量的計數值減一
        if inner.count < 0 {
            inner.wait_queue.push_back(current_task().unwrap()); //放入等待隊列
            drop(inner);
            //把當前線程從就緒隊列中取出，設置為阻塞態，切換到另一就緒線程執行
            block_current_and_run_next();
        }
    }
```


---
###  程序設計
semaphore的相關函數
```rust
    pub fn up(&self) {
        let mut inner = self.inner.exclusive_access();
        inner.count += 1;//信號量的計數值加一
        if inner.count <= 0 {
            //從等待隊列中取出線程，並放入到就緒隊列中
            if let Some(task) = inner.wait_queue.pop_front() {
                add_task(task);
            }
        }
    }
```



---
### 實踐步驟
基於互斥鎖和條件變量的多線程應用 `test_condvar`
```rust
pub fn main() -> i32 {
    // create condvar & mutex
    assert_eq!(condvar_create() as usize, CONDVAR_ID);
    assert_eq!(mutex_blocking_create() as usize, MUTEX_ID);
    // create threads
    let threads = vec![ thread_create(first as usize, 0),
                        thread_create(second as usize, 0),];
    // wait for all threads to complete
    for thread in threads.iter() {
        waittid(*thread as usize);
    }
    ...
```

---
### 實踐步驟
基於互斥鎖和條件變量的多線程應用 `test_condvar`
```rust
unsafe fn second() -> ! {
    println!("Second want to continue,but need to wait A=1");
    mutex_lock(MUTEX_ID);
    while A == 0 {
        println!("Second: A is {}", A);
        condvar_wait(CONDVAR_ID, MUTEX_ID);
    }
    mutex_unlock(MUTEX_ID);
    println!("A is {}, Second can work now", A);
    exit(0)
}
```

---
### 實踐步驟
基於互斥鎖和條件變量的多線程應用 `test_condvar`
```rust
unsafe fn first() -> ! {
    sleep(10);
    println!("First work, Change A --> 1 and wakeup Second");
    mutex_lock(MUTEX_ID);
    A = 1;
    condvar_signal(CONDVAR_ID);
    mutex_unlock(MUTEX_ID);
    exit(0)
}
```

---
### 實踐步驟
基於互斥鎖和條件變量的多線程應用 `test_condvar`
```
>> test_condvar
Second: A is 0
First work, Change A --> 1 and wakeup Second
A is 1, Second can work now
```
- `second`先執行，但由於`A==0`，使得等在條件變量上
- `first`後執行，但會先於`second`，並通過條件變量喚醒`second`

---
###  程序設計
condvar的核心數據結構
```rust
pub struct Condvar {
    pub inner: UPSafeCell<CondvarInner>, //UPSafeCell包裹的內部可變結構
}

pub struct CondvarInner {
    pub wait_queue: VecDeque<Arc<TaskControlBlock>>,//等待隊列
}
```

---
###  程序設計
condvar的相關函數
```rust
    pub fn wait(&self, mutex: Arc<dyn Mutex>) {
        mutex.unlock(); //釋放鎖
        let mut inner = self.inner.exclusive_access();
        inner.wait_queue.push_back(current_task().unwrap()); //放入等待隊列
        drop(inner);
        //把當前線程從就緒隊列中取出，設置為阻塞態，切換到另一就緒線程執行
        block_current_and_run_next();
        mutex.lock();
    }
```

---
###  程序設計
condvar的相關函數
```rust
    pub fn signal(&self) {
        let mut inner = self.inner.exclusive_access();
        //從等待隊列中取出線程，並放入到就緒隊列中
        if let Some(task) = inner.wait_queue.pop_front() {
            add_task(task);
        }
    }
```

---
###  程序設計
sleep的設計實現
```rust
pub fn sys_sleep(ms: usize) -> isize {
    let expire_ms = get_time_ms() + ms;
    let task = current_task().unwrap();
    add_timer(expire_ms, task);
    block_current_and_run_next();
    0
}
```
---
### 小結
- 學習掌握面向多線程應用的同步互斥機制
   - 互斥鎖
   - 信號量
   - 條件變量
   - 原子操作
- 能寫慈母龍OS

![bg right 70%](figs/maiasaura.png)