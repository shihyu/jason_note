# C++基礎入門

## 1 C++初識

### 1.1  第一個C++程式

編寫一個C++程式總共分為4個步驟

* 創建專案
* 創建檔案
* 編寫程式碼
* 運行程式

#### 1.1.1 創建專案

​	Visual Studio是我們用來編寫C++程式的主要工具，我們先將它打開

![1541383178746](assets/1541383178746.png)



![1541384366413](assets/1541384366413.png)

#### 1.1.2 創建檔案

右鍵原始檔，選擇添加->新建項

![1541383817248](assets/1541383817248.png)

給C++檔案起個名稱，然後點擊添加即可。

![1541384140042](assets/1541384140042.png)



#### 1.1.3 編寫程式碼

```c++
#include<iostream>
using namespace std;

int main() {

	cout << "Hello world" << endl;

	system("pause");

	return 0;
}
```

#### 1.1.4 運行程式

![1541384818688](assets/1541384818688.png)













### 1.2 註釋

**作用**：在程式碼中加一些說明和解釋，方便自己或其他程式員程式員閱讀程式碼

**兩種格式**

1. **單行註釋**：`// 描述資訊` 
   - 通常放在一行程式碼的上方，或者一條語句的末尾，==對該行程式碼說明==
2. **多行註釋**： `/* 描述資訊 */`
   - 通常放在一段程式碼的上方，==對該段程式碼做整體說明==

> 提示：編譯器在編譯程式碼時，會忽略註釋的內容











### 1.3 變數

**作用**：給一段指定的記憶體空間起名，方便操作這段記憶體

**語法**：`數據型別 變數名 = 初始值;`

**示例：**

```C++
#include<iostream>
using namespace std;

int main() {

	//變數的定義
	//語法：數據型別  變數名 = 初始值

	int a = 10;

	cout << "a = " << a << endl;
	
	system("pause");

	return 0;
}
```



> 注意：C++在創建變數時，必須給變數一個初始值，否則會報錯















### 1.4  常數

**作用**：用於記錄程式中不可更改的數據

C++定義常數兩種方式

1. **\#define** 巨集常數： `#define 常數名 常數值`
   * ==通常在檔案上方定義==，表示一個常數


2. **const**修飾的變數 `const 數據型別 常數名 = 常數值`
   * ==通常在變數定義前加關鍵字const==，修飾該變數為常數，不可修改



**示例：**

```C++
//1、巨集常數
#define day 7

int main() {

	cout << "一週裡總共有 " << day << " 天" << endl;
	//day = 8;  //報錯，巨集常數不可以修改

	//2、const修飾變數
	const int month = 12;
	cout << "一年裡總共有 " << month << " 個月份" << endl;
	//month = 24; //報錯，常數是不可以修改的
	
	
	system("pause");

	return 0;
}
```










### 1.5 關鍵字

**作用：**關鍵字是C++中預先保留的單詞（標識符）

* **在定義變數或者常數時候，不要用關鍵字**



C++關鍵字如下：

| asm        | do           | if               | return      | typedef  |
| ---------- | ------------ | ---------------- | ----------- | -------- |
| auto       | double       | inline           | short       | typeid   |
| bool       | dynamic_cast | int              | signed      | typename |
| break      | else         | long             | sizeof      | union    |
| case       | enum         | mutable          | static      | unsigned |
| catch      | explicit     | namespace        | static_cast | using    |
| char       | export       | new              | struct      | virtual  |
| class      | extern       | operator         | switch      | void     |
| const      | false        | private          | template    | volatile |
| const_cast | float        | protected        | this        | wchar_t  |
| continue   | for          | public           | throw       | while    |
| default    | friend       | register         | true        |          |
| delete     | goto         | reinterpret_cast | try         |          |

`提示：在給變數或者常數起名稱時候，不要用C++得關鍵字，否則會產生歧義。`











### 1.6 標識符命名規則

**作用**：C++規定給標識符（變數、常數）命名時，有一套自己的規則

* 標識符不能是關鍵字
* 標識符只能由字母、數字、下劃線組成
* 第一個字符必須為字母或下劃線
* 標識符中字母區分大小寫

> 建議：給標識符命名時，爭取做到見名知意的效果，方便自己和他人的閱讀















## 2 數據型別

C++規定在創建一個變數或者常數時，必須要指定出相應的數據型別，否則無法給變數分配記憶體

### 2.1 整型

**作用**：整型變數表示的是==整數型別==的數據

C++中能夠表示整型的型別有以下幾種方式，**區別在於所佔記憶體空間不同**：

| **數據型別**        | **佔用空間**                                    | 取值範圍         |
| ------------------- | ----------------------------------------------- | ---------------- |
| short(短整型)       | 2位元元組                                           | (-2^15 ~ 2^15-1) |
| int(整型)           | 4位元元組                                           | (-2^31 ~ 2^31-1) |
| long(長整形)        | Windows為4位元元組，Linux為4位元元組(32位元元)，8位元元組(64位元元) | (-2^31 ~ 2^31-1) |
| long long(長長整形) | 8位元元組                                           | (-2^63 ~ 2^63-1) |













### 2.2 sizeof關鍵字

**作用：**利用sizeof關鍵字可以==統計數據型別所佔記憶體大小==

**語法：** `sizeof( 數據型別 / 變數)`

**示例：**

```C++
int main() {

	cout << "short 型別所佔記憶體空間為： " << sizeof(short) << endl;

	cout << "int 型別所佔記憶體空間為： " << sizeof(int) << endl;

	cout << "long 型別所佔記憶體空間為： " << sizeof(long) << endl;

	cout << "long long 型別所佔記憶體空間為： " << sizeof(long long) << endl;

	system("pause");

	return 0;
}
```





> **整型結論**：==short < int <= long <= long long==















### 2.3 實型（浮點型）

**作用**：用於==表示小數==

浮點型變數分為兩種：

1. 單精度float 
2. 雙精度double

兩者的**區別**在於表示的有效數字範圍不同。

| **數據型別** | **佔用空間** | **有效數字範圍** |
| ------------ | ------------ | ---------------- |
| float        | 4位元元組        | 7位元元有效數字      |
| double       | 8位元元組        | 15～16位元元有效數字 |

**示例：**

```C++
int main() {

	float f1 = 3.14f;
	double d1 = 3.14;

	cout << f1 << endl;
	cout << d1<< endl;

	cout << "float  sizeof = " << sizeof(f1) << endl;
	cout << "double sizeof = " << sizeof(d1) << endl;

	//科學計數法
	float f2 = 3e2; // 3 * 10 ^ 2 
	cout << "f2 = " << f2 << endl;

	float f3 = 3e-2;  // 3 * 0.1 ^ 2
	cout << "f3 = " << f3 << endl;

	system("pause");

	return 0;
}
```











### 2.4 字符型

**作用：**字符型變數用於顯示單個字符

**語法：**`char ch = 'a';`



> 注意1：在顯示字符型變數時，用單引號將字符括起來，不要用雙引號

> 注意2：單引號內只能有一個字符，不可以是字串



- C和C++中字符型變數只佔用==1個位元元組==。
- 字符型變數並不是把字符本身放到記憶體中存儲，而是將對應的ASCII編碼放入到存儲單元



示例：

```C++
int main() {
	
	char ch = 'a';
	cout << ch << endl;
	cout << sizeof(char) << endl;

	//ch = "abcde"; //錯誤，不可以用雙引號
	//ch = 'abcde'; //錯誤，單引號內只能參照一個字符

	cout << (int)ch << endl;  //查看字符a對應的ASCII碼
	ch = 97; //可以直接用ASCII給字符型變數賦值
	cout << ch << endl;

	system("pause");

	return 0;
}
```

ASCII碼錶格：

