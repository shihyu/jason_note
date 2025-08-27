# 設計模式指南 - Python 範例

## 一、創建型模式 (Creational Patterns)

### 1. 單例模式 (Singleton Pattern)
**精神**：確保一個類別只有一個實例，並提供全域訪問點。

**白話解釋**：就像一個國家只有一個總統，整個系統只需要一個物件實例。

**常見用法**：資料庫連線、設定檔管理、日誌記錄器

```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = "資料庫連線建立"
        return cls._instance
    
# 使用範例
db1 = DatabaseConnection()
db2 = DatabaseConnection()
print(db1 is db2)  # True，兩個變數指向同一個實例
```

### 2. 工廠模式 (Factory Pattern)
**精神**：定義一個創建物件的介面，讓子類別決定實例化哪個類別。

**白話解釋**：像是餐廳點餐，你說要什麼，廚房就做什麼給你，你不需要知道怎麼做。

**常見用法**：根據條件創建不同類型的物件

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "汪汪！"

class Cat(Animal):
    def speak(self):
        return "喵喵！"

class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            return None

# 使用範例
factory = AnimalFactory()
dog = factory.create_animal("dog")
print(dog.speak())  # 汪汪！
```

### 3. 建造者模式 (Builder Pattern)
**精神**：將複雜物件的建構過程分離，使同樣的建構過程可以創建不同的表示。

**白話解釋**：像組裝電腦，可以選擇不同的 CPU、記憶體、硬碟，最後組成一台完整的電腦。

**常見用法**：創建有許多選項的複雜物件

```python
class Computer:
    def __init__(self):
        self.cpu = None
        self.ram = None
        self.storage = None
    
    def __str__(self):
        return f"電腦配置：CPU={self.cpu}, RAM={self.ram}, Storage={self.storage}"

class ComputerBuilder:
    def __init__(self):
        self.computer = Computer()
    
    def set_cpu(self, cpu):
        self.computer.cpu = cpu
        return self
    
    def set_ram(self, ram):
        self.computer.ram = ram
        return self
    
    def set_storage(self, storage):
        self.computer.storage = storage
        return self
    
    def build(self):
        return self.computer

# 使用範例
gaming_pc = ComputerBuilder()\
    .set_cpu("Intel i9")\
    .set_ram("32GB")\
    .set_storage("2TB SSD")\
    .build()
print(gaming_pc)
```

## 二、結構型模式 (Structural Patterns)

### 4. 轉接器模式 (Adapter Pattern)
**精神**：將一個類別的介面轉換成客戶希望的另一個介面。

**白話解釋**：像是電源轉接頭，讓不同規格的插頭可以連接使用。

**常見用法**：整合第三方程式庫、舊系統相容

```python
# 舊的支付系統
class OldPaymentSystem:
    def make_payment(self, amount):
        return f"舊系統：支付 ${amount}"

# 新的支付介面
class NewPaymentInterface:
    def pay(self, amount):
        pass

# 轉接器
class PaymentAdapter(NewPaymentInterface):
    def __init__(self, old_system):
        self.old_system = old_system
    
    def pay(self, amount):
        return self.old_system.make_payment(amount)

# 使用範例
old_system = OldPaymentSystem()
adapter = PaymentAdapter(old_system)
print(adapter.pay(100))  # 舊系統：支付 $100
```

### 5. 裝飾者模式 (Decorator Pattern)
**精神**：動態地給物件添加新功能，不改變其結構。

**白話解釋**：像是咖啡加料，基本咖啡可以加牛奶、加糖、加奶泡，每加一樣就多一個功能。

**常見用法**：動態添加功能、權限驗證、日誌記錄

```python
class Coffee:
    def cost(self):
        return 30
    
    def description(self):
        return "基本咖啡"

class MilkDecorator:
    def __init__(self, coffee):
        self.coffee = coffee
    
    def cost(self):
        return self.coffee.cost() + 10
    
    def description(self):
        return self.coffee.description() + " + 牛奶"

class SugarDecorator:
    def __init__(self, coffee):
        self.coffee = coffee
    
    def cost(self):
        return self.coffee.cost() + 5
    
    def description(self):
        return self.coffee.description() + " + 糖"

# 使用範例
coffee = Coffee()
coffee_with_milk = MilkDecorator(coffee)
coffee_with_milk_sugar = SugarDecorator(coffee_with_milk)

print(coffee_with_milk_sugar.description())  # 基本咖啡 + 牛奶 + 糖
print(f"價格：${coffee_with_milk_sugar.cost()}")  # 價格：$45
```

### 6. 外觀模式 (Facade Pattern)
**精神**：為子系統中的一組介面提供一個統一的高層介面。

**白話解釋**：像是家庭劇院的遙控器，一個按鈕就能開啟電視、音響、調光等多個設備。

**常見用法**：簡化複雜系統的操作介面

```python
class TV:
    def turn_on(self):
        return "電視開啟"
    
class SoundSystem:
    def turn_on(self):
        return "音響開啟"
    
class Lights:
    def dim(self):
        return "燈光調暗"

class HomeTheaterFacade:
    def __init__(self):
        self.tv = TV()
        self.sound = SoundSystem()
        self.lights = Lights()
    
    def watch_movie(self):
        results = []
        results.append(self.tv.turn_on())
        results.append(self.sound.turn_on())
        results.append(self.lights.dim())
        return " -> ".join(results)

