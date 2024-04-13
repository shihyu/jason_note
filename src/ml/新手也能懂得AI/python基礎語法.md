 # python基礎語法



## 0.了解變數與資料型態

在開始之前我們要先知道如何宣告變數(Variable)與它的資料型態(Type)。

### int、float、str

int:只要是數字在程式中就會被當作是int像是:0、1、1000、-1都是屬於int的類型。

```ini
a = 0    #int
```

float:只要將數字加上.像是0.0、0.1、1.2534都是屬於float。

```ini
a = 0.0  #float
```

在兩者之間加入'' or ""就會是屬於str。

```ini
a = '0'  #str
```

在以上的範例中a就是我們的變數，而這個變數的型態會隨者我賦予它的值去變動它。

### 運算規則

在這些資料型態裡面當然有一些運算規則。
例如:int與float可以互相加減乘除、str只能與int相乘

```makefile
a = 0.1 #float
b = 1   #int
print(a+b)
-------顯示--------
1.1
a='0'
b = 2
print(a*b)
-------顯示--------
'00'
```

### List、Dict、Tuple

如果有一大筆的資料難道要一個一個宣告變數嗎?當然還有幾種資料型態。

#### list[資料1,資料2]:

```lua
list = [1,2,3,4]
print(list[0])
-------顯示--------
1
```

當我們有很多資料時可以放入到一個list當中，若有需要的資料可以直接輸入變數名稱[index]就能呼叫出裡面的資料。

#### dict{'資料的索引1':資料的值1,'資料的索引2':資料的值2}:

```python
dict = {'a':0,'b':1}
print(dict['a'])
-------顯示--------
0
```

dict則是可以依照索引值去尋找你所想要的數值。

#### tuple(資料1,資料2):

```python
tuple = (1,2,3,4)
print(tuple[0])
-------顯示--------
1
```

我們可以看到tuple的效果與list相同，但實際上卻是有差別的，我們用以下程式做個實驗。

```python
tuple = (1,2,3,4)
tuple[0]=0
-------顯示--------
TypeError: 'tuple' object does not support item assignment
list = [1,2,3,4]
list[0]=0
print(list)
-------顯示--------
[0,2,3,4]
```

這一些都搞懂之後我們就來開始一些python的基礎操作吧!!

## 1.基礎操作

### print

> print (* objects , sep = ' ' , end = '\n' , file = sys . stdout , flush = False )

當我們要顯示文字或變數內容時，可以使用print()顯示結果。

```lua
print("hello world")
-------顯示--------
hello world
```

### type

> type(object)

若是我們不知道一個變數的型態，可以使用type()查詢。

```go
b = 1
print(type(b))
-------顯示--------
int
```

### input

> input([prompt])

當我們程式需要一些外部輸入的時候我們可以使用input()。

```lua
n = input('這裡可以輸入你想要的文字:') #輸入123123
print(n)
-------顯示--------
這裡可以輸入你想要的文字:123123
123123
```

### int()、float()、str()

如果把上面的程式修改成做數值相加就會發現系統跳出錯誤提示。

```python
n = input('這裡可以輸入你想要的文字:') #輸入123123
a = 123456
print(n+a)
-------顯示--------
TypeError: can only concatenate str (not "int") to str
```

會發生這樣的問題是因為input回傳是str而不是int與float，所以我們需會用到int()、float()、str()把數值轉型。

```python
n = int(input('這裡可以輸入你想要的文字:')) #輸入123123
a = 123456
print(n+a)
-------顯示--------
246579
```

## 2.邏輯判斷(if...else、for、while)

### if..else

從這邊開始就會有一些難度了，不過也別擔心，if...else我們每天也都會用到，像是今天如果下雨我就不出門，只是將這種邏輯讓程式看得懂而已，以下是程式的用法。

```bash
if 條件1:
    執行的動作
elif 條件2:
    執行的動作
else:
    執行的動作
```

這樣講可能會比較難理解，我舉個例子來說。
例如:成績80以上的人顯示好棒、60以上的人顯示不錯、60以下的人顯示再加強，用程式就可以這樣子表達:

```bash
if score >=80:
    print('好棒')
elif score >=60:
    print('不錯')
else:
    print('再加強')
```