| **ASCII**值 | **控制字符** | **ASCII**值 | **字符** | **ASCII**值 | **字符** | **ASCII**值 | **字符** |
| ----------- | ------------ | ----------- | -------- | ----------- | -------- | ----------- | -------- |
| 0           | NUT          | 32          | (space)  | 64          | @        | 96          | 、       |
| 1           | SOH          | 33          | !        | 65          | A        | 97          | a        |
| 2           | STX          | 34          | "        | 66          | B        | 98          | b        |
| 3           | ETX          | 35          | #        | 67          | C        | 99          | c        |
| 4           | EOT          | 36          | $        | 68          | D        | 100         | d        |
| 5           | ENQ          | 37          | %        | 69          | E        | 101         | e        |
| 6           | ACK          | 38          | &        | 70          | F        | 102         | f        |
| 7           | BEL          | 39          | ,        | 71          | G        | 103         | g        |
| 8           | BS           | 40          | (        | 72          | H        | 104         | h        |
| 9           | HT           | 41          | )        | 73          | I        | 105         | i        |
| 10          | LF           | 42          | *        | 74          | J        | 106         | j        |
| 11          | VT           | 43          | +        | 75          | K        | 107         | k        |
| 12          | FF           | 44          | ,        | 76          | L        | 108         | l        |
| 13          | CR           | 45          | -        | 77          | M        | 109         | m        |
| 14          | SO           | 46          | .        | 78          | N        | 110         | n        |
| 15          | SI           | 47          | /        | 79          | O        | 111         | o        |
| 16          | DLE          | 48          | 0        | 80          | P        | 112         | p        |
| 17          | DCI          | 49          | 1        | 81          | Q        | 113         | q        |
| 18          | DC2          | 50          | 2        | 82          | R        | 114         | r        |
| 19          | DC3          | 51          | 3        | 83          | S        | 115         | s        |
| 20          | DC4          | 52          | 4        | 84          | T        | 116         | t        |
| 21          | NAK          | 53          | 5        | 85          | U        | 117         | u        |
| 22          | SYN          | 54          | 6        | 86          | V        | 118         | v        |
| 23          | TB           | 55          | 7        | 87          | W        | 119         | w        |
| 24          | CAN          | 56          | 8        | 88          | X        | 120         | x        |
| 25          | EM           | 57          | 9        | 89          | Y        | 121         | y        |
| 26          | SUB          | 58          | :        | 90          | Z        | 122         | z        |
| 27          | ESC          | 59          | ;        | 91          | [        | 123         | {        |
| 28          | FS           | 60          | <        | 92          | /        | 124         | \|       |
| 29          | GS           | 61          | =        | 93          | ]        | 125         | }        |
| 30          | RS           | 62          | >        | 94          | ^        | 126         | `        |
| 31          | US           | 63          | ?        | 95          | _        | 127         | DEL      |

ASCII 碼大致由以下**兩部分組**成：

* ASCII 非印出控制字符： ASCII 表上的數字 **0-31** 分配給了控制字符，用於控制像印出機等一些外圍設備。
* ASCII 印出字符：數字 **32-126** 分配給了能在鍵盤上找到的字符，當查看或印出文件時就會出現。













### 2.5 轉義字符

**作用：**用於表示一些==不能顯示出來的ASCII字符==

現階段我們常用的轉義字符有：` \n  \\  \t`

| **轉義字符** | **含義**                                | **ASCII**碼值（十進制） |
| ------------ | --------------------------------------- | ----------------------- |
| \a           | 警報                                    | 007                     |
| \b           | 退格(BS) ，將當前位元元置移到前一列         | 008                     |
| \f           | 換頁(FF)，將當前位元元置移到下頁開頭        | 012                     |
| **\n**       | **換行(LF) ，將當前位元元置移到下一行開頭** | **010**                 |
| \r           | 回車(CR) ，將當前位元元置移到本行開頭       | 013                     |
| **\t**       | **水平製表(HT)  （跳到下一個TAB位元元置）** | **009**                 |
| \v           | 垂直製表(VT)                            | 011                     |
| **\\\\**     | **代表一個反斜線字符"\"**               | **092**                 |
| \'           | 代表一個單引號（撇號）字符              | 039                     |
| \"           | 代表一個雙引號字符                      | 034                     |
| \?           | 代表一個問號                            | 063                     |
| \0           | 數字0                                   | 000                     |
| \ddd         | 8進制轉義字符，d範圍0~7                 | 3位元元8進制                |
| \xhh         | 16進制轉義字符，h範圍0~9，a~f，A~F      | 3位元元16進制               |

示例：

```C++
int main() {
	
	
	cout << "\\" << endl;
	cout << "\tHello" << endl;
	cout << "\n" << endl;

	system("pause");

	return 0;
}
```













### 2.6 字串型

**作用**：用於表示一串字符

**兩種風格**

1. **C風格字串**： `char 變數名[] = "字串值"`

   示例：

   ```C++
   int main() {

   	char str1[] = "hello world";
   	cout << str1 << endl;
       
   	system("pause");

   	return 0;
   }
   ```

> 注意：C風格的字串要用雙引號括起來

1. **C++風格字串**：  `string  變數名 = "字串值"`

   示例：

   ```C++
   int main() {

   	string str = "hello world";
   	cout << str << endl;
   	
   	system("pause");

   	return 0;
   }
   ```

   ​

> 注意：C++風格字串，需要加入頭檔案==#include\<string>==













### 2.7 布爾型別 bool

**作用：**布爾數據型別代表真或假的值 

bool型別只有兩個值：

* true  --- 真（本質是1）
* false --- 假（本質是0）

**bool型別佔==1個位元元組==大小**

示例：

```C++
int main() {

	bool flag = true;
	cout << flag << endl; // 1

	flag = false;
	cout << flag << endl; // 0

	cout << "size of bool = " << sizeof(bool) << endl; //1
	
	system("pause");

	return 0;
}
```















### 2.8 數據的輸入

**作用：用於從鍵盤獲取數據**

**關鍵字：**cin

**語法：** `cin >> 變數 `

示例：

```C++
int main(){

	//整型輸入
	int a = 0;
	cout << "請輸入整型變數：" << endl;
	cin >> a;
	cout << a << endl;

	//浮點型輸入
	double d = 0;
	cout << "請輸入浮點型變數：" << endl;
	cin >> d;
	cout << d << endl;

	//字符型輸入
	char ch = 0;
	cout << "請輸入字符型變數：" << endl;
	cin >> ch;
	cout << ch << endl;

	//字串型輸入
	string str;
	cout << "請輸入字串型變數：" << endl;
	cin >> str;
	cout << str << endl;

	//布爾型別輸入
	bool flag = true;
	cout << "請輸入布爾型變數：" << endl;
	cin >> flag;
	cout << flag << endl;
	system("pause");
	return EXIT_SUCCESS;
}
```













## 3 運算子

**作用：**用於執行程式碼的運算

本章我們主要講解以下幾類運算子：

| **運算子型別** | **作用**                               |
| -------------- | -------------------------------------- |
| 算術運算子     | 用於處理四則運算                       |
| 賦值運算子     | 用於將表達式的值賦給變數               |
| 比較運算子     | 用於表達式的比較，並返回一個真值或假值 |
| 邏輯運算子     | 用於根據表達式的值返回真值或假值       |

### 3.1 算術運算子

**作用**：用於處理四則運算 

算術運算子包括以下符號：

| **運算子** | **術語**   | **示例**    | **結果**  |
| ---------- | ---------- | ----------- | --------- |
| +          | 正號       | +3          | 3         |
| -          | 負號       | -3          | -3        |
| +          | 加         | 10 + 5      | 15        |
| -          | 減         | 10 - 5      | 5         |
| *          | 乘         | 10 * 5      | 50        |
| /          | 除         | 10 / 5      | 2         |
| %          | 取模(取餘) | 10 % 3      | 1         |
| ++         | 前置遞增   | a=2; b=++a; | a=3; b=3; |
| ++         | 後置遞增   | a=2; b=a++; | a=3; b=2; |
| --         | 前置遞減   | a=2; b=--a; | a=1; b=1; |
| --         | 後置遞減   | a=2; b=a--; | a=1; b=2; |

**示例1：**

```C++
//加減乘除
int main() {

	int a1 = 10;
	int b1 = 3;

	cout << a1 + b1 << endl;
	cout << a1 - b1 << endl;
	cout << a1 * b1 << endl;
	cout << a1 / b1 << endl;  //兩個整數相除結果依然是整數

	int a2 = 10;
	int b2 = 20;
	cout << a2 / b2 << endl; 

	int a3 = 10;
	int b3 = 0;
	//cout << a3 / b3 << endl; //報錯，除數不可以為0


	//兩個小數可以相除
	double d1 = 0.5;
	double d2 = 0.25;
	cout << d1 / d2 << endl;

	system("pause");

	return 0;
}
```

> 總結：在除法運算中，除數不能為0





**示例2：**

```C++
//取模
int main() {

	int a1 = 10;
	int b1 = 3;

	cout << 10 % 3 << endl;

	int a2 = 10;
	int b2 = 20;

	cout << a2 % b2 << endl;

	int a3 = 10;
	int b3 = 0;

	//cout << a3 % b3 << endl; //取模運算時，除數也不能為0

	//兩個小數不可以取模
	double d1 = 3.14;
	double d2 = 1.1;

	//cout << d1 % d2 << endl;

	system("pause");

	return 0;
}

