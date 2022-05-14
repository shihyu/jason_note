# python中的wait和notify

這次講一下python中的wait和notify

現在假如有如下情況：

小明:小紅

小紅:在

小明:我喜歡你
小紅:對不起，你是個好人。

對於這種一問一答的方式，我們是否也可以通過加鎖來解決呢，我們看代碼。

```python
import threading

class XiaoMing(threading.Thread):
    def __init__(self,lock):
        super().__init__(name='小明')
    
    
    def run(self):
        lock.acquire()
        print('{}:小紅'.format(self.name))
        lock.release()

        lock.acquire()
        print('{}:我喜歡你'.format(self.name))
        lock.release()

class XiaoHong(threading.Thread):
    def __init__(self,lock):
        super().__init__(name='小紅')
    
    def run(self):
        lock.acquire()
        print('{}:在'.format(self.name))
        lock.release()

        lock.acquire()
        print('{}:對不起,你是個好人'.format(self.name))
        lock.release()

if __name__ == '__main__':
    lock = threading.Lock()
    xiaoming = XiaoMing(lock)
    xiaohong = XiaoHong(lock)
    
    xiaoming.start()
    xiaohong.start()
```

這個時候會出現一個現象，我們發現執行的結果是

小明:小紅
小明:我喜歡你
小紅:在
小紅:對不起,你是個好人

很顯然，這跟我們想要的結果是不一樣的，那麼為什麼會導致這樣的結果呢。

原因就在於我們在小明說完小紅的時候會釋放鎖，接著小明這個線程又拿到了鎖，這個時候又繼續說了我喜歡你。這就是導致結果跟預期不一致的原因。

因此我們在這裡引出了wait和notify這兩個方法，這兩個方法屬於threading的Condition類，condition是一個條件變量，是用來控制復雜的線程之間的同步。

如果看過condition的源碼，就會發現condition實現了__enter__ 和__exit__這兩個魔術方法，因此我們可以通過with語句來使用condition這個變量。

再說一下wait和notify，wait()只有在被notify喚醒時，才會繼續往下執行。因此會有下面這樣的代碼。

```python
import threading
from threading import Condition


class XiaoMing(threading.Thread):
    def __init__(self,condition):
        super().__init__(name='小明')
        self.condition = condition
    
    def run(self):
        with self.condition:
            print('{}:小紅'.format(self.name))
            self.condition.notify()
            self.condition.wait()

            print('{}:我喜歡你'.format(self.name))
            self.condition.notify()
            self.condition.wait()


class XiaoHong(threading.Thread):
    def __init__(self,condition):
        super().__init__(name='小紅')
        self.condition = condition

    def run(self):
        with self.condition:
            self.condition.wait()
            print('{}:在'.format(self.name))
            self.condition.notify()

            self.condition.wait()
            print('{}:對不起,你是個好人'.format(self.name))
            self.condition.notify()

if __name__ == '__main__':
    condition = threading.Condition()
    xiaoming = XiaoMing(condition)
    xiaohong = XiaoHong(condition)
    
    xiaohong.start()
    xiaoming.start()
```

運行上面的代碼，我們發現執行結果按照我們預期的進行了。需要注意的一點就是start的順序改了，是小紅先start，小明才start。

如果是小明先start的話，那麼小紅就會在小明notify之後才start，這樣小紅的wait就收不到小明發過來的信號了，因此會導致

程序一直卡住。

其實這個condition的源碼裡面，在初始化condition的時候，就會上一把鎖，這樣另一個線程就進不去with裡面了，

而在調用wait的時候，會先把condition時初始化的鎖釋放掉，然後再分配一把鎖到condition的等待隊列中，等待notify的喚醒。