# 使用範例
theater = HomeTheaterFacade()
print(theater.watch_movie())  # 電視開啟 -> 音響開啟 -> 燈光調暗
```

## 三、行為型模式 (Behavioral Patterns)

### 7. 觀察者模式 (Observer Pattern)
**精神**：定義物件間一對多的依賴關係，當一個物件狀態改變時，所有依賴者都會收到通知。

**白話解釋**：像是訂閱 YouTube 頻道，頻道更新影片時，所有訂閱者都會收到通知。

**常見用法**：事件處理、模型-視圖架構、訊息推播

```python
class YouTubeChannel:
    def __init__(self, name):
        self.name = name
        self.subscribers = []
    
    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
    
    def notify(self, video):
        for subscriber in self.subscribers:
            subscriber.update(self.name, video)
    
    def upload_video(self, video):
        print(f"{self.name} 上傳了：{video}")
        self.notify(video)

class Subscriber:
    def __init__(self, name):
        self.name = name
    
    def update(self, channel, video):
        print(f"{self.name} 收到通知：{channel} 上傳了 {video}")

# 使用範例
channel = YouTubeChannel("科技頻道")
subscriber1 = Subscriber("小明")
subscriber2 = Subscriber("小華")

channel.subscribe(subscriber1)
channel.subscribe(subscriber2)
channel.upload_video("Python 教學")
```

### 8. 策略模式 (Strategy Pattern)
**精神**：定義一系列演算法，把它們封裝起來，並且使它們可以互相替換。

**白話解釋**：像是出門選擇交通工具，可以開車、騎車或搭捷運，根據情況選擇不同策略。

**常見用法**：支付方式選擇、排序演算法選擇、資料驗證

```python
class PaymentStrategy:
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        return f"使用信用卡支付 ${amount}"

class CashPayment(PaymentStrategy):
    def pay(self, amount):
        return f"使用現金支付 ${amount}"

class MobilePayment(PaymentStrategy):
    def pay(self, amount):
        return f"使用行動支付 ${amount}"

class ShoppingCart:
    def __init__(self, payment_strategy):
        self.payment_strategy = payment_strategy
    
    def checkout(self, amount):
        return self.payment_strategy.pay(amount)

# 使用範例
cart = ShoppingCart(CreditCardPayment())
print(cart.checkout(1000))  # 使用信用卡支付 $1000

cart.payment_strategy = MobilePayment()
print(cart.checkout(500))   # 使用行動支付 $500
```

### 9. 模板方法模式 (Template Method Pattern)
**精神**：定義演算法的骨架，將一些步驟延遲到子類別中實現。

**白話解釋**：像是泡茶和泡咖啡，步驟類似（煮水、沖泡、倒入杯子、加調料），但細節不同。

**常見用法**：資料處理流程、遊戲回合制流程

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    def process(self):
        self.read_data()
        self.process_data()
        self.save_data()
    
    @abstractmethod
    def read_data(self):
        pass
    
    @abstractmethod
    def process_data(self):
        pass
    
    def save_data(self):
        print("儲存處理後的資料")

class CSVProcessor(DataProcessor):
    def read_data(self):
        print("讀取 CSV 檔案")
    
    def process_data(self):
        print("處理 CSV 資料")

class JSONProcessor(DataProcessor):
    def read_data(self):
        print("讀取 JSON 檔案")
    
    def process_data(self):
        print("處理 JSON 資料")

# 使用範例
csv_processor = CSVProcessor()
csv_processor.process()
print("---")
json_processor = JSONProcessor()
json_processor.process()
```

### 10. 命令模式 (Command Pattern)
**精神**：將請求封裝成物件，讓你可以用不同的請求參數化客戶端。

**白話解釋**：像是遙控器的按鈕，每個按鈕都是一個命令，按下就執行對應動作。

**常見用法**：撤銷/重做功能、巨集錄製、佇列請求

```python
class Light:
    def turn_on(self):
        return "燈光開啟"
    
    def turn_off(self):
        return "燈光關閉"

class LightOnCommand:
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        return self.light.turn_on()
    
    def undo(self):
        return self.light.turn_off()

class LightOffCommand:
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        return self.light.turn_off()
    
    def undo(self):
        return self.light.turn_on()

class RemoteControl:
    def __init__(self):
        self.command = None
        self.history = []
    
    def set_command(self, command):
        self.command = command
    
    def press_button(self):
        if self.command:
            result = self.command.execute()
            self.history.append(self.command)
            return result
    
    def press_undo(self):
        if self.history:
            last_command = self.history.pop()
            return last_command.undo()

# 使用範例
light = Light()
light_on = LightOnCommand(light)
light_off = LightOffCommand(light)

remote = RemoteControl()
remote.set_command(light_on)
print(remote.press_button())  # 燈光開啟
print(remote.press_undo())    # 燈光關閉
```

## 總結

設計模式的核心價值：
- **提高程式碼的可重用性**：相同的模式可以在不同專案中使用
- **提高程式碼的可讀性**：使用標準化的解決方案，團隊成員更容易理解
- **降低耦合度**：各個元件之間的依賴關係更加清晰
- **提高可維護性**：結構清晰的程式碼更容易修改和擴展

記住：設計模式不是萬能的，要根據實際需求選擇合適的模式，避免過度設計！