```

> 總結：只有整型變數可以進行取模運算



**示例3：**

```C++
//遞增
int main() {

	//後置遞增
	int a = 10;
	a++; //等價於a = a + 1
	cout << a << endl; // 11

	//前置遞增
	int b = 10;
	++b;
	cout << b << endl; // 11

	//區別
	//前置遞增先對變數進行++，再計算表達式
	int a2 = 10;
	int b2 = ++a2 * 10;
	cout << b2 << endl;

	//後置遞增先計算表達式，後對變數進行++
	int a3 = 10;
	int b3 = a3++ * 10;
	cout << b3 << endl;

	system("pause");

	return 0;
}

```



> 總結：前置遞增先對變數進行++，再計算表達式，後置遞增相反









### 3.2 賦值運算子

**作用：**用於將表達式的值賦給變數

賦值運算子包括以下幾個符號：

| **運算子** | **術語** | **示例**   | **結果**  |
| ---------- | -------- | ---------- | --------- |
| =          | 賦值     | a=2; b=3;  | a=2; b=3; |
| +=         | 加等於   | a=0; a+=2; | a=2;      |
| -=         | 減等於   | a=5; a-=3; | a=2;      |
| *=         | 乘等於   | a=2; a*=2; | a=4;      |
| /=         | 除等於   | a=4; a/=2; | a=2;      |
| %=         | 模等於   | a=3; a%2;  | a=1;      |



**示例：**

```C++
int main() {

	//賦值運算子

	// =
	int a = 10;
	a = 100;
	cout << "a = " << a << endl;

	// +=
	a = 10;
	a += 2; // a = a + 2;
	cout << "a = " << a << endl;

	// -=
	a = 10;
	a -= 2; // a = a - 2
	cout << "a = " << a << endl;

	// *=
	a = 10;
	a *= 2; // a = a * 2
	cout << "a = " << a << endl;

	// /=
	a = 10;
	a /= 2;  // a = a / 2;
	cout << "a = " << a << endl;

	// %=
	a = 10;
	a %= 2;  // a = a % 2;
	cout << "a = " << a << endl;

	system("pause");

	return 0;
}
```









### 3.3 比較運算子

**作用：**用於表達式的比較，並返回一個真值或假值

比較運算子有以下符號：

| **運算子** | **術語** | **示例** | **結果** |
| ---------- | -------- | -------- | -------- |
| ==         | 相等於   | 4 == 3   | 0        |
| !=         | 不等於   | 4 != 3   | 1        |
| <          | 小於     | 4 < 3    | 0        |
| \>         | 大於     | 4 > 3    | 1        |
| <=         | 小於等於 | 4 <= 3   | 0        |
| \>=        | 大於等於 | 4 >= 1   | 1        |

示例：

```C++
int main() {

	int a = 10;
	int b = 20;

	cout << (a == b) << endl; // 0 

	cout << (a != b) << endl; // 1

	cout << (a > b) << endl; // 0

	cout << (a < b) << endl; // 1

	cout << (a >= b) << endl; // 0

	cout << (a <= b) << endl; // 1
	
	system("pause");

	return 0;
}
```



> 注意：C和C++ 語言的比較運算中， ==“真”用數字“1”來表示， “假”用數字“0”來表示。== 













### 3.4 邏輯運算子

**作用：**用於根據表達式的值返回真值或假值

邏輯運算子有以下符號：

| **運算子** | **術語** | **示例** | **結果**                                                 |
| ---------- | -------- | -------- | -------------------------------------------------------- |
| !          | 非       | !a       | 如果a為假，則!a為真；  如果a為真，則!a為假。             |
| &&         | 與       | a && b   | 如果a和b都為真，則結果為真，否則為假。                   |
| \|\|       | 或       | a \|\| b | 如果a和b有一個為真，則結果為真，二者都為假時，結果為假。 |

**示例1：**邏輯非

```C++
//邏輯運算子  --- 非
int main() {

	int a = 10;

	cout << !a << endl; // 0

	cout << !!a << endl; // 1

	system("pause");

	return 0;
}
```

> 總結： 真變假，假變真





**示例2：**邏輯與

```C++
//邏輯運算子  --- 與
int main() {

	int a = 10;
	int b = 10;

	cout << (a && b) << endl;// 1

	a = 10;
	b = 0;

	cout << (a && b) << endl;// 0 

	a = 0;
	b = 0;

	cout << (a && b) << endl;// 0

	system("pause");

	return 0;
}