### for

> range(start, stop[, step])

當我們需要做重複的事情的時候我們就可以使用for 變數名稱 in range(範圍)。
例如:一班10個學生，成績80以上的人顯示好棒、60以上的人顯示不錯、60以下的人顯示再加強。

```python
score = [80,99,10,20,50,60,70,30,20,35]
for i in range(10):
    if score[i] >=80:
        print('好棒')
    elif score[i] >=60:
        print('不錯')
    else:
        print('再加強')
```

不過像上述的寫法會有一種問題，假如今天有轉走了一位學生但範圍還是10，那麼程式執行到最後時就會告知你index out range。

```python
score = [80,99,10,20,50,60,70,30,20]
for i in range(10):
    if score[i] >=80:
        print('好棒')
    elif score[i] >=60:
        print('不錯')
    else:
        print('再加強')
-------顯示--------
好棒
好棒
再加強
再加強
再加強
不錯
不錯
再加強
再加強
IndexError: list index out of range
```

所以我們可以將寫法改變成range(len(score))。

```python
score = [80,99,10,20,50,60,70,30,20]
for i in range(len(score)):#len()可以取得str或list的大小
    if score[i] >=80:
        print('好棒')
    elif score[i] >=60:
        print('不錯')
    else:
        print('再加強')
```

或直接使用score做迴圈。

```bash
score = [80,99,10,20,50,60,70,30,20]
for i in score:#直接拿score做迴圈條件
    if i >=80:
        print('好棒')
    elif i >=60:
        print('不錯')
    else:
        print('再加強')
```

### while

前面說到的for是因為能知道這個迴圈會做幾次，如果不知道要做多少次呢?
舉一個例子，像是寫一個猜數字的小遊戲

```python
n = int(input('輸入數字:'))
num = 80
while(num != n):#未達成條件繼續迴圈
    print('猜錯了!!')
```

我們也可以將while寫成永久迴圈，並且用if控制跳脫迴圈。

```python
n = int(input('輸入數字:'))
num = 80
while(True):#永遠不會停止
    if num == n:.
        break #break為中斷迴圈
    print('猜錯了!!')
```

以上就是迴圈的基本應用。

## 3.進階教學

### function

當我們在寫一個專案的時候，常常會為了方便管理而將一個功能寫在其他地方。
這時就會去定義def function名稱(變數)。
例子:寫一個將兩數相加的function

```css
def add_num(a,b):
    return a+b
    
num = add_num(1,2)
print(num)
-------顯示--------
3
```

但要注意function裡面的變數並不是全域變數，但list、dict、tuple會是為全域變數。
例子:

```sql
def add_num():
    result = list[0]+list[1] #list為全域變數不需傳入function
    return result #result則不是全域變數只存在於這個function中
list = [1,2]
num = add_num()
print(num)
print(result)
-------顯示--------
3
NameError: name 'result' is not defined
```

### class

這個是資料結構的一些技術我盡量簡單的解釋，因為在AI方面這比較不重要，所以我只會提到些基礎的用法，若有興趣的人可以再去查詢這方面的相關知識

```python
class Student:
    # 建構式(Constructor)想放入class的資料會通過__init__建立(放入austin與100到這)
    def __init__(self, name, score):
        self.name = name   #屬性(Attribute):可以使數值在各function之中傳遞
        self.score = score  
        
    # 方法(Method)實際執行動作的地方
    def print_info(self):
        print(f"{self.name}:{self.score}")

people = Student('austin',100)#這邊只會執行__init__
people.print_info()#這邊才是使用print_info這個function
-------顯示--------
austin:100
```

- 類別(Class):在例子中class就是Student
- 物件(Object):在例子中Object就是people
- 屬性(Attribute):在例子中Attribute就是
- 建構式(Constructor):在例子中Constructor就是def **init**(self, name, score)
- 方法(Method):在例子中Method就是def print_info(self)

用一句來講就是:將變數指定為物件(Object)，並且使用建構式(Constructor)賦予屬性(Attribute)，最後用方法(Method)來達成動作

那今天就到這裡，明天會正式講解AI相關技術，謝謝大家