```

> 總結：邏輯==與==運算子總結： ==同真為真，其餘為假==







**示例3：**邏輯或

```c++
//邏輯運算子  --- 或
int main() {

	int a = 10;
	int b = 10;

	cout << (a || b) << endl;// 1

	a = 10;
	b = 0;

	cout << (a || b) << endl;// 1 

	a = 0;
	b = 0;

	cout << (a || b) << endl;// 0

	system("pause");

	return 0;
}
```

> 邏輯==或==運算子總結： ==同假為假，其餘為真==

















## 4 程式流程結構

C/C++支援最基本的三種程式運行結構：==順序結構、選擇結構、迴圈結構==

* 順序結構：程式按順序執行，不發生跳轉
* 選擇結構：依據條件是否滿足，有選擇的執行相應功能
* 迴圈結構：依據條件是否滿足，迴圈多次執行某段程式碼



### 4.1 選擇結構

#### 4.1.1 if語句

**作用：**執行滿足條件的語句

if語句的三種形式

* 單行格式if語句

* 多行格式if語句

* 多條件的if語句

  ​

1. 單行格式if語句：`if(條件){ 條件滿足執行的語句 }`

   ![img](assets/clip_image002.png)

   示例：

   ```C++
   int main() {

   	//選擇結構-單行if語句
   	//輸入一個分數，如果分數大於600分，視為考上一本大學，並在螢幕上印出

   	int score = 0;
   	cout << "請輸入一個分數：" << endl;
   	cin >> score;

   	cout << "您輸入的分數為： " << score << endl;

   	//if語句
   	//注意事項，在if判斷語句後面，不要加分號
   	if (score > 600)
   	{
   		cout << "我考上了一本大學！！！" << endl;
   	}

   	system("pause");

   	return 0;
   }
   ```

   ​


> 注意：if條件表達式後不要加分號







2. 多行格式if語句：`if(條件){ 條件滿足執行的語句 }else{ 條件不滿足執行的語句 };`

![img](assets/clip_image002-1541662519170.png)

​

示例：

```C++
int main() {

	int score = 0;

	cout << "請輸入考試分數：" << endl;

	cin >> score;

	if (score > 600)
	{
		cout << "我考上了一本大學" << endl;
	}
	else
	{
		cout << "我未考上一本大學" << endl;
	}

	system("pause");

	return 0;
}
```











3. 多條件的if語句：`if(條件1){ 條件1滿足執行的語句 }else if(條件2){條件2滿足執行的語句}... else{ 都不滿足執行的語句}`

![img](assets/clip_image002-1541662566808.png)

​

​

​

示例：

```C++
	int main() {

	int score = 0;

	cout << "請輸入考試分數：" << endl;

	cin >> score;

	if (score > 600)
	{
		cout << "我考上了一本大學" << endl;
	}
	else if (score > 500)
	{
		cout << "我考上了二本大學" << endl;
	}
	else if (score > 400)
	{
		cout << "我考上了三本大學" << endl;
	}
	else
	{
		cout << "我未考上本科" << endl;
	}

	system("pause");

	return 0;
}
```

​







**嵌套if語句**：在if語句中，可以嵌套使用if語句，達到更精確的條件判斷



案例需求：

* 提示用戶輸入一個高考考試分數，根據分數做如下判斷
* 分數如果大於600分視為考上一本，大於500分考上二本，大於400考上三本，其餘視為未考上本科；
* 在一本分數中，如果大於700分，考入北大，大於650分，考入清華，大於600考入人大。



**示例：**

```c++
int main() {

	int score = 0;

	cout << "請輸入考試分數：" << endl;

	cin >> score;

	if (score > 600)
	{
		cout << "我考上了一本大學" << endl;
		if (score > 700)
		{
			cout << "我考上了北大" << endl;
		}
		else if (score > 650)
		{
			cout << "我考上了清華" << endl;
		}
		else
		{
			cout << "我考上了人大" << endl;
		}
		
	}
	else if (score > 500)
	{
		cout << "我考上了二本大學" << endl;
	}
	else if (score > 400)
	{
		cout << "我考上了三本大學" << endl;
	}
	else
	{
		cout << "我未考上本科" << endl;
	}

	system("pause");

	return 0;
}
```







**練習案例：** 三隻小豬稱體重

有三隻小豬ABC，請分別輸入三隻小豬的體重，並且判斷哪隻小豬最重？![三隻小豬](assets/三隻小豬.jpg)









#### 4.1.2 三目運算子

**作用：** 通過三目運算子實現簡單的判斷

**語法：**`表達式1 ? 表達式2 ：表達式3`

**解釋：**

如果表達式1的值為真，執行表達式2，並返回表達式2的結果；

如果表達式1的值為假，執行表達式3，並返回表達式3的結果。

**示例：**

```C++
int main() {

	int a = 10;
	int b = 20;
	int c = 0;

	c = a > b ? a : b;
	cout << "c = " << c << endl;

	//C++中三目運算子返回的是變數,可以繼續賦值

	(a > b ? a : b) = 100;

	cout << "a = " << a << endl;
	cout << "b = " << b << endl;
	cout << "c = " << c << endl;

	system("pause");

	return 0;
}
```

> 總結：和if語句比較，三目運算子優點是短小整潔，缺點是如果用嵌套，結構不清晰









#### 4.1.3 switch語句

**作用：**執行多條件分支語句

**語法：**

```C++
switch(表達式)

{

	case 結果1：執行語句;break;

	case 結果2：執行語句;break;

	...

	default:執行語句;break;

}

```







**示例：**

```C++
int main() {

	//請給電影評分 
	//10 ~ 9   經典   
	// 8 ~ 7   非常好
	// 6 ~ 5   一般
	// 5分以下 爛片

	int score = 0;
	cout << "請給電影打分" << endl;
	cin >> score;

	switch (score)
	{
	case 10:
	case 9:
		cout << "經典" << endl;
		break;
	case 8:
		cout << "非常好" << endl;
		break;
	case 7:
	case 6:
		cout << "一般" << endl;
		break;
	default:
		cout << "爛片" << endl;
		break;
	}

	system("pause");

	return 0;
}
```



> 注意1：switch語句中表達式型別只能是整型或者字符型

> 注意2：case裡如果沒有break，那麼程式會一直向下執行

> 總結：與if語句比，對於多條件判斷時，switch的結構清晰，執行效率高，缺點是switch不可以判斷區間















### 4.2 迴圈結構

#### 4.2.1 while迴圈語句

**作用：**滿足迴圈條件，執行迴圈語句

**語法：**` while(迴圈條件){ 迴圈語句 }`

**解釋：**==只要迴圈條件的結果為真，就執行迴圈語句==

![img](assets/clip_image002-1541668640382.png)







**示例：**

```C++
int main() {

	int num = 0;
	while (num < 10)
	{
		cout << "num = " << num << endl;
		num++;
	}
	
	system("pause");

	return 0;
}
```



> 注意：在執行迴圈語句時候，程式必須提供跳出迴圈的出口，否則出現死迴圈









**while迴圈練習案例：**==猜數字==

**案例描述：**系統隨機生成一個1到100之間的數字，玩家進行猜測，如果猜錯，提示玩家數字過大或過小，如果猜對恭喜玩家勝利，並且退出遊戲。



![猜數字](assets/猜數字.jpg)

















#### 4.2.2 do...while迴圈語句

**作用：** 滿足迴圈條件，執行迴圈語句

**語法：** `do{ 迴圈語句 } while(迴圈條件);`

**注意：**與while的區別在於==do...while會先執行一次迴圈語句==，再判斷迴圈條件

![img](assets/clip_image002-1541671163478.png)



**示例：**

```C++
int main() {

	int num = 0;

	do
	{
		cout << num << endl;
		num++;

	} while (num < 10);
	
	
	system("pause");

	return 0;
}
```



> 總結：與while迴圈區別在於，do...while先執行一次迴圈語句，再判斷迴圈條件













**練習案例：水仙花數**

**案例描述：**水仙花數是指一個 3 位元元數，它的每個位元元上的數字的 3次冪之和等於它本身

例如：1^3 + 5^3+ 3^3 = 153

請利用do...while語句，求出所有3位元元數中的水仙花數





















#### 4.2.3 for迴圈語句

**作用：** 滿足迴圈條件，執行迴圈語句

**語法：**` for(起始表達式;條件表達式;末尾迴圈體) { 迴圈語句; }`



**示例：**

```C++
int main() {

	for (int i = 0; i < 10; i++)
	{
		cout << i << endl;
	}
	
	system("pause");

	return 0;
}
```







**詳解：**

![1541673704101](assets/1541673704101.png)



> 注意：for迴圈中的表達式，要用分號進行分隔

> 總結：while , do...while, for都是開發中常用的迴圈語句，for迴圈結構比較清晰，比較常用











**練習案例：敲桌子**

案例描述：從1開始數到數字100， 如果數字個位元元含有7，或者數字十位元元含有7，或者該數字是7的倍數，我們印出敲桌子，其餘數字直接印出輸出。

![timg](assets/timg.gif)













#### 4.2.4 嵌套迴圈

**作用：** 在迴圈體中再嵌套一層迴圈，解決一些實際問題

例如我們想在螢幕中印出如下圖片，就需要利用嵌套迴圈

![1541676003486](assets/1541676003486.png)











**示例：**

```C++
int main() {

	//外層迴圈執行1次，內層迴圈執行1輪
	for (int i = 0; i < 10; i++)
	{
		for (int j = 0; j < 10; j++)
		{
			cout << "*" << " ";
		}
		cout << endl;
	}

	system("pause");

	return 0;
}
```













**練習案例：**乘法口訣表

案例描述：利用嵌套迴圈，實現九九乘法表

![0006018857256120_b](assets/0006018857256120_b.jpg)





### 4.3 跳轉語句

#### 4.3.1 break語句

**作用:** 用於跳出==選擇結構==或者==迴圈結構==

break使用的時機：

* 出現在switch條件語句中，作用是終止case並跳出switch
* 出現在迴圈語句中，作用是跳出當前的迴圈語句
* 出現在嵌套迴圈中，跳出最近的內層迴圈語句



**示例1：**

```C++
int main() {
	//1、在switch 語句中使用break
	cout << "請選擇您挑戰副本的難度：" << endl;
	cout << "1、普通" << endl;
	cout << "2、中等" << endl;
	cout << "3、困難" << endl;

	int num = 0;

	cin >> num;

	switch (num)
	{
	case 1:
		cout << "您選擇的是普通難度" << endl;
		break;
	case 2:
		cout << "您選擇的是中等難度" << endl;
		break;
	case 3:
		cout << "您選擇的是困難難度" << endl;
		break;
	}

	system("pause");

	return 0;
}
```



**示例2：**

```C++
int main() {
	//2、在迴圈語句中用break
	for (int i = 0; i < 10; i++)
	{
		if (i == 5)
		{
			break; //跳出迴圈語句
		}
		cout << i << endl;
	}

	system("pause");

	return 0;
}
```



**示例3：**

```C++
int main() {
	//在嵌套迴圈語句中使用break，退出內層迴圈
	for (int i = 0; i < 10; i++)
	{
		for (int j = 0; j < 10; j++)
		{
			if (j == 5)
			{
				break;
			}
			cout << "*" << " ";
		}
		cout << endl;
	}
	
	system("pause");

	return 0;
}
```















#### 4.3.2 continue語句

**作用：**在==迴圈語句==中，跳過本次迴圈中餘下尚未執行的語句，繼續執行下一次迴圈

**示例：**

```C++
int main() {

	for (int i = 0; i < 100; i++)
	{
		if (i % 2 == 0)
		{
			continue;
		}
		cout << i << endl;
	}
	
	system("pause");

	return 0;
}
```



> 注意：continue並沒有使整個迴圈終止，而break會跳出迴圈











#### 4.3.3 goto語句

**作用：**可以無條件跳轉語句



**語法：** `goto 標記;`

**解釋：**如果標記的名稱存在，執行到goto語句時，會跳轉到標記的位元元置



**示例：**

```C++
int main() {

	cout << "1" << endl;

	goto FLAG;

	cout << "2" << endl;
	cout << "3" << endl;
	cout << "4" << endl;

	FLAG:

	cout << "5" << endl;
	
	system("pause");

	return 0;
}
```



> 注意：在程式中不建議使用goto語句，以免造成程式流程混亂













## 5 陣列

### 5.1 概述

所謂陣列，就是一個集合，裡面存放了相同型別的數據元素



**特點1：**陣列中的每個==數據元素都是相同的數據型別==

**特點2：**陣列是由==連續的記憶體==位元元置組成的













![1541748375356](assets/1541748375356.png)













### 5.2 一維陣列

#### 5.2.1 一維陣列定義方式

一維陣列定義的三種方式：

1. ` 數據型別  陣列名[ 陣列長度 ]; `
2. `數據型別  陣列名[ 陣列長度 ] = { 值1，值2 ...};`
3. `數據型別  陣列名[ ] = { 值1，值2 ...};`



示例

```C++
int main() {

	//定義方式1
	//數據型別 陣列名[元素個數];
	int score[10];

	//利用下標賦值
	score[0] = 100;
	score[1] = 99;
	score[2] = 85;

	//利用下標輸出
	cout << score[0] << endl;
	cout << score[1] << endl;
	cout << score[2] << endl;


	//第二種定義方式
	//數據型別 陣列名[元素個數] =  {值1，值2 ，值3 ...};
	//如果{}內不足10個數據，剩餘數據用0補全
	int score2[10] = { 100, 90,80,70,60,50,40,30,20,10 };
	
	//逐個輸出
	//cout << score2[0] << endl;
	//cout << score2[1] << endl;

	//一個一個輸出太麻煩，因此可以利用迴圈進行輸出
	for (int i = 0; i < 10; i++)
	{
		cout << score2[i] << endl;
	}

	//定義方式3
	//數據型別 陣列名[] =  {值1，值2 ，值3 ...};
	int score3[] = { 100,90,80,70,60,50,40,30,20,10 };

	for (int i = 0; i < 10; i++)
	{
		cout << score3[i] << endl;
	}

	system("pause");

	return 0;
}
```



> 總結1：陣列名的命名規範與變數名命名規範一致，不要和變數重名

> 總結2：陣列中下標是從0開始索引









#### 5.2.2 一維陣列陣列名

一維陣列名稱的**用途**：

1. 可以統計整個陣列在記憶體中的長度
2. 可以獲取陣列在記憶體中的首地址





**示例：**

```C++
int main() {

	//陣列名用途
	//1、可以獲取整個陣列佔用記憶體空間大小
	int arr[10] = { 1,2,3,4,5,6,7,8,9,10 };

	cout << "整個陣列所佔記憶體空間為： " << sizeof(arr) << endl;
	cout << "每個元素所佔記憶體空間為： " << sizeof(arr[0]) << endl;
	cout << "陣列的元素個數為： " << sizeof(arr) / sizeof(arr[0]) << endl;

	//2、可以通過陣列名獲取到陣列首地址
	cout << "陣列首地址為： " << (int)arr << endl;
	cout << "陣列中第一個元素地址為： " << (int)&arr[0] << endl;
	cout << "陣列中第二個元素地址為： " << (int)&arr[1] << endl;

	//arr = 100; 錯誤，陣列名是常數，因此不可以賦值


	system("pause");

	return 0;
}
```



> 注意：陣列名是常數，不可以賦值

> 總結1：直接印出陣列名，可以查看陣列所佔記憶體的首地址

>總結2：對陣列名進行sizeof，可以獲取整個陣列佔記憶體空間的大小











**練習案例1**：五隻小豬稱體重

**案例描述：**

在一個陣列中記錄了五隻小豬的體重，如：int arr[5] = {300,350,200,400,250};

找出並印出最重的小豬體重。









**練習案例2：**陣列元素逆置

**案例描述：**請聲明一個5個元素的陣列，並且將元素逆置.

(如原陣列元素為：1,3,2,5,4;逆置後輸出結果為:4,5,2,3,1);

















#### 5.2.3 冒泡排序

**作用：** 最常用的排序演演算法，對陣列內元素進行排序

1. 比較相鄰的元素。如果第一個比第二個大，就交換他們兩個。
2. 對每一對相鄰元素做同樣的工作，執行完畢後，找到第一個最大值。
3. 重複以上的步驟，每次比較次數-1，直到不需要比較

![1541905327273](assets/1541905327273.png)

**示例：** 將陣列 { 4,2,8,0,5,7,1,3,9 } 進行升序排序

```C++
int main() {

	int arr[9] = { 4,2,8,0,5,7,1,3,9 };

	for (int i = 0; i < 9 - 1; i++)
	{
		for (int j = 0; j < 9 - 1 - i; j++)
		{
			if (arr[j] > arr[j + 1])
			{
				int temp = arr[j];
				arr[j] = arr[j + 1];
				arr[j + 1] = temp;
			}
		}
	}

	for (int i = 0; i < 9; i++)
	{
		cout << arr[i] << endl;
	}
    
	system("pause");

	return 0;
}
```









### 5.3 二維陣列

二維陣列就是在一維陣列上，多加一個維度。

![1541905559138](assets/1541905559138.png)

#### 5.3.1 二維陣列定義方式

二維陣列定義的四種方式：

1. ` 數據型別  陣列名[ 行數 ][ 列數 ]; `
2. `數據型別  陣列名[ 行數 ][ 列數 ] = { {數據1，數據2 } ，{數據3，數據4 } };`
3. `數據型別  陣列名[ 行數 ][ 列數 ] = { 數據1，數據2，數據3，數據4};`
4. ` 數據型別  陣列名[  ][ 列數 ] = { 數據1，數據2，數據3，數據4};`



> 建議：以上4種定義方式，利用==第二種更加直觀，提高程式碼的可讀性==

示例：

```C++
int main() {

	//方式1  
	//陣列型別 陣列名 [行數][列數]
	int arr[2][3];
	arr[0][0] = 1;
	arr[0][1] = 2;
	arr[0][2] = 3;
	arr[1][0] = 4;
	arr[1][1] = 5;
	arr[1][2] = 6;

	for (int i = 0; i < 2; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			cout << arr[i][j] << " ";
		}
		cout << endl;
	}

	//方式2 
	//數據型別 陣列名[行數][列數] = { {數據1，數據2 } ，{數據3，數據4 } };
	int arr2[2][3] =
	{
		{1,2,3},
		{4,5,6}
	};

	//方式3
	//數據型別 陣列名[行數][列數] = { 數據1，數據2 ,數據3，數據4  };
	int arr3[2][3] = { 1,2,3,4,5,6 }; 

	//方式4 
	//數據型別 陣列名[][列數] = { 數據1，數據2 ,數據3，數據4  };
	int arr4[][3] = { 1,2,3,4,5,6 };
	
	system("pause");

	return 0;
}
```



> 總結：在定義二維陣列時，如果初始化了數據，可以省略行數













#### 5.3.2 二維陣列陣列名



* 查看二維陣列所佔記憶體空間
* 獲取二維陣列首地址





**示例：**

```C++
int main() {

	//二維陣列陣列名
	int arr[2][3] =
	{
		{1,2,3},
		{4,5,6}
	};

	cout << "二維陣列大小： " << sizeof(arr) << endl;
	cout << "二維陣列一行大小： " << sizeof(arr[0]) << endl;
	cout << "二維陣列元素大小： " << sizeof(arr[0][0]) << endl;

	cout << "二維陣列行數： " << sizeof(arr) / sizeof(arr[0]) << endl;
	cout << "二維陣列列數： " << sizeof(arr[0]) / sizeof(arr[0][0]) << endl;

	//地址
	cout << "二維陣列首地址：" << arr << endl;
	cout << "二維陣列第一行地址：" << arr[0] << endl;
	cout << "二維陣列第二行地址：" << arr[1] << endl;

	cout << "二維陣列第一個元素地址：" << &arr[0][0] << endl;
	cout << "二維陣列第二個元素地址：" << &arr[0][1] << endl;

	system("pause");

	return 0;
}
```



> 總結1：二維陣列名就是這個陣列的首地址

> 總結2：對二維陣列名進行sizeof時，可以獲取整個二維陣列佔用的記憶體空間大小













#### **5.3.3 二維陣列應用案例**

**考試成績統計：**

案例描述：有三名同學（張三，李四，王五），在一次考試中的成績分別如下表，**請分別輸出三名同學的總成績**

|      | 語文 | 數學 | 英語 |
| ---- | ---- | ---- | ---- |
| 張三 | 100  | 100  | 100  |
| 李四 | 90   | 50   | 100  |
| 王五 | 60   | 70   | 80   |





**參考答案：**

```C++
int main() {

	int scores[3][3] =
	{
		{100,100,100},
		{90,50,100},
		{60,70,80},
	};

	string names[3] = { "張三","李四","王五" };

	for (int i = 0; i < 3; i++)
	{
		int sum = 0;
		for (int j = 0; j < 3; j++)
		{
			sum += scores[i][j];
		}
		cout << names[i] << "同學總成績為： " << sum << endl;
	}

	system("pause");

	return 0;
}
```













## 6 函式

### 6.1 概述

**作用：**將一段經常使用的程式碼封裝起來，減少重複程式碼

一個較大的程式，一般分為若干個程式塊，每個模組實現特定的功能。

### 6.2 函式的定義

函式的定義一般主要有5個步驟：

1、回傳值型別 

2、函式名

3、參數表列

4、函式體語句 

5、return 表達式

**語法：** 

```C++
回傳值型別 函式名 （參數列表）
{

       函式體語句

       return表達式

}
```



* 回傳值型別 ：一個函式可以返回一個值。在函式定義中
* 函式名：給函式起個名稱
* 參數列表：使用該函式時，傳入的數據
* 函式體語句：花括號內的程式碼，函式內需要執行的語句
* return表達式： 和回傳值型別掛鉤，函式執行完後，返回相應的數據





**示例：**定義一個加法函式，實現兩個數相加

```C++
//函式定義
int add(int num1, int num2)
{
	int sum = num1 + num2;
	return sum;
}
```











### 6.3 函式的調用

**功能：**使用定義好的函式

**語法：**` 函式名（參數）`

**示例：**

```C++
//函式定義
int add(int num1, int num2) //定義中的num1,num2稱為形式參數，簡稱形式參數
{
	int sum = num1 + num2;
	return sum;
}

int main() {

	int a = 10;
	int b = 10;
	//調用add函式
	int sum = add(a, b);//調用時的a，b稱為實際參數，簡稱實際參數
	cout << "sum = " << sum << endl;

	a = 100;
	b = 100;

	sum = add(a, b);
	cout << "sum = " << sum << endl;

	system("pause");

	return 0;
}
```

> 總結：函式定義裡小括號內稱為形式參數，函式調用時傳入的參數稱為實際參數









### 6.4 值傳遞

* 所謂值傳遞，就是函式調用時實際參數將數值傳入給形式參數
* 值傳遞時，==如果形式參數發生，並不會影響實際參數==



**示例：**

```C++
void swap(int num1, int num2)
{
	cout << "交換前：" << endl;
	cout << "num1 = " << num1 << endl;
	cout << "num2 = " << num2 << endl;

	int temp = num1;
	num1 = num2;
	num2 = temp;

	cout << "交換後：" << endl;
	cout << "num1 = " << num1 << endl;
	cout << "num2 = " << num2 << endl;

	//return ; 當函式聲明時候，不需要回傳值，可以不寫return
}

int main() {

	int a = 10;
	int b = 20;

	swap(a, b);

	cout << "mian中的 a = " << a << endl;
	cout << "mian中的 b = " << b << endl;

	system("pause");

	return 0;
}
```



> 總結： 值傳遞時，形式參數是修飾不了實際參數的









### **6.5 函式的常見樣式**

常見的函式樣式有4種

1. 無參無返
2. 有參無返
3. 無參有返
4. 有參有返

**示例：**

```C++
//函式常見樣式
//1、 無參無返
void test01()
{
	//void a = 10; //無型別不可以創建變數,原因無法分配記憶體
	cout << "this is test01" << endl;
	//test01(); 函式調用
}

//2、 有參無返
void test02(int a)
{
	cout << "this is test02" << endl;
	cout << "a = " << a << endl;
}

//3、無參有返
int test03()
{
	cout << "this is test03 " << endl;
	return 10;
}

//4、有參有返
int test04(int a, int b)
{
	cout << "this is test04 " << endl;
	int sum = a + b;
	return sum;
}
```











### 6.6 函式的聲明

**作用：** 告訴編譯器函式名稱及如何調用函式。函式的實際主體可以單獨定義。



*  函式的**聲明可以多次**，但是函式的**定義只能有一次**



**示例：**

```C++
//聲明可以多次，定義只能一次
//聲明
int max(int a, int b);
int max(int a, int b);
//定義
int max(int a, int b)
{
	return a > b ? a : b;
}

int main() {

	int a = 100;
	int b = 200;

	cout << max(a, b) << endl;

	system("pause");

	return 0;
}
```











### 6.7 函式的分檔案編寫

**作用：**讓程式碼結構更加清晰

函式分檔案編寫一般有4個步驟

1. 創建後綴名為.h的頭檔案  
2. 創建後綴名為.cpp的原始檔
3. 在頭檔案中寫函式的聲明
4. 在原始檔中寫函式的定義

**示例：**

```C++
//swap.h檔案
#include<iostream>
using namespace std;

//實現兩個數字交換的函式聲明
void swap(int a, int b);

```

```C++
//swap.cpp檔案
#include "swap.h"

void swap(int a, int b)
{
	int temp = a;
	a = b;
	b = temp;

	cout << "a = " << a << endl;
	cout << "b = " << b << endl;
}
```

```C++
//main函式檔案
#include "swap.h"
int main() {

	int a = 100;
	int b = 200;
	swap(a, b);

	system("pause");

	return 0;
}

```













## 7 指標

### 7.1 指標的基本概念

**指標的作用：** 可以通過指標間接訪問記憶體



* 記憶體編號是從0開始記錄的，一般用十六進制數字表示
* 可以利用指標變數保存地址

  ​

### 7.2 指標變數的定義和使用

指標變數定義語法： `數據型別 * 變數名；`

**示例：**

```C++
int main() {

	//1、指標的定義
	int a = 10; //定義整型變數a
	
	//指標定義語法： 數據型別 * 變數名 ;
	int * p;

	//指標變數賦值
	p = &a; //指標指向變數a的地址
	cout << &a << endl; //印出數據a的地址
	cout << p << endl;  //印出指標變數p

	//2、指標的使用
	//通過*操作指標變數指向的記憶體
	cout << "*p = " << *p << endl;

	system("pause");

	return 0;
}
```



指標變數和普通變數的區別

* 普通變數存放的是數據,指標變數存放的是地址
* 指標變數可以通過" * "操作符，操作指標變數指向的記憶體空間，這個過程稱為解參照



> 總結1： 我們可以通過 & 符號 獲取變數的地址

> 總結2：利用指標可以記錄地址

> 總結3：對指標變數解參照，可以操作指標指向的記憶體











### 7.3 指標所佔記憶體空間



提問：指標也是種數據型別，那麼這種數據型別佔用多少記憶體空間？



**示例：**

```C++
int main() {

	int a = 10;

	int * p;
	p = &a; //指標指向數據a的地址

	cout << *p << endl; //* 解參照
	cout << sizeof(p) << endl;
	cout << sizeof(char *) << endl;
	cout << sizeof(float *) << endl;
	cout << sizeof(double *) << endl;

	system("pause");

	return 0;
}
```



> 總結：所有指標型別在32位元元作業系統下是4個位元元組











### 7.4 空指標和野指標

**空指標**：指標變數指向記憶體中編號為0的空間

**用途：**初始化指標變數

**注意：**空指標指向的記憶體是不可以訪問的



**示例1：空指標**

```C++
int main() {

	//指標變數p指向記憶體地址編號為0的空間
	int * p = NULL;

	//訪問空指標報錯 
	//記憶體編號0 ~255為系統佔用記憶體，不允許用戶訪問
	cout << *p << endl;

	system("pause");

	return 0;
}
```















**野指標**：指標變數指向非法的記憶體空間

**示例2：野指標**

```C++
int main() {

	//指標變數p指向記憶體地址編號為0x1100的空間
	int * p = (int *)0x1100;

	//訪問野指標報錯 
	cout << *p << endl;

	system("pause");

	return 0;
}
```





> 總結：空指標和野指標都不是我們申請的空間，因此不要訪問。









### 7.5 const修飾指標

const修飾指標有三種情況

1. const修飾指標   --- 常數指標
2. const修飾常數   --- 指標常數
3. const即修飾指標，又修飾常數




**示例：**


```c++
int main() {

	int a = 10;
	int b = 10;

	//const修飾的是指標，指標指向可以改，指標指向的值不可以更改
	const int * p1 = &a; 
	p1 = &b; //正確
	//*p1 = 100;  報錯
	

	//const修飾的是常數，指標指向不可以改，指標指向的值可以更改
	int * const p2 = &a;
	//p2 = &b; //錯誤
	*p2 = 100; //正確

    //const既修飾指標又修飾常數
	const int * const p3 = &a;
	//p3 = &b; //錯誤
	//*p3 = 100; //錯誤

	system("pause");

	return 0;
}
```



> 技巧：看const右側緊跟著的是指標還是常數, 是指標就是常數指標，是常數就是指標常數









### 7.6 指標和陣列

**作用：**利用指標訪問陣列中元素

**示例：**

```C++
int main() {

	int arr[] = { 1,2,3,4,5,6,7,8,9,10 };

	int * p = arr;  //指向陣列的指標

	cout << "第一個元素： " << arr[0] << endl;
	cout << "指標訪問第一個元素： " << *p << endl;

	for (int i = 0; i < 10; i++)
	{
		//利用指標走訪陣列
		cout << *p << endl;
		p++;
	}

	system("pause");

	return 0;
}
```











### 7.7 指標和函式

**作用：**利用指標作函式參數，可以修改實際參數的值



**示例：**

```C++
//值傳遞
void swap1(int a ,int b)
{
	int temp = a;
	a = b; 
	b = temp;
}
//地址傳遞
void swap2(int * p1, int *p2)
{
	int temp = *p1;
	*p1 = *p2;
	*p2 = temp;
}

int main() {

	int a = 10;
	int b = 20;
	swap1(a, b); // 值傳遞不會改變實際參數

	swap2(&a, &b); //地址傳遞會改變實際參數

	cout << "a = " << a << endl;

	cout << "b = " << b << endl;

	system("pause");

	return 0;
}
```



> 總結：如果不想修改實際參數，就用值傳遞，如果想修改實際參數，就用地址傳遞













### 7.8 指標、陣列、函式

**案例描述：**封裝一個函式，利用冒泡排序，實現對整型陣列的升序排序

例如陣列：int arr[10] = { 4,3,6,9,1,2,10,8,7,5 };



**示例：**

```c++
//冒泡排序函式
void bubbleSort(int * arr, int len)  //int * arr 也可以寫為int arr[]
{
	for (int i = 0; i < len - 1; i++)
	{
		for (int j = 0; j < len - 1 - i; j++)
		{
			if (arr[j] > arr[j + 1])
			{
				int temp = arr[j];
				arr[j] = arr[j + 1];
				arr[j + 1] = temp;
			}
		}
	}
}

//印出陣列函式
void printArray(int arr[], int len)
{
	for (int i = 0; i < len; i++)
	{
		cout << arr[i] << endl;
	}
}

int main() {

	int arr[10] = { 4,3,6,9,1,2,10,8,7,5 };
	int len = sizeof(arr) / sizeof(int);

	bubbleSort(arr, len);

	printArray(arr, len);

	system("pause");

	return 0;
}
```



> 總結：當陣列名傳入到函式作為參數時，被退化為指向首元素的指標









## 8 結構

### 8.1 結構基本概念

結構屬於用戶==自定義的數據型別==，允許用戶存儲不同的數據型別



### 8.2 結構定義和使用

**語法：**`struct 結構名 { 結構成員列表 }；`

通過結構創建變數的方式有三種：

* struct 結構名 變數名
* struct 結構名 變數名 = { 成員1值 ， 成員2值...}
* 定義結構時順便創建變數

**示例：**

```C++
//結構定義
struct student
{
	//成員列表
	string name;  //姓名
	int age;      //年齡
	int score;    //分數
}stu3; //結構變數創建方式3 


int main() {

	//結構變數創建方式1
	struct student stu1; //struct 關鍵字可以省略

	stu1.name = "張三";
	stu1.age = 18;
	stu1.score = 100;
	
	cout << "姓名：" << stu1.name << " 年齡：" << stu1.age  << " 分數：" << stu1.score << endl;

	//結構變數創建方式2
	struct student stu2 = { "李四",19,60 };

	cout << "姓名：" << stu2.name << " 年齡：" << stu2.age  << " 分數：" << stu2.score << endl;


	stu3.name = "王五";
	stu3.age = 18;
	stu3.score = 80;
	

	cout << "姓名：" << stu3.name << " 年齡：" << stu3.age  << " 分數：" << stu3.score << endl;

	system("pause");

	return 0;
}
```



> 總結1：定義結構時的關鍵字是struct，不可省略

> 總結2：創建結構變數時，關鍵字struct可以省略

> 總結3：結構變數利用操作符 ''.''  訪問成員









### 8.3 結構陣列

**作用：**將自定義的結構放入到陣列中方便維護

**語法：**` struct  結構名 陣列名[元素個數] = {  {} , {} , ... {} }`

**示例：**

```C++
//結構定義
struct student
{
	//成員列表
	string name;  //姓名
	int age;      //年齡
	int score;    //分數
}

int main() {
	
	//結構陣列
	struct student arr[3]=
	{
		{"張三",18,80 },
		{"李四",19,60 },
		{"王五",20,70 }
	};

	for (int i = 0; i < 3; i++)
	{
		cout << "姓名：" << arr[i].name << " 年齡：" << arr[i].age << " 分數：" << arr[i].score << endl;
	}

	system("pause");

	return 0;
}
```











### 8.4 結構指標

**作用：**通過指標訪問結構中的成員



* 利用操作符 `-> `可以通過結構指標訪問結構屬性



**示例：**

```C++
//結構定義
struct student
{
	//成員列表
	string name;  //姓名
	int age;      //年齡
	int score;    //分數
};


int main() {
	
	struct student stu = { "張三",18,100, };
	
	struct student * p = &stu;
	
	p->score = 80; //指標通過 -> 操作符可以訪問成員

	cout << "姓名：" << p->name << " 年齡：" << p->age << " 分數：" << p->score << endl;
	
	system("pause");

	return 0;
}
```



> 總結：結構指標可以通過 -> 操作符 來訪問結構中的成員













### 8.5 結構嵌套結構

**作用：** 結構中的成員可以是另一個結構

**例如：**每個老師輔導一個學員，一個老師的結構中，記錄一個學生的結構

**示例：**

```C++
//學生結構定義
struct student
{
	//成員列表
	string name;  //姓名
	int age;      //年齡
	int score;    //分數
};

//教師結構定義
struct teacher
{
    //成員列表
	int id; //職工編號
	string name;  //教師姓名
	int age;   //教師年齡
	struct student stu; //子結構 學生
};


int main() {

	struct teacher t1;
	t1.id = 10000;
	t1.name = "老王";
	t1.age = 40;

	t1.stu.name = "張三";
	t1.stu.age = 18;
	t1.stu.score = 100;

	cout << "教師 職工編號： " << t1.id << " 姓名： " << t1.name << " 年齡： " << t1.age << endl;
	
	cout << "輔導學員 姓名： " << t1.stu.name << " 年齡：" << t1.stu.age << " 考試分數： " << t1.stu.score << endl;

	system("pause");

	return 0;
}
```



**總結：**在結構中可以定義另一個結構作為成員，用來解決實際問題









### 8.6 結構做函式參數 

**作用：**將結構作為參數向函式中傳遞

傳遞方式有兩種：

* 值傳遞
* 地址傳遞

**示例：**

```C++
//學生結構定義
struct student
{
	//成員列表
	string name;  //姓名
	int age;      //年齡
	int score;    //分數
};

//值傳遞
void printStudent(student stu )
{
	stu.age = 28;
	cout << "子函式中 姓名：" << stu.name << " 年齡： " << stu.age  << " 分數：" << stu.score << endl;
}

//地址傳遞
void printStudent2(student *stu)
{
	stu->age = 28;
	cout << "子函式中 姓名：" << stu->name << " 年齡： " << stu->age  << " 分數：" << stu->score << endl;
}

int main() {

	student stu = { "張三",18,100};
	//值傳遞
	printStudent(stu);
	cout << "主函式中 姓名：" << stu.name << " 年齡： " << stu.age << " 分數：" << stu.score << endl;

	cout << endl;

	//地址傳遞
	printStudent2(&stu);
	cout << "主函式中 姓名：" << stu.name << " 年齡： " << stu.age  << " 分數：" << stu.score << endl;

	system("pause");

	return 0;
}
```

> 總結：如果不想修改主函式中的數據，用值傳遞，反之用地址傳遞







### 8.7 結構中 const使用場景

**作用：**用const來防止誤操作

**示例：**

```C++
//學生結構定義
struct student
{
	//成員列表
	string name;  //姓名
	int age;      //年齡
	int score;    //分數
};

//const使用場景
void printStudent(const student *stu) //加const防止函式體中的誤操作
{
	//stu->age = 100; //操作失敗，因為加了const修飾
	cout << "姓名：" << stu->name << " 年齡：" << stu->age << " 分數：" << stu->score << endl;

}

int main() {

	student stu = { "張三",18,100 };

	printStudent(&stu);

	system("pause");

	return 0;
}
```









### 8.8 結構案例

#### 8.8.1 案例1

**案例描述：**

學校正在做畢設專案，每名老師帶領5個學生，總共有3名老師，需求如下

設計學生和老師的結構，其中在老師的結構中，有老師姓名和一個存放5名學生的陣列作為成員

學生的成員有姓名、考試分數，創建陣列存放3名老師，通過函式給每個老師及所帶的學生賦值

最終印出出老師數據以及老師所帶的學生數據。



**示例：**

```C++
struct Student
{
	string name;
	int score;
};
struct Teacher
{
	string name;
	Student sArray[5];
};

void allocateSpace(Teacher tArray[] , int len)
{
	string tName = "教師";
	string sName = "學生";
	string nameSeed = "ABCDE";
	for (int i = 0; i < len; i++)
	{
		tArray[i].name = tName + nameSeed[i];
		
		for (int j = 0; j < 5; j++)
		{
			tArray[i].sArray[j].name = sName + nameSeed[j];
			tArray[i].sArray[j].score = rand() % 61 + 40;
		}
	}
}

void printTeachers(Teacher tArray[], int len)
{
	for (int i = 0; i < len; i++)
	{
		cout << tArray[i].name << endl;
		for (int j = 0; j < 5; j++)
		{
			cout << "\t姓名：" << tArray[i].sArray[j].name << " 分數：" << tArray[i].sArray[j].score << endl;
		}
	}
}

int main() {

	srand((unsigned int)time(NULL)); //隨機數種子 頭檔案 #include <ctime>

	Teacher tArray[3]; //老師陣列

	int len = sizeof(tArray) / sizeof(Teacher);

	allocateSpace(tArray, len); //創建數據

	printTeachers(tArray, len); //印出數據
	
	system("pause");

	return 0;
}
```









#### 8.8.2 案例2

**案例描述：**

設計一個英雄的結構，包括成員姓名，年齡，性別;創建結構陣列，陣列中存放5名英雄。

通過冒泡排序的演演算法，將陣列中的英雄按照年齡進行升序排序，最終印出排序後的結果。



五名英雄資訊如下：

```C++
		{"劉備",23,"男"},
		{"關羽",22,"男"},
		{"張飛",20,"男"},
		{"趙雲",21,"男"},
		{"貂蟬",19,"女"},
```









**示例：**

```C++
//英雄結構
struct hero
{
	string name;
	int age;
	string sex;
};
//冒泡排序
void bubbleSort(hero arr[] , int len)
{
	for (int i = 0; i < len - 1; i++)
	{
		for (int j = 0; j < len - 1 - i; j++)
		{
			if (arr[j].age > arr[j + 1].age)
			{
				hero temp = arr[j];
				arr[j] = arr[j + 1];
				arr[j + 1] = temp;
			}
		}
	}
}
//印出陣列
void printHeros(hero arr[], int len)
{
	for (int i = 0; i < len; i++)
	{
		cout << "姓名： " << arr[i].name << " 性別： " << arr[i].sex << " 年齡： " << arr[i].age << endl;
	}
}

int main() {

	struct hero arr[5] =
	{
		{"劉備",23,"男"},
		{"關羽",22,"男"},
		{"張飛",20,"男"},
		{"趙雲",21,"男"},
		{"貂蟬",19,"女"},
	};

	int len = sizeof(arr) / sizeof(hero); //獲取陣列元素個數

	bubbleSort(arr, len); //排序

	printHeros(arr, len); //印出

	system("pause");

	return 0;
}
```



# 