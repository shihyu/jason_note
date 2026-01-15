# C++核心編程

本階段主要針對C++==面向對象==編程技術做詳細講解，探討C++中的核心和精髓。



## 1 內存分區模型

C++程序在執行時，將內存大方向劃分為**4個區域**

- 代碼區：存放函數體的二進制代碼，由操作系統進行管理的
- 全局區：存放全局變量和靜態變量以及常量
- 棧區：由編譯器自動分配釋放, 存放函數的參數值,局部變量等
- 堆區：由程序員分配和釋放,若程序員不釋放,程序結束時由操作系統回收







**內存四區意義：**

不同區域存放的數據，賦予不同的生命週期, 給我們更大的靈活編程





### 1.1 程序運行前

​	在程序編譯後，生成了exe可執行程序，**未執行該程序前**分為兩個區域

​	**代碼區：**

​		存放 CPU 執行的機器指令

​		代碼區是**共享**的，共享的目的是對於頻繁被執行的程序，只需要在內存中有一份代碼即可

​		代碼區是**只讀**的，使其只讀的原因是防止程序意外地修改了它的指令

​	**全局區：**

​		全局變量和靜態變量存放在此.

​		全局區還包含了常量區, 字符串常量和其他常量也存放在此.

​		==該區域的數據在程序結束後由操作系統釋放==.













**示例：**

```c++
//全局變量
int g_a = 10;
int g_b = 10;

//全局常量
const int c_g_a = 10;
const int c_g_b = 10;

int main() {

	//局部變量
	int a = 10;
	int b = 10;

	//打印地址
	cout << "局部變量a地址為： " << (int)&a << endl;
	cout << "局部變量b地址為： " << (int)&b << endl;

	cout << "全局變量g_a地址為： " <<  (int)&g_a << endl;
	cout << "全局變量g_b地址為： " <<  (int)&g_b << endl;

	//靜態變量
	static int s_a = 10;
	static int s_b = 10;

	cout << "靜態變量s_a地址為： " << (int)&s_a << endl;
	cout << "靜態變量s_b地址為： " << (int)&s_b << endl;

	cout << "字符串常量地址為： " << (int)&"hello world" << endl;
	cout << "字符串常量地址為： " << (int)&"hello world1" << endl;

	cout << "全局常量c_g_a地址為： " << (int)&c_g_a << endl;
	cout << "全局常量c_g_b地址為： " << (int)&c_g_b << endl;

	const int c_l_a = 10;
	const int c_l_b = 10;
	cout << "局部常量c_l_a地址為： " << (int)&c_l_a << endl;
	cout << "局部常量c_l_b地址為： " << (int)&c_l_b << endl;

	system("pause");

	return 0;
}
```

打印結果：

![1545017602518](assets/1545017602518.png)



總結：

* C++中在程序運行前分為全局區和代碼區
* 代碼區特點是共享和只讀
* 全局區中存放全局變量、靜態變量、常量
* 常量區中存放 const修飾的全局常量  和 字符串常量






### 1.2 程序運行後



​	**棧區：**

​		由編譯器自動分配釋放, 存放函數的參數值,局部變量等

​		注意事項：不要返回局部變量的地址，棧區開闢的數據由編譯器自動釋放



**示例：**

```c++
int * func()
{
	int a = 10;
	return &a;
}

int main() {

	int *p = func();

	cout << *p << endl;
	cout << *p << endl;

	system("pause");

	return 0;
}
```







​	**堆區：**

​		由程序員分配釋放,若程序員不釋放,程序結束時由操作系統回收

​		在C++中主要利用new在堆區開闢內存

**示例：**

```c++
int* func()
{
	int* a = new int(10);
	return a;
}

int main() {

	int *p = func();

	cout << *p << endl;
	cout << *p << endl;
    
	system("pause");

	return 0;
}
```



**總結：**

堆區數據由程序員管理開闢和釋放

堆區數據利用new關鍵字進行開闢內存









### 1.3 new操作符



​	C++中利用==new==操作符在堆區開闢數據

​	堆區開闢的數據，由程序員手動開闢，手動釋放，釋放利用操作符 ==delete==

​	語法：` new 數據類型`

​	利用new創建的數據，會返回該數據對應的類型的指針



**示例1： 基本語法**

```c++
int* func()
{
	int* a = new int(10);
	return a;
}

int main() {

	int *p = func();

	cout << *p << endl;
	cout << *p << endl;

	//利用delete釋放堆區數據
	delete p;

	//cout << *p << endl; //報錯，釋放的空間不可訪問

	system("pause");

	return 0;
}
```



**示例2：開闢數組**

```c++
//堆區開闢數組
int main() {

	int* arr = new int[10];

	for (int i = 0; i < 10; i++)
	{
		arr[i] = i + 100;
	}

	for (int i = 0; i < 10; i++)
	{
		cout << arr[i] << endl;
	}
	//釋放數組 delete 後加 []
	delete[] arr;

	system("pause");

	return 0;
}

```











## 2 引用

### 2.1 引用的基本使用

**作用： **給變量起別名

**語法：** `數據類型 &別名 = 原名`



**示例：**

```C++
int main() {

	int a = 10;
	int &b = a;

	cout << "a = " << a << endl;
	cout << "b = " << b << endl;

	b = 100;

	cout << "a = " << a << endl;
	cout << "b = " << b << endl;

	system("pause");

	return 0;
}
```







### 2.2 引用注意事項

* 引用必須初始化
* 引用在初始化後，不可以改變

示例：

```C++
int main() {

	int a = 10;
	int b = 20;
	//int &c; //錯誤，引用必須初始化
	int &c = a; //一旦初始化後，就不可以更改
	c = b; //這是賦值操作，不是更改引用

	cout << "a = " << a << endl;
	cout << "b = " << b << endl;
	cout << "c = " << c << endl;

	system("pause");

	return 0;
}
```











### 2.3 引用做函數參數

**作用：**函數傳參時，可以利用引用的技術讓形參修飾實參

**優點：**可以簡化指針修改實參



**示例：**

```C++
//1. 值傳遞
void mySwap01(int a, int b) {
	int temp = a;
	a = b;
	b = temp;
}

//2. 地址傳遞
void mySwap02(int* a, int* b) {
	int temp = *a;
	*a = *b;
	*b = temp;
}

//3. 引用傳遞
void mySwap03(int& a, int& b) {
	int temp = a;
	a = b;
	b = temp;
}

int main() {

	int a = 10;
	int b = 20;

	mySwap01(a, b);
	cout << "a:" << a << " b:" << b << endl;

	mySwap02(&a, &b);
	cout << "a:" << a << " b:" << b << endl;

	mySwap03(a, b);
	cout << "a:" << a << " b:" << b << endl;

	system("pause");

	return 0;
}

```



> 總結：通過引用參數產生的效果同按地址傳遞是一樣的。引用的語法更清楚簡單













### 2.4 引用做函數返回值



作用：引用是可以作為函數的返回值存在的



注意：**不要返回局部變量引用**

用法：函數調用作為左值



**示例：**

```C++
//返回局部變量引用
int& test01() {
	int a = 10; //局部變量
	return a;
}

//返回靜態變量引用
int& test02() {
	static int a = 20;
	return a;
}

int main() {

	//不能返回局部變量的引用
	int& ref = test01();
	cout << "ref = " << ref << endl;
	cout << "ref = " << ref << endl;

	//如果函數做左值，那麼必須返回引用
	int& ref2 = test02();
	cout << "ref2 = " << ref2 << endl;
	cout << "ref2 = " << ref2 << endl;

	test02() = 1000;

	cout << "ref2 = " << ref2 << endl;
	cout << "ref2 = " << ref2 << endl;

	system("pause");

	return 0;
}
```





​	









### 2.5 引用的本質

本質：**引用的本質在c++內部實現是一個指針常量.**

講解示例：

```C++
//發現是引用，轉換為 int* const ref = &a;
void func(int& ref){
	ref = 100; // ref是引用，轉換為*ref = 100
}
int main(){
	int a = 10;
    
    //自動轉換為 int* const ref = &a; 指針常量是指針指向不可改，也說明為什麼引用不可更改
	int& ref = a; 
	ref = 20; //內部發現ref是引用，自動幫我們轉換為: *ref = 20;
    
	cout << "a:" << a << endl;
	cout << "ref:" << ref << endl;
    
	func(a);
	return 0;
}
```

結論：C++推薦用引用技術，因為語法方便，引用本質是指針常量，但是所有的指針操作編譯器都幫我們做了













### 2.6 常量引用



**作用：**常量引用主要用來修飾形參，防止誤操作



在函數形參列表中，可以加==const修飾形參==，防止形參改變實參



**示例：**



```C++
//引用使用的場景，通常用來修飾形參
void showValue(const int& v) {
	//v += 10;
	cout << v << endl;
}

int main() {

	//int& ref = 10;  引用本身需要一個合法的內存空間，因此這行錯誤
	//加入const就可以了，編譯器優化代碼，int temp = 10; const int& ref = temp;
	const int& ref = 10;

	//ref = 100;  //加入const後不可以修改變量
	cout << ref << endl;

	//函數中利用常量引用防止誤操作修改實參
	int a = 10;
	showValue(a);

	system("pause");

	return 0;
}
```









## 3 函數提高

### 3.1 函數默認參數



在C++中，函數的形參列表中的形參是可以有默認值的。

語法：` 返回值類型  函數名 （參數= 默認值）{}`



**示例：**

```C++
int func(int a, int b = 10, int c = 10) {
	return a + b + c;
}

//1. 如果某個位置參數有默認值，那麼從這個位置往後，從左向右，必須都要有默認值
//2. 如果函數聲明有默認值，函數實現的時候就不能有默認參數
int func2(int a = 10, int b = 10);
int func2(int a, int b) {
	return a + b;
}

int main() {

	cout << "ret = " << func(20, 20) << endl;
	cout << "ret = " << func(100) << endl;

	system("pause");

	return 0;
}
```







### 3.2 函數佔位參數



C++中函數的形參列表裡可以有佔位參數，用來做佔位，調用函數時必須填補該位置



**語法：** `返回值類型 函數名 (數據類型){}`



在現階段函數的佔位參數存在意義不大，但是後面的課程中會用到該技術



**示例：**

```C++
//函數佔位參數 ，佔位參數也可以有默認參數
void func(int a, int) {
	cout << "this is func" << endl;
}

int main() {

	func(10,10); //佔位參數必須填補

	system("pause");

	return 0;
}
```









### 3.3 函數重載

#### 3.3.1 函數重載概述



**作用：**函數名可以相同，提高複用性



**函數重載滿足條件：**

* 同一個作用域下
* 函數名稱相同
* 函數參數**類型不同**  或者 **個數不同** 或者 **順序不同**



**注意:**  函數的返回值不可以作為函數重載的條件



**示例：**

```C++
//函數重載需要函數都在同一個作用域下
void func()
{
	cout << "func 的調用！" << endl;
}
void func(int a)
{
	cout << "func (int a) 的調用！" << endl;
}
void func(double a)
{
	cout << "func (double a)的調用！" << endl;
}
void func(int a ,double b)
{
	cout << "func (int a ,double b) 的調用！" << endl;
}
void func(double a ,int b)
{
	cout << "func (double a ,int b)的調用！" << endl;
}

//函數返回值不可以作為函數重載條件
//int func(double a, int b)
//{
//	cout << "func (double a ,int b)的調用！" << endl;
//}


int main() {

	func();
	func(10);
	func(3.14);
	func(10,3.14);
	func(3.14 , 10);
	
	system("pause");

	return 0;
}
```













#### 3.3.2 函數重載注意事項



* 引用作為重載條件
* 函數重載碰到函數默認參數





**示例：**

```C++
//函數重載注意事項
//1、引用作為重載條件

void func(int &a)
{
	cout << "func (int &a) 調用 " << endl;
}

void func(const int &a)
{
	cout << "func (const int &a) 調用 " << endl;
}


//2、函數重載碰到函數默認參數

void func2(int a, int b = 10)
{
	cout << "func2(int a, int b = 10) 調用" << endl;
}

void func2(int a)
{
	cout << "func2(int a) 調用" << endl;
}

int main() {
	
	int a = 10;
	func(a); //調用無const
	func(10);//調用有const


	//func2(10); //碰到默認參數產生歧義，需要避免

	system("pause");

	return 0;
}
```







## **4** 類和對象



C++面向對象的三大特性為：==封裝、繼承、多態==



C++認為==萬事萬物都皆為對象==，對象上有其屬性和行為



**例如：**

​	人可以作為對象，屬性有姓名、年齡、身高、體重...，行為有走、跑、跳、吃飯、唱歌...

​	車也可以作為對象，屬性有輪胎、方向盤、車燈...,行為有載人、放音樂、放空調...

​	具有相同性質的==對象==，我們可以抽象稱為==類==，人屬於人類，車屬於車類

### 4.1 封裝

#### 4.1.1  封裝的意義

封裝是C++面向對象三大特性之一

封裝的意義：

* 將屬性和行為作為一個整體，表現生活中的事物
* 將屬性和行為加以權限控制



**封裝意義一：**

​	在設計類的時候，屬性和行為寫在一起，表現事物

**語法：** `class 類名{   訪問權限： 屬性  / 行為  };`



**示例1：**設計一個圓類，求圓的周長

**示例代碼：**

```C++
//圓周率
const double PI = 3.14;

//1、封裝的意義
//將屬性和行為作為一個整體，用來表現生活中的事物

//封裝一個圓類，求圓的周長
//class代表設計一個類，後面跟著的是類名
class Circle
{
public:  //訪問權限  公共的權限

	//屬性
	int m_r;//半徑

	//行為
	//獲取到圓的周長
	double calculateZC()
	{
		//2 * pi  * r
		//獲取圓的周長
		return  2 * PI * m_r;
	}
};

int main() {

	//通過圓類，創建圓的對象
	// c1就是一個具體的圓
	Circle c1;
	c1.m_r = 10; //給圓對象的半徑 進行賦值操作

	//2 * pi * 10 = = 62.8
	cout << "圓的周長為： " << c1.calculateZC() << endl;

	system("pause");

	return 0;
}
```





**示例2：**設計一個學生類，屬性有姓名和學號，可以給姓名和學號賦值，可以顯示學生的姓名和學號





**示例2代碼：**

```C++
//學生類
class Student {
public:
	void setName(string name) {
		m_name = name;
	}
	void setID(int id) {
		m_id = id;
	}

	void showStudent() {
		cout << "name:" << m_name << " ID:" << m_id << endl;
	}
public:
	string m_name;
	int m_id;
};

int main() {

	Student stu;
	stu.setName("德瑪西亞");
	stu.setID(250);
	stu.showStudent();

	system("pause");

	return 0;
}

```









**封裝意義二：**

類在設計時，可以把屬性和行為放在不同的權限下，加以控制

訪問權限有三種：



1. public        公共權限  
2. protected 保護權限
3. private      私有權限







**示例：**

```C++
//三種權限
//公共權限  public     類內可以訪問  類外可以訪問
//保護權限  protected  類內可以訪問  類外不可以訪問
//私有權限  private    類內可以訪問  類外不可以訪問

class Person
{
	//姓名  公共權限
public:
	string m_Name;

	//汽車  保護權限
protected:
	string m_Car;

	//銀行卡密碼  私有權限
private:
	int m_Password;

public:
	void func()
	{
		m_Name = "張三";
		m_Car = "拖拉機";
		m_Password = 123456;
	}
};

int main() {

	Person p;
	p.m_Name = "李四";
	//p.m_Car = "奔馳";  //保護權限類外訪問不到
	//p.m_Password = 123; //私有權限類外訪問不到

	system("pause");

	return 0;
}
```







#### 4.1.2 struct和class區別



在C++中 struct和class唯一的**區別**就在於 **默認的訪問權限不同**

區別：

* struct 默認權限為公共
* class   默認權限為私有



```C++
class C1
{
	int  m_A; //默認是私有權限
};

struct C2
{
	int m_A;  //默認是公共權限
};

int main() {

	C1 c1;
	c1.m_A = 10; //錯誤，訪問權限是私有

	C2 c2;
	c2.m_A = 10; //正確，訪問權限是公共

	system("pause");

	return 0;
}
```













#### 4.1.3 成員屬性設置為私有



**優點1：**將所有成員屬性設置為私有，可以自己控制讀寫權限

**優點2：**對於寫權限，我們可以檢測數據的有效性



**示例：**

```C++
class Person {
public:

	//姓名設置可讀可寫
	void setName(string name) {
		m_Name = name;
	}
	string getName()
	{
		return m_Name;
	}


	//獲取年齡 
	int getAge() {
		return m_Age;
	}
	//設置年齡
	void setAge(int age) {
		if (age < 0 || age > 150) {
			cout << "你個老妖精!" << endl;
			return;
		}
		m_Age = age;
	}

	//情人設置為只寫
	void setLover(string lover) {
		m_Lover = lover;
	}

private:
	string m_Name; //可讀可寫  姓名
	
	int m_Age; //只讀  年齡

	string m_Lover; //只寫  情人
};


int main() {

	Person p;
	//姓名設置
	p.setName("張三");
	cout << "姓名： " << p.getName() << endl;

	//年齡設置
	p.setAge(50);
	cout << "年齡： " << p.getAge() << endl;

	//情人設置
	p.setLover("蒼井");
	//cout << "情人： " << p.m_Lover << endl;  //只寫屬性，不可以讀取

	system("pause");

	return 0;
}
```









**練習案例1：設計立方體類**

設計立方體類(Cube)

求出立方體的面積和體積

分別用全局函數和成員函數判斷兩個立方體是否相等。



![1545533548532](assets/1545533548532.png)











**練習案例2：點和圓的關係**

設計一個圓形類（Circle），和一個點類（Point），計算點和圓的關係。



![1545533829184](assets/1545533829184.png)







### 4.2 對象的初始化和清理



*  生活中我們買的電子產品都基本會有出廠設置，在某一天我們不用時候也會刪除一些自己信息數據保證安全
*  C++中的面向對象來源於生活，每個對象也都會有初始設置以及 對象銷燬前的清理數據的設置。





#### 4.2.1 構造函數和析構函數

對象的**初始化和清理**也是兩個非常重要的安全問題

​	一個對象或者變量沒有初始狀態，對其使用後果是未知

​	同樣的使用完一個對象或變量，沒有及時清理，也會造成一定的安全問題



c++利用了**構造函數**和**析構函數**解決上述問題，這兩個函數將會被編譯器自動調用，完成對象初始化和清理工作。

對象的初始化和清理工作是編譯器強制要我們做的事情，因此如果**我們不提供構造和析構，編譯器會提供**

**編譯器提供的構造函數和析構函數是空實現。**



* 構造函數：主要作用在於創建對象時為對象的成員屬性賦值，構造函數由編譯器自動調用，無須手動調用。
* 析構函數：主要作用在於對象**銷燬前**系統自動調用，執行一些清理工作。





**構造函數語法：**`類名(){}`

1. 構造函數，沒有返回值也不寫void
2. 函數名稱與類名相同
3. 構造函數可以有參數，因此可以發生重載
4. 程序在調用對象時候會自動調用構造，無須手動調用,而且只會調用一次





**析構函數語法：** `~類名(){}`

1. 析構函數，沒有返回值也不寫void
2. 函數名稱與類名相同,在名稱前加上符號  ~
3. 析構函數不可以有參數，因此不可以發生重載
4. 程序在對象銷燬前會自動調用析構，無須手動調用,而且只會調用一次





```C++
class Person
{
public:
	//構造函數
	Person()
	{
		cout << "Person的構造函數調用" << endl;
	}
	//析構函數
	~Person()
	{
		cout << "Person的析構函數調用" << endl;
	}

};

void test01()
{
	Person p;
}

int main() {
	
	test01();

	system("pause");

	return 0;
}
```











#### 4.2.2 構造函數的分類及調用

兩種分類方式：

​	按參數分為： 有參構造和無參構造

​	按類型分為： 普通構造和拷貝構造

三種調用方式：

​	括號法

​	顯示法

​	隱式轉換法



**示例：**

```C++
//1、構造函數分類
// 按照參數分類分為 有參和無參構造   無參又稱為默認構造函數
// 按照類型分類分為 普通構造和拷貝構造

class Person {
public:
	//無參（默認）構造函數
	Person() {
		cout << "無參構造函數!" << endl;
	}
	//有參構造函數
	Person(int a) {
		age = a;
		cout << "有參構造函數!" << endl;
	}
	//拷貝構造函數
	Person(const Person& p) {
		age = p.age;
		cout << "拷貝構造函數!" << endl;
	}
	//析構函數
	~Person() {
		cout << "析構函數!" << endl;
	}
public:
	int age;
};

//2、構造函數的調用
//調用無參構造函數
void test01() {
	Person p; //調用無參構造函數
}

//調用有參的構造函數
void test02() {

	//2.1  括號法，常用
	Person p1(10);
	//注意1：調用無參構造函數不能加括號，如果加了編譯器認為這是一個函數聲明
	//Person p2();

	//2.2 顯式法
	Person p2 = Person(10); 
	Person p3 = Person(p2);
	//Person(10)單獨寫就是匿名對象  當前行結束之後，馬上析構

	//2.3 隱式轉換法
	Person p4 = 10; // Person p4 = Person(10); 
	Person p5 = p4; // Person p5 = Person(p4); 

	//注意2：不能利用 拷貝構造函數 初始化匿名對象 編譯器認為是對象聲明
	//Person p5(p4);
}

int main() {

	test01();
	//test02();

	system("pause");

	return 0;
}
```









#### 4.2.3 拷貝構造函數調用時機



C++中拷貝構造函數調用時機通常有三種情況

* 使用一個已經創建完畢的對象來初始化一個新對象
* 值傳遞的方式給函數參數傳值
* 以值方式返回局部對象



**示例：**

```C++
class Person {
public:
	Person() {
		cout << "無參構造函數!" << endl;
		mAge = 0;
	}
	Person(int age) {
		cout << "有參構造函數!" << endl;
		mAge = age;
	}
	Person(const Person& p) {
		cout << "拷貝構造函數!" << endl;
		mAge = p.mAge;
	}
	//析構函數在釋放內存之前調用
	~Person() {
		cout << "析構函數!" << endl;
	}
public:
	int mAge;
};

//1. 使用一個已經創建完畢的對象來初始化一個新對象
void test01() {

	Person man(100); //p對象已經創建完畢
	Person newman(man); //調用拷貝構造函數
	Person newman2 = man; //拷貝構造

	//Person newman3;
	//newman3 = man; //不是調用拷貝構造函數，賦值操作
}

//2. 值傳遞的方式給函數參數傳值
//相當於Person p1 = p;
void doWork(Person p1) {}
void test02() {
	Person p; //無參構造函數
	doWork(p);
}

//3. 以值方式返回局部對象
Person doWork2()
{
	Person p1;
	cout << (int *)&p1 << endl;
	return p1;
}

void test03()
{
	Person p = doWork2();
	cout << (int *)&p << endl;
}


int main() {

	//test01();
	//test02();
	test03();

	system("pause");

	return 0;
}
```





#### 4.2.4 構造函數調用規則

默認情況下，c++編譯器至少給一個類添加3個函數

1．默認構造函數(無參，函數體為空)

2．默認析構函數(無參，函數體為空)

3．默認拷貝構造函數，對屬性進行值拷貝



構造函數調用規則如下：

* 如果用戶定義有參構造函數，c++不在提供默認無參構造，但是會提供默認拷貝構造


* 如果用戶定義拷貝構造函數，c++不會再提供其他構造函數



示例：

```C++
class Person {
public:
	//無參（默認）構造函數
	Person() {
		cout << "無參構造函數!" << endl;
	}
	//有參構造函數
	Person(int a) {
		age = a;
		cout << "有參構造函數!" << endl;
	}
	//拷貝構造函數
	Person(const Person& p) {
		age = p.age;
		cout << "拷貝構造函數!" << endl;
	}
	//析構函數
	~Person() {
		cout << "析構函數!" << endl;
	}
public:
	int age;
};

void test01()
{
	Person p1(18);
	//如果不寫拷貝構造，編譯器會自動添加拷貝構造，並且做淺拷貝操作
	Person p2(p1);

	cout << "p2的年齡為： " << p2.age << endl;
}

void test02()
{
	//如果用戶提供有參構造，編譯器不會提供默認構造，會提供拷貝構造
	Person p1; //此時如果用戶自己沒有提供默認構造，會出錯
	Person p2(10); //用戶提供的有參
	Person p3(p2); //此時如果用戶沒有提供拷貝構造，編譯器會提供

	//如果用戶提供拷貝構造，編譯器不會提供其他構造函數
	Person p4; //此時如果用戶自己沒有提供默認構造，會出錯
	Person p5(10); //此時如果用戶自己沒有提供有參，會出錯
	Person p6(p5); //用戶自己提供拷貝構造
}

int main() {

	test01();

	system("pause");

	return 0;
}
```









#### 4.2.5 深拷貝與淺拷貝



深淺拷貝是面試經典問題，也是常見的一個坑



淺拷貝：簡單的賦值拷貝操作



深拷貝：在堆區重新申請空間，進行拷貝操作



**示例：**

```C++
class Person {
public:
	//無參（默認）構造函數
	Person() {
		cout << "無參構造函數!" << endl;
	}
	//有參構造函數
	Person(int age ,int height) {
		
		cout << "有參構造函數!" << endl;

		m_age = age;
		m_height = new int(height);
		
	}
	//拷貝構造函數  
	Person(const Person& p) {
		cout << "拷貝構造函數!" << endl;
		//如果不利用深拷貝在堆區創建新內存，會導致淺拷貝帶來的重複釋放堆區問題
		m_age = p.m_age;
		m_height = new int(*p.m_height);
		
	}

	//析構函數
	~Person() {
		cout << "析構函數!" << endl;
		if (m_height != NULL)
		{
			delete m_height;
		}
	}
public:
	int m_age;
	int* m_height;
};

void test01()
{
	Person p1(18, 180);

	Person p2(p1);

	cout << "p1的年齡： " << p1.m_age << " 身高： " << *p1.m_height << endl;

	cout << "p2的年齡： " << p2.m_age << " 身高： " << *p2.m_height << endl;
}

int main() {

	test01();

	system("pause");

	return 0;
}
```

> 總結：如果屬性有在堆區開闢的，一定要自己提供拷貝構造函數，防止淺拷貝帶來的問題









#### 4.2.6 初始化列表



**作用：**

C++提供了初始化列表語法，用來初始化屬性



**語法：**`構造函數()：屬性1(值1),屬性2（值2）... {}`



**示例：**

```C++
class Person {
public:

	////傳統方式初始化
	//Person(int a, int b, int c) {
	//	m_A = a;
	//	m_B = b;
	//	m_C = c;
	//}

	//初始化列表方式初始化
	Person(int a, int b, int c) :m_A(a), m_B(b), m_C(c) {}
	void PrintPerson() {
		cout << "mA:" << m_A << endl;
		cout << "mB:" << m_B << endl;
		cout << "mC:" << m_C << endl;
	}
private:
	int m_A;
	int m_B;
	int m_C;
};

int main() {

	Person p(1, 2, 3);
	p.PrintPerson();


	system("pause");

	return 0;
}
```





#### 4.2.7 類對象作為類成員



C++類中的成員可以是另一個類的對象，我們稱該成員為 對象成員



例如：

```C++
class A {}
class B
{
    A a；
}
```



B類中有對象A作為成員，A為對象成員



那麼當創建B對象時，A與B的構造和析構的順序是誰先誰後？



**示例：**

```C++
class Phone
{
public:
	Phone(string name)
	{
		m_PhoneName = name;
		cout << "Phone構造" << endl;
	}

	~Phone()
	{
		cout << "Phone析構" << endl;
	}

	string m_PhoneName;

};


class Person
{
public:

	//初始化列表可以告訴編譯器調用哪一個構造函數
	Person(string name, string pName) :m_Name(name), m_Phone(pName)
	{
		cout << "Person構造" << endl;
	}

	~Person()
	{
		cout << "Person析構" << endl;
	}

	void playGame()
	{
		cout << m_Name << " 使用" << m_Phone.m_PhoneName << " 牌手機! " << endl;
	}

	string m_Name;
	Phone m_Phone;

};
void test01()
{
	//當類中成員是其他類對象時，我們稱該成員為 對象成員
	//構造的順序是 ：先調用對象成員的構造，再調用本類構造
	//析構順序與構造相反
	Person p("張三" , "蘋果X");
	p.playGame();

}


int main() {

	test01();

	system("pause");

	return 0;
}
```











#### 4.2.8 靜態成員

靜態成員就是在成員變量和成員函數前加上關鍵字static，稱為靜態成員

靜態成員分為：



*  靜態成員變量
   *  所有對象共享同一份數據
   *  在編譯階段分配內存
   *  類內聲明，類外初始化
*  靜態成員函數
   *  所有對象共享同一個函數
   *  靜態成員函數只能訪問靜態成員變量







**示例1 ：**靜態成員變量

```C++
class Person
{
	
public:

	static int m_A; //靜態成員變量

	//靜態成員變量特點：
	//1 在編譯階段分配內存
	//2 類內聲明，類外初始化
	//3 所有對象共享同一份數據

private:
	static int m_B; //靜態成員變量也是有訪問權限的
};
int Person::m_A = 10;
int Person::m_B = 10;

void test01()
{
	//靜態成員變量兩種訪問方式

	//1、通過對象
	Person p1;
	p1.m_A = 100;
	cout << "p1.m_A = " << p1.m_A << endl;

	Person p2;
	p2.m_A = 200;
	cout << "p1.m_A = " << p1.m_A << endl; //共享同一份數據
	cout << "p2.m_A = " << p2.m_A << endl;

	//2、通過類名
	cout << "m_A = " << Person::m_A << endl;


	//cout << "m_B = " << Person::m_B << endl; //私有權限訪問不到
}

int main() {

	test01();

	system("pause");

	return 0;
}
```



**示例2：**靜態成員函數

```C++
class Person
{

public:

	//靜態成員函數特點：
	//1 程序共享一個函數
	//2 靜態成員函數只能訪問靜態成員變量
	
	static void func()
	{
		cout << "func調用" << endl;
		m_A = 100;
		//m_B = 100; //錯誤，不可以訪問非靜態成員變量
	}

	static int m_A; //靜態成員變量
	int m_B; // 
private:

	//靜態成員函數也是有訪問權限的
	static void func2()
	{
		cout << "func2調用" << endl;
	}
};
int Person::m_A = 10;


void test01()
{
	//靜態成員變量兩種訪問方式

	//1、通過對象
	Person p1;
	p1.func();

	//2、通過類名
	Person::func();


	//Person::func2(); //私有權限訪問不到
}

int main() {

	test01();

	system("pause");

	return 0;
}
```









### 4.3 C++對象模型和this指針



#### 4.3.1 成員變量和成員函數分開存儲



在C++中，類內的成員變量和成員函數分開存儲

只有非靜態成員變量才屬於類的對象上



```C++
class Person {
public:
	Person() {
		mA = 0;
	}
	//非靜態成員變量佔對象空間
	int mA;
	//靜態成員變量不佔對象空間
	static int mB; 
	//函數也不佔對象空間，所有函數共享一個函數實例
	void func() {
		cout << "mA:" << this->mA << endl;
	}
	//靜態成員函數也不佔對象空間
	static void sfunc() {
	}
};

int main() {

	cout << sizeof(Person) << endl;

	system("pause");

	return 0;
}
```







#### 4.3.2 this指針概念

通過4.3.1我們知道在C++中成員變量和成員函數是分開存儲的

每一個非靜態成員函數只會誕生一份函數實例，也就是說多個同類型的對象會共用一塊代碼

那麼問題是：這一塊代碼是如何區分那個對象調用自己的呢？



c++通過提供特殊的對象指針，this指針，解決上述問題。**this指針指向被調用的成員函數所屬的對象**



this指針是隱含每一個非靜態成員函數內的一種指針

this指針不需要定義，直接使用即可



this指針的用途：

*  當形參和成員變量同名時，可用this指針來區分
*  在類的非靜態成員函數中返回對象本身，可使用return *this

```C++
class Person
{
public:

	Person(int age)
	{
		//1、當形參和成員變量同名時，可用this指針來區分
		this->age = age;
	}

	Person& PersonAddPerson(Person p)
	{
		this->age += p.age;
		//返回對象本身
		return *this;
	}

	int age;
};

void test01()
{
	Person p1(10);
	cout << "p1.age = " << p1.age << endl;

	Person p2(10);
	p2.PersonAddPerson(p1).PersonAddPerson(p1).PersonAddPerson(p1);
	cout << "p2.age = " << p2.age << endl;
}

int main() {

	test01();

	system("pause");

	return 0;
}
```









#### 4.3.3 空指針訪問成員函數



C++中空指針也是可以調用成員函數的，但是也要注意有沒有用到this指針



如果用到this指針，需要加以判斷保證代碼的健壯性



**示例：**

```C++
//空指針訪問成員函數
class Person {
public:

	void ShowClassName() {
		cout << "我是Person類!" << endl;
	}

	void ShowPerson() {
		if (this == NULL) {
			return;
		}
		cout << mAge << endl;
	}

public:
	int mAge;
};

void test01()
{
	Person * p = NULL;
	p->ShowClassName(); //空指針，可以調用成員函數
	p->ShowPerson();  //但是如果成員函數中用到了this指針，就不可以了
}

int main() {

	test01();

	system("pause");

	return 0;
}
```









#### 4.3.4 const修飾成員函數



**常函數：**

* 成員函數後加const後我們稱為這個函數為**常函數**
* 常函數內不可以修改成員屬性
* 成員屬性聲明時加關鍵字mutable後，在常函數中依然可以修改



**常對象：**

* 聲明對象前加const稱該對象為常對象
* 常對象只能調用常函數







**示例：**

```C++
class Person {
public:
	Person() {
		m_A = 0;
		m_B = 0;
	}

	//this指針的本質是一個指針常量，指針的指向不可修改
	//如果想讓指針指向的值也不可以修改，需要聲明常函數
	void ShowPerson() const {
		//const Type* const pointer;
		//this = NULL; //不能修改指針的指向 Person* const this;
		//this->mA = 100; //但是this指針指向的對象的數據是可以修改的

		//const修飾成員函數，表示指針指向的內存空間的數據不能修改，除了mutable修飾的變量
		this->m_B = 100;
	}

	void MyFunc() const {
		//mA = 10000;
	}

public:
	int m_A;
	mutable int m_B; //可修改 可變的
};


//const修飾對象  常對象
void test01() {

	const Person person; //常量對象  
	cout << person.m_A << endl;
	//person.mA = 100; //常對象不能修改成員變量的值,但是可以訪問
	person.m_B = 100; //但是常對象可以修改mutable修飾成員變量

	//常對象訪問成員函數
	person.MyFunc(); //常對象不能調用const的函數

}

int main() {

	test01();

	system("pause");

	return 0;
}
```








### 4.4 友元



生活中你的家有客廳(Public)，有你的臥室(Private)

客廳所有來的客人都可以進去，但是你的臥室是私有的，也就是說只有你能進去

但是呢，你也可以允許你的好閨蜜好基友進去。



在程序裡，有些私有屬性 也想讓類外特殊的一些函數或者類進行訪問，就需要用到友元的技術



友元的目的就是讓一個函數或者類 訪問另一個類中私有成員



友元的關鍵字為  ==friend==



友元的三種實現

* 全局函數做友元
* 類做友元
* 成員函數做友元





#### 4.4.1 全局函數做友元

```C++
class Building
{
	//告訴編譯器 goodGay全局函數 是 Building類的好朋友，可以訪問類中的私有內容
	friend void goodGay(Building * building);

public:

	Building()
	{
		this->m_SittingRoom = "客廳";
		this->m_BedRoom = "臥室";
	}


public:
	string m_SittingRoom; //客廳

private:
	string m_BedRoom; //臥室
};


void goodGay(Building * building)
{
	cout << "好基友正在訪問： " << building->m_SittingRoom << endl;
	cout << "好基友正在訪問： " << building->m_BedRoom << endl;
}


void test01()
{
	Building b;
	goodGay(&b);
}

int main(){

	test01();

	system("pause");
	return 0;
}
```



#### 4.4.2 類做友元



```C++
class Building;
class goodGay
{
public:

	goodGay();
	void visit();

private:
	Building *building;
};


class Building
{
	//告訴編譯器 goodGay類是Building類的好朋友，可以訪問到Building類中私有內容
	friend class goodGay;

public:
	Building();

public:
	string m_SittingRoom; //客廳
private:
	string m_BedRoom;//臥室
};

Building::Building()
{
	this->m_SittingRoom = "客廳";
	this->m_BedRoom = "臥室";
}

goodGay::goodGay()
{
	building = new Building;
}

void goodGay::visit()
{
	cout << "好基友正在訪問" << building->m_SittingRoom << endl;
	cout << "好基友正在訪問" << building->m_BedRoom << endl;
}

void test01()
{
	goodGay gg;
	gg.visit();

}

int main(){

	test01();

	system("pause");
	return 0;
}
```





#### 4.4.3 成員函數做友元



```C++

class Building;
class goodGay
{
public:

	goodGay();
	void visit(); //只讓visit函數作為Building的好朋友，可以發訪問Building中私有內容
	void visit2(); 

private:
	Building *building;
};


class Building
{
	//告訴編譯器  goodGay類中的visit成員函數 是Building好朋友，可以訪問私有內容
	friend void goodGay::visit();

public:
	Building();

public:
	string m_SittingRoom; //客廳
private:
	string m_BedRoom;//臥室
};

Building::Building()
{
	this->m_SittingRoom = "客廳";
	this->m_BedRoom = "臥室";
}

goodGay::goodGay()
{
	building = new Building;
}

void goodGay::visit()
{
	cout << "好基友正在訪問" << building->m_SittingRoom << endl;
	cout << "好基友正在訪問" << building->m_BedRoom << endl;
}

void goodGay::visit2()
{
	cout << "好基友正在訪問" << building->m_SittingRoom << endl;
	//cout << "好基友正在訪問" << building->m_BedRoom << endl;
}

void test01()
{
	goodGay  gg;
	gg.visit();

}

int main(){
    
	test01();

	system("pause");
	return 0;
}
```









### 4.5 運算符重載



運算符重載概念：對已有的運算符重新進行定義，賦予其另一種功能，以適應不同的數據類型



#### 4.5.1 加號運算符重載



作用：實現兩個自定義數據類型相加的運算



```C++
class Person {
public:
	Person() {};
	Person(int a, int b)
	{
		this->m_A = a;
		this->m_B = b;
	}
	//成員函數實現 + 號運算符重載
	Person operator+(const Person& p) {
		Person temp;
		temp.m_A = this->m_A + p.m_A;
		temp.m_B = this->m_B + p.m_B;
		return temp;
	}


public:
	int m_A;
	int m_B;
};

//全局函數實現 + 號運算符重載
//Person operator+(const Person& p1, const Person& p2) {
//	Person temp(0, 0);
//	temp.m_A = p1.m_A + p2.m_A;
//	temp.m_B = p1.m_B + p2.m_B;
//	return temp;
//}

//運算符重載 可以發生函數重載 
Person operator+(const Person& p2, int val)  
{
	Person temp;
	temp.m_A = p2.m_A + val;
	temp.m_B = p2.m_B + val;
	return temp;
}

void test() {

	Person p1(10, 10);
	Person p2(20, 20);

	//成員函數方式
	Person p3 = p2 + p1;  //相當於 p2.operaor+(p1)
	cout << "mA:" << p3.m_A << " mB:" << p3.m_B << endl;


	Person p4 = p3 + 10; //相當於 operator+(p3,10)
	cout << "mA:" << p4.m_A << " mB:" << p4.m_B << endl;

}

int main() {

	test();

	system("pause");

	return 0;
}
```



> 總結1：對於內置的數據類型的表達式的的運算符是不可能改變的

> 總結2：不要濫用運算符重載







#### 4.5.2 左移運算符重載



作用：可以輸出自定義數據類型



```C++
class Person {
	friend ostream& operator<<(ostream& out, Person& p);

public:

	Person(int a, int b)
	{
		this->m_A = a;
		this->m_B = b;
	}

	//成員函數 實現不了  p << cout 不是我們想要的效果
	//void operator<<(Person& p){
	//}

private:
	int m_A;
	int m_B;
};

//全局函數實現左移重載
//ostream對象只能有一個
ostream& operator<<(ostream& out, Person& p) {
	out << "a:" << p.m_A << " b:" << p.m_B;
	return out;
}

void test() {

	Person p1(10, 20);

	cout << p1 << "hello world" << endl; //鏈式編程
}

int main() {

	test();

	system("pause");

	return 0;
}
```



> 總結：重載左移運算符配合友元可以實現輸出自定義數據類型













#### 4.5.3 遞增運算符重載



作用： 通過重載遞增運算符，實現自己的整型數據



```C++

class MyInteger {

	friend ostream& operator<<(ostream& out, MyInteger myint);

public:
	MyInteger() {
		m_Num = 0;
	}
	//前置++
	MyInteger& operator++() {
		//先++
		m_Num++;
		//再返回
		return *this;
	}

	//後置++
	MyInteger operator++(int) {
		//先返回
		MyInteger temp = *this; //記錄當前本身的值，然後讓本身的值加1，但是返回的是以前的值，達到先返回後++；
		m_Num++;
		return temp;
	}

private:
	int m_Num;
};


ostream& operator<<(ostream& out, MyInteger myint) {
	out << myint.m_Num;
	return out;
}


//前置++ 先++ 再返回
void test01() {
	MyInteger myInt;
	cout << ++myInt << endl;
	cout << myInt << endl;
}

//後置++ 先返回 再++
void test02() {

	MyInteger myInt;
	cout << myInt++ << endl;
	cout << myInt << endl;
}

int main() {

	test01();
	//test02();

	system("pause");

	return 0;
}
```



> 總結： 前置遞增返回引用，後置遞增返回值













#### 4.5.4 賦值運算符重載



c++編譯器至少給一個類添加4個函數

1. 默認構造函數(無參，函數體為空)
2. 默認析構函數(無參，函數體為空)
3. 默認拷貝構造函數，對屬性進行值拷貝
4. 賦值運算符 operator=, 對屬性進行值拷貝





如果類中有屬性指向堆區，做賦值操作時也會出現深淺拷貝問題





**示例：**

```C++
class Person
{
public:

	Person(int age)
	{
		//將年齡數據開闢到堆區
		m_Age = new int(age);
	}

	//重載賦值運算符 
	Person& operator=(Person &p)
	{
		if (m_Age != NULL)
		{
			delete m_Age;
			m_Age = NULL;
		}
		//編譯器提供的代碼是淺拷貝
		//m_Age = p.m_Age;

		//提供深拷貝 解決淺拷貝的問題
		m_Age = new int(*p.m_Age);

		//返回自身
		return *this;
	}


	~Person()
	{
		if (m_Age != NULL)
		{
			delete m_Age;
			m_Age = NULL;
		}
	}

	//年齡的指針
	int *m_Age;

};


void test01()
{
	Person p1(18);

	Person p2(20);

	Person p3(30);

	p3 = p2 = p1; //賦值操作

	cout << "p1的年齡為：" << *p1.m_Age << endl;

	cout << "p2的年齡為：" << *p2.m_Age << endl;

	cout << "p3的年齡為：" << *p3.m_Age << endl;
}

int main() {

	test01();

	//int a = 10;
	//int b = 20;
	//int c = 30;

	//c = b = a;
	//cout << "a = " << a << endl;
	//cout << "b = " << b << endl;
	//cout << "c = " << c << endl;

	system("pause");

	return 0;
}
```









#### 4.5.5 關係運算符重載



**作用：**重載關係運算符，可以讓兩個自定義類型對象進行對比操作



**示例：**

```C++
class Person
{
public:
	Person(string name, int age)
	{
		this->m_Name = name;
		this->m_Age = age;
	};

	bool operator==(Person & p)
	{
		if (this->m_Name == p.m_Name && this->m_Age == p.m_Age)
		{
			return true;
		}
		else
		{
			return false;
		}
	}

	bool operator!=(Person & p)
	{
		if (this->m_Name == p.m_Name && this->m_Age == p.m_Age)
		{
			return false;
		}
		else
		{
			return true;
		}
	}

	string m_Name;
	int m_Age;
};

void test01()
{
	//int a = 0;
	//int b = 0;

	Person a("孫悟空", 18);
	Person b("孫悟空", 18);

	if (a == b)
	{
		cout << "a和b相等" << endl;
	}
	else
	{
		cout << "a和b不相等" << endl;
	}

	if (a != b)
	{
		cout << "a和b不相等" << endl;
	}
	else
	{
		cout << "a和b相等" << endl;
	}
}


int main() {

	test01();

	system("pause");

	return 0;
}
```





#### 4.5.6 函數調用運算符重載



* 函數調用運算符 ()  也可以重載
* 由於重載後使用的方式非常像函數的調用，因此稱為仿函數
* 仿函數沒有固定寫法，非常靈活



**示例：**

```C++
class MyPrint
{
public:
	void operator()(string text)
	{
		cout << text << endl;
	}

};
void test01()
{
	//重載的（）操作符 也稱為仿函數
	MyPrint myFunc;
	myFunc("hello world");
}


class MyAdd
{
public:
	int operator()(int v1, int v2)
	{
		return v1 + v2;
	}
};

void test02()
{
	MyAdd add;
	int ret = add(10, 10);
	cout << "ret = " << ret << endl;

	//匿名對象調用  
	cout << "MyAdd()(100,100) = " << MyAdd()(100, 100) << endl;
}

int main() {

	test01();
	test02();

	system("pause");

	return 0;
}
```









### 4.6  繼承

**繼承是面向對象三大特性之一**

有些類與類之間存在特殊的關係，例如下圖中：

![1544861202252](assets/1544861202252.png)

我們發現，定義這些類時，下級別的成員除了擁有上一級的共性，還有自己的特性。

這個時候我們就可以考慮利用繼承的技術，減少重複代碼



#### 4.6.1 繼承的基本語法



例如我們看到很多網站中，都有公共的頭部，公共的底部，甚至公共的左側列表，只有中心內容不同

接下來我們分別利用普通寫法和繼承的寫法來實現網頁中的內容，看一下繼承存在的意義以及好處



**普通實現：**

```C++
//Java頁面
class Java 
{
public:
	void header()
	{
		cout << "首頁、公開課、登錄、註冊...（公共頭部）" << endl;
	}
	void footer()
	{
		cout << "幫助中心、交流合作、站內地圖...(公共底部)" << endl;
	}
	void left()
	{
		cout << "Java,Python,C++...(公共分類列表)" << endl;
	}
	void content()
	{
		cout << "JAVA學科視頻" << endl;
	}
};
//Python頁面
class Python
{
public:
	void header()
	{
		cout << "首頁、公開課、登錄、註冊...（公共頭部）" << endl;
	}
	void footer()
	{
		cout << "幫助中心、交流合作、站內地圖...(公共底部)" << endl;
	}
	void left()
	{
		cout << "Java,Python,C++...(公共分類列表)" << endl;
	}
	void content()
	{
		cout << "Python學科視頻" << endl;
	}
};
//C++頁面
class CPP 
{
public:
	void header()
	{
		cout << "首頁、公開課、登錄、註冊...（公共頭部）" << endl;
	}
	void footer()
	{
		cout << "幫助中心、交流合作、站內地圖...(公共底部)" << endl;
	}
	void left()
	{
		cout << "Java,Python,C++...(公共分類列表)" << endl;
	}
	void content()
	{
		cout << "C++學科視頻" << endl;
	}
};

void test01()
{
	//Java頁面
	cout << "Java下載視頻頁面如下： " << endl;
	Java ja;
	ja.header();
	ja.footer();
	ja.left();
	ja.content();
	cout << "--------------------" << endl;

	//Python頁面
	cout << "Python下載視頻頁面如下： " << endl;
	Python py;
	py.header();
	py.footer();
	py.left();
	py.content();
	cout << "--------------------" << endl;

	//C++頁面
	cout << "C++下載視頻頁面如下： " << endl;
	CPP cp;
	cp.header();
	cp.footer();
	cp.left();
	cp.content();

}

int main() {

	test01();

	system("pause");

	return 0;
}
```



**繼承實現：**

```C++
//公共頁面
class BasePage
{
public:
	void header()
	{
		cout << "首頁、公開課、登錄、註冊...（公共頭部）" << endl;
	}

	void footer()
	{
		cout << "幫助中心、交流合作、站內地圖...(公共底部)" << endl;
	}
	void left()
	{
		cout << "Java,Python,C++...(公共分類列表)" << endl;
	}

};

//Java頁面
class Java : public BasePage
{
public:
	void content()
	{
		cout << "JAVA學科視頻" << endl;
	}
};
//Python頁面
class Python : public BasePage
{
public:
	void content()
	{
		cout << "Python學科視頻" << endl;
	}
};
//C++頁面
class CPP : public BasePage
{
public:
	void content()
	{
		cout << "C++學科視頻" << endl;
	}
};

void test01()
{
	//Java頁面
	cout << "Java下載視頻頁面如下： " << endl;
	Java ja;
	ja.header();
	ja.footer();
	ja.left();
	ja.content();
	cout << "--------------------" << endl;

	//Python頁面
	cout << "Python下載視頻頁面如下： " << endl;
	Python py;
	py.header();
	py.footer();
	py.left();
	py.content();
	cout << "--------------------" << endl;

	//C++頁面
	cout << "C++下載視頻頁面如下： " << endl;
	CPP cp;
	cp.header();
	cp.footer();
	cp.left();
	cp.content();


}

int main() {

	test01();

	system("pause");

	return 0;
}
```



**總結：**

繼承的好處：==可以減少重複的代碼==

class A : public B; 

A 類稱為子類 或 派生類

B 類稱為父類 或 基類



**派生類中的成員，包含兩大部分**：

一類是從基類繼承過來的，一類是自己增加的成員。

從基類繼承過過來的表現其共性，而新增的成員體現了其個性。









#### 4.6.2 繼承方式



繼承的語法：`class 子類 : 繼承方式  父類`



**繼承方式一共有三種：**

* 公共繼承
* 保護繼承
* 私有繼承





![img](assets/clip_image002.png)





**示例：**

```C++
class Base1
{
public: 
	int m_A;
protected:
	int m_B;
private:
	int m_C;
};

//公共繼承
class Son1 :public Base1
{
public:
	void func()
	{
		m_A; //可訪問 public權限
		m_B; //可訪問 protected權限
		//m_C; //不可訪問
	}
};

void myClass()
{
	Son1 s1;
	s1.m_A; //其他類只能訪問到公共權限
}

//保護繼承
class Base2
{
public:
	int m_A;
protected:
	int m_B;
private:
	int m_C;
};
class Son2:protected Base2
{
public:
	void func()
	{
		m_A; //可訪問 protected權限
		m_B; //可訪問 protected權限
		//m_C; //不可訪問
	}
};
void myClass2()
{
	Son2 s;
	//s.m_A; //不可訪問
}

//私有繼承
class Base3
{
public:
	int m_A;
protected:
	int m_B;
private:
	int m_C;
};
class Son3:private Base3
{
public:
	void func()
	{
		m_A; //可訪問 private權限
		m_B; //可訪問 private權限
		//m_C; //不可訪問
	}
};
class GrandSon3 :public Son3
{
public:
	void func()
	{
		//Son3是私有繼承，所以繼承Son3的屬性在GrandSon3中都無法訪問到
		//m_A;
		//m_B;
		//m_C;
	}
};
```









#### 4.6.3 繼承中的對象模型



**問題：**從父類繼承過來的成員，哪些屬於子類對象中？



**示例：**

```C++
class Base
{
public:
	int m_A;
protected:
	int m_B;
private:
	int m_C; //私有成員只是被隱藏了，但是還是會繼承下去
};

//公共繼承
class Son :public Base
{
public:
	int m_D;
};

void test01()
{
	cout << "sizeof Son = " << sizeof(Son) << endl;
}

int main() {

	test01();

	system("pause");

	return 0;
}
```





利用工具查看：



![1545881904150](assets/1545881904150.png)



打開工具窗口後，定位到當前CPP文件的盤符

然後輸入： cl /d1 reportSingleClassLayout查看的類名   所屬文件名



效果如下圖：



![1545882158050](assets/1545882158050.png)



> 結論： 父類中私有成員也是被子類繼承下去了，只是由編譯器給隱藏後訪問不到



















#### 4.6.4 繼承中構造和析構順序



子類繼承父類後，當創建子類對象，也會調用父類的構造函數



問題：父類和子類的構造和析構順序是誰先誰後？



**示例：**

```C++
class Base 
{
public:
	Base()
	{
		cout << "Base構造函數!" << endl;
	}
	~Base()
	{
		cout << "Base析構函數!" << endl;
	}
};

class Son : public Base
{
public:
	Son()
	{
		cout << "Son構造函數!" << endl;
	}
	~Son()
	{
		cout << "Son析構函數!" << endl;
	}

};


void test01()
{
	//繼承中 先調用父類構造函數，再調用子類構造函數，析構順序與構造相反
	Son s;
}

int main() {

	test01();

	system("pause");

	return 0;
}
```



> 總結：繼承中 先調用父類構造函數，再調用子類構造函數，析構順序與構造相反











#### 4.6.5 繼承同名成員處理方式



問題：當子類與父類出現同名的成員，如何通過子類對象，訪問到子類或父類中同名的數據呢？



* 訪問子類同名成員   直接訪問即可
* 訪問父類同名成員   需要加作用域



**示例：**

```C++
class Base {
public:
	Base()
	{
		m_A = 100;
	}

	void func()
	{
		cout << "Base - func()調用" << endl;
	}

	void func(int a)
	{
		cout << "Base - func(int a)調用" << endl;
	}

public:
	int m_A;
};


class Son : public Base {
public:
	Son()
	{
		m_A = 200;
	}

	//當子類與父類擁有同名的成員函數，子類會隱藏父類中所有版本的同名成員函數
	//如果想訪問父類中被隱藏的同名成員函數，需要加父類的作用域
	void func()
	{
		cout << "Son - func()調用" << endl;
	}
public:
	int m_A;
};

void test01()
{
	Son s;

	cout << "Son下的m_A = " << s.m_A << endl;
	cout << "Base下的m_A = " << s.Base::m_A << endl;

	s.func();
	s.Base::func();
	s.Base::func(10);

}
int main() {

	test01();

	system("pause");
	return EXIT_SUCCESS;
}
```

總結：

1. 子類對象可以直接訪問到子類中同名成員
2. 子類對象加作用域可以訪問到父類同名成員
3. 當子類與父類擁有同名的成員函數，子類會隱藏父類中同名成員函數，加作用域可以訪問到父類中同名函數













#### 4.6.6 繼承同名靜態成員處理方式



問題：繼承中同名的靜態成員在子類對象上如何進行訪問？



靜態成員和非靜態成員出現同名，處理方式一致



- 訪問子類同名成員   直接訪問即可
- 訪問父類同名成員   需要加作用域



**示例：**

```C++
class Base {
public:
	static void func()
	{
		cout << "Base - static void func()" << endl;
	}
	static void func(int a)
	{
		cout << "Base - static void func(int a)" << endl;
	}

	static int m_A;
};

int Base::m_A = 100;

class Son : public Base {
public:
	static void func()
	{
		cout << "Son - static void func()" << endl;
	}
	static int m_A;
};

int Son::m_A = 200;

//同名成員屬性
void test01()
{
	//通過對象訪問
	cout << "通過對象訪問： " << endl;
	Son s;
	cout << "Son  下 m_A = " << s.m_A << endl;
	cout << "Base 下 m_A = " << s.Base::m_A << endl;

	//通過類名訪問
	cout << "通過類名訪問： " << endl;
	cout << "Son  下 m_A = " << Son::m_A << endl;
	cout << "Base 下 m_A = " << Son::Base::m_A << endl;
}

//同名成員函數
void test02()
{
	//通過對象訪問
	cout << "通過對象訪問： " << endl;
	Son s;
	s.func();
	s.Base::func();

	cout << "通過類名訪問： " << endl;
	Son::func();
	Son::Base::func();
	//出現同名，子類會隱藏掉父類中所有同名成員函數，需要加作作用域訪問
	Son::Base::func(100);
}
int main() {

	//test01();
	test02();

	system("pause");

	return 0;
}
```

> 總結：同名靜態成員處理方式和非靜態處理方式一樣，只不過有兩種訪問的方式（通過對象 和 通過類名）













#### 4.6.7 多繼承語法



C++允許**一個類繼承多個類**



語法：` class 子類 ：繼承方式 父類1 ， 繼承方式 父類2...`



多繼承可能會引發父類中有同名成員出現，需要加作用域區分



**C++實際開發中不建議用多繼承**







**示例：**

```C++
class Base1 {
public:
	Base1()
	{
		m_A = 100;
	}
public:
	int m_A;
};

class Base2 {
public:
	Base2()
	{
		m_A = 200;  //開始是m_B 不會出問題，但是改為mA就會出現不明確
	}
public:
	int m_A;
};

//語法：class 子類：繼承方式 父類1 ，繼承方式 父類2 
class Son : public Base2, public Base1 
{
public:
	Son()
	{
		m_C = 300;
		m_D = 400;
	}
public:
	int m_C;
	int m_D;
};


//多繼承容易產生成員同名的情況
//通過使用類名作用域可以區分調用哪一個基類的成員
void test01()
{
	Son s;
	cout << "sizeof Son = " << sizeof(s) << endl;
	cout << s.Base1::m_A << endl;
	cout << s.Base2::m_A << endl;
}

int main() {

	test01();

	system("pause");

	return 0;
}
```



> 總結： 多繼承中如果父類中出現了同名情況，子類使用時候要加作用域











#### 4.6.8 菱形繼承



**菱形繼承概念：**

​	兩個派生類繼承同一個基類

​	又有某個類同時繼承者兩個派生類

​	這種繼承被稱為菱形繼承，或者鑽石繼承



**典型的菱形繼承案例：**



![IMG_256](assets/clip_image002.jpg)



**菱形繼承問題：**



1.     羊繼承了動物的數據，駝同樣繼承了動物的數據，當草泥馬使用數據時，就會產生二義性。

2. 草泥馬繼承自動物的數據繼承了兩份，其實我們應該清楚，這份數據我們只需要一份就可以。



**示例：**

```C++
class Animal
{
public:
	int m_Age;
};

//繼承前加virtual關鍵字後，變為虛繼承
//此時公共的父類Animal稱為虛基類
class Sheep : virtual public Animal {};
class Tuo   : virtual public Animal {};
class SheepTuo : public Sheep, public Tuo {};

void test01()
{
	SheepTuo st;
	st.Sheep::m_Age = 100;
	st.Tuo::m_Age = 200;

	cout << "st.Sheep::m_Age = " << st.Sheep::m_Age << endl;
	cout << "st.Tuo::m_Age = " <<  st.Tuo::m_Age << endl;
	cout << "st.m_Age = " << st.m_Age << endl;
}


int main() {

	test01();

	system("pause");

	return 0;
}
```



總結：

* 菱形繼承帶來的主要問題是子類繼承兩份相同的數據，導致資源浪費以及毫無意義
* 利用虛繼承可以解決菱形繼承問題



















### 4.7  多態

#### 4.7.1 多態的基本概念



**多態是C++面向對象三大特性之一**

多態分為兩類

* 靜態多態: 函數重載 和 運算符重載屬於靜態多態，複用函數名
* 動態多態: 派生類和虛函數實現運行時多態



靜態多態和動態多態區別：

* 靜態多態的函數地址早綁定  -  編譯階段確定函數地址
* 動態多態的函數地址晚綁定  -  運行階段確定函數地址



下面通過案例進行講解多態



```C++
class Animal
{
public:
	//Speak函數就是虛函數
	//函數前面加上virtual關鍵字，變成虛函數，那麼編譯器在編譯的時候就不能確定函數調用了。
	virtual void speak()
	{
		cout << "動物在說話" << endl;
	}
};

class Cat :public Animal
{
public:
	void speak()
	{
		cout << "小貓在說話" << endl;
	}
};

class Dog :public Animal
{
public:

	void speak()
	{
		cout << "小狗在說話" << endl;
	}

};
//我們希望傳入什麼對象，那麼就調用什麼對象的函數
//如果函數地址在編譯階段就能確定，那麼靜態聯編
//如果函數地址在運行階段才能確定，就是動態聯編

void DoSpeak(Animal & animal)
{
	animal.speak();
}
//
//多態滿足條件： 
//1、有繼承關係
//2、子類重寫父類中的虛函數
//多態使用：
//父類指針或引用指向子類對象

void test01()
{
	Cat cat;
	DoSpeak(cat);


	Dog dog;
	DoSpeak(dog);
}


int main() {

	test01();

	system("pause");

	return 0;
}
```

總結：

多態滿足條件

* 有繼承關係
* 子類重寫父類中的虛函數

多態使用條件

* 父類指針或引用指向子類對象

重寫：函數返回值類型  函數名 參數列表 完全一致稱為重寫









#### 4.7.2 多態案例一-計算器類



案例描述：

分別利用普通寫法和多態技術，設計實現兩個操作數進行運算的計算器類



多態的優點：

* 代碼組織結構清晰
* 可讀性強
* 利於前期和後期的擴展以及維護



**示例：**

```C++
//普通實現
class Calculator {
public:
	int getResult(string oper)
	{
		if (oper == "+") {
			return m_Num1 + m_Num2;
		}
		else if (oper == "-") {
			return m_Num1 - m_Num2;
		}
		else if (oper == "*") {
			return m_Num1 * m_Num2;
		}
		//如果要提供新的運算，需要修改源碼
	}
public:
	int m_Num1;
	int m_Num2;
};

void test01()
{
	//普通實現測試
	Calculator c;
	c.m_Num1 = 10;
	c.m_Num2 = 10;
	cout << c.m_Num1 << " + " << c.m_Num2 << " = " << c.getResult("+") << endl;

	cout << c.m_Num1 << " - " << c.m_Num2 << " = " << c.getResult("-") << endl;

	cout << c.m_Num1 << " * " << c.m_Num2 << " = " << c.getResult("*") << endl;
}



//多態實現
//抽象計算器類
//多態優點：代碼組織結構清晰，可讀性強，利於前期和後期的擴展以及維護
class AbstractCalculator
{
public :

	virtual int getResult()
	{
		return 0;
	}

	int m_Num1;
	int m_Num2;
};

//加法計算器
class AddCalculator :public AbstractCalculator
{
public:
	int getResult()
	{
		return m_Num1 + m_Num2;
	}
};

//減法計算器
class SubCalculator :public AbstractCalculator
{
public:
	int getResult()
	{
		return m_Num1 - m_Num2;
	}
};

//乘法計算器
class MulCalculator :public AbstractCalculator
{
public:
	int getResult()
	{
		return m_Num1 * m_Num2;
	}
};


void test02()
{
	//創建加法計算器
	AbstractCalculator *abc = new AddCalculator;
	abc->m_Num1 = 10;
	abc->m_Num2 = 10;
	cout << abc->m_Num1 << " + " << abc->m_Num2 << " = " << abc->getResult() << endl;
	delete abc;  //用完了記得銷燬

	//創建減法計算器
	abc = new SubCalculator;
	abc->m_Num1 = 10;
	abc->m_Num2 = 10;
	cout << abc->m_Num1 << " - " << abc->m_Num2 << " = " << abc->getResult() << endl;
	delete abc;  

	//創建乘法計算器
	abc = new MulCalculator;
	abc->m_Num1 = 10;
	abc->m_Num2 = 10;
	cout << abc->m_Num1 << " * " << abc->m_Num2 << " = " << abc->getResult() << endl;
	delete abc;
}

int main() {

	//test01();

	test02();

	system("pause");

	return 0;
}
```

> 總結：C++開發提倡利用多態設計程序架構，因為多態優點很多

















#### 4.7.3 純虛函數和抽象類



在多態中，通常父類中虛函數的實現是毫無意義的，主要都是調用子類重寫的內容



因此可以將虛函數改為**純虛函數**



純虛函數語法：`virtual 返回值類型 函數名 （參數列表）= 0 ;`



當類中有了純虛函數，這個類也稱為==抽象類==



**抽象類特點**：

 * 無法實例化對象
 * 子類必須重寫抽象類中的純虛函數，否則也屬於抽象類





**示例：**

```C++
class Base
{
public:
	//純虛函數
	//類中只要有一個純虛函數就稱為抽象類
	//抽象類無法實例化對象
	//子類必須重寫父類中的純虛函數，否則也屬於抽象類
	virtual void func() = 0;
};

class Son :public Base
{
public:
	virtual void func() 
	{
		cout << "func調用" << endl;
	};
};

void test01()
{
	Base * base = NULL;
	//base = new Base; // 錯誤，抽象類無法實例化對象
	base = new Son;
	base->func();
	delete base;//記得銷燬
}

int main() {

	test01();

	system("pause");

	return 0;
}
```















#### 4.7.4 多態案例二-製作飲品

**案例描述：**

製作飲品的大致流程為：煮水 -  沖泡 - 倒入杯中 - 加入輔料



利用多態技術實現本案例，提供抽象製作飲品基類，提供子類製作咖啡和茶葉



![1545985945198](assets/1545985945198.png)



**示例：**

```C++
//抽象製作飲品
class AbstractDrinking {
public:
	//燒水
	virtual void Boil() = 0;
	//沖泡
	virtual void Brew() = 0;
	//倒入杯中
	virtual void PourInCup() = 0;
	//加入輔料
	virtual void PutSomething() = 0;
	//規定流程
	void MakeDrink() {
		Boil();
		Brew();
		PourInCup();
		PutSomething();
	}
};

//製作咖啡
class Coffee : public AbstractDrinking {
public:
	//燒水
	virtual void Boil() {
		cout << "煮農夫山泉!" << endl;
	}
	//沖泡
	virtual void Brew() {
		cout << "沖泡咖啡!" << endl;
	}
	//倒入杯中
	virtual void PourInCup() {
		cout << "將咖啡倒入杯中!" << endl;
	}
	//加入輔料
	virtual void PutSomething() {
		cout << "加入牛奶!" << endl;
	}
};

//製作茶水
class Tea : public AbstractDrinking {
public:
	//燒水
	virtual void Boil() {
		cout << "煮自來水!" << endl;
	}
	//沖泡
	virtual void Brew() {
		cout << "沖泡茶葉!" << endl;
	}
	//倒入杯中
	virtual void PourInCup() {
		cout << "將茶水倒入杯中!" << endl;
	}
	//加入輔料
	virtual void PutSomething() {
		cout << "加入枸杞!" << endl;
	}
};

//業務函數
void DoWork(AbstractDrinking* drink) {
	drink->MakeDrink();
	delete drink;
}

void test01() {
	DoWork(new Coffee);
	cout << "--------------" << endl;
	DoWork(new Tea);
}


int main() {

	test01();

	system("pause");

	return 0;
}
```



















#### 4.7.5 虛析構和純虛析構



多態使用時，如果子類中有屬性開闢到堆區，那麼父類指針在釋放時無法調用到子類的析構代碼



解決方式：將父類中的析構函數改為**虛析構**或者**純虛析構**



虛析構和純虛析構共性：

* 可以解決父類指針釋放子類對象
* 都需要有具體的函數實現

虛析構和純虛析構區別：

* 如果是純虛析構，該類屬於抽象類，無法實例化對象



虛析構語法：

`virtual ~類名(){}`

純虛析構語法：

` virtual ~類名() = 0;`

`類名::~類名(){}`



**示例：**

```C++
class Animal {
public:

	Animal()
	{
		cout << "Animal 構造函數調用！" << endl;
	}
	virtual void Speak() = 0;

	//析構函數加上virtual關鍵字，變成虛析構函數
	//virtual ~Animal()
	//{
	//	cout << "Animal虛析構函數調用！" << endl;
	//}


	virtual ~Animal() = 0;
};

Animal::~Animal()
{
	cout << "Animal 純虛析構函數調用！" << endl;
}

//和包含普通純虛函數的類一樣，包含了純虛析構函數的類也是一個抽象類。不能夠被實例化。

class Cat : public Animal {
public:
	Cat(string name)
	{
		cout << "Cat構造函數調用！" << endl;
		m_Name = new string(name);
	}
	virtual void Speak()
	{
		cout << *m_Name <<  "小貓在說話!" << endl;
	}
	~Cat()
	{
		cout << "Cat析構函數調用!" << endl;
		if (this->m_Name != NULL) {
			delete m_Name;
			m_Name = NULL;
		}
	}

public:
	string *m_Name;
};

void test01()
{
	Animal *animal = new Cat("Tom");
	animal->Speak();

	//通過父類指針去釋放，會導致子類對象可能清理不乾淨，造成內存洩漏
	//怎麼解決？給基類增加一個虛析構函數
	//虛析構函數就是用來解決通過父類指針釋放子類對象
	delete animal;
}

int main() {

	test01();

	system("pause");

	return 0;
}
```



總結：

​	1. 虛析構或純虛析構就是用來解決通過父類指針釋放子類對象

​	2. 如果子類中沒有堆區數據，可以不寫為虛析構或純虛析構

​	3. 擁有純虛析構函數的類也屬於抽象類















#### 4.7.6 多態案例三-電腦組裝



**案例描述：**



電腦主要組成部件為 CPU（用於計算），顯卡（用於顯示），內存條（用於存儲）

將每個零件封裝出抽象基類，並且提供不同的廠商生產不同的零件，例如Intel廠商和Lenovo廠商

創建電腦類提供讓電腦工作的函數，並且調用每個零件工作的接口

測試時組裝三臺不同的電腦進行工作





**示例：**

```C++
#include<iostream>
using namespace std;

//抽象CPU類
class CPU
{
public:
	//抽象的計算函數
	virtual void calculate() = 0;
};

//抽象顯卡類
class VideoCard
{
public:
	//抽象的顯示函數
	virtual void display() = 0;
};

//抽象內存條類
class Memory
{
public:
	//抽象的存儲函數
	virtual void storage() = 0;
};

//電腦類
class Computer
{
public:
	Computer(CPU * cpu, VideoCard * vc, Memory * mem)
	{
		m_cpu = cpu;
		m_vc = vc;
		m_mem = mem;
	}

	//提供工作的函數
	void work()
	{
		//讓零件工作起來，調用接口
		m_cpu->calculate();

		m_vc->display();

		m_mem->storage();
	}

	//提供析構函數 釋放3個電腦零件
	~Computer()
	{

		//釋放CPU零件
		if (m_cpu != NULL)
		{
			delete m_cpu;
			m_cpu = NULL;
		}

		//釋放顯卡零件
		if (m_vc != NULL)
		{
			delete m_vc;
			m_vc = NULL;
		}

		//釋放內存條零件
		if (m_mem != NULL)
		{
			delete m_mem;
			m_mem = NULL;
		}
	}

private:

	CPU * m_cpu; //CPU的零件指針
	VideoCard * m_vc; //顯卡零件指針
	Memory * m_mem; //內存條零件指針
};

//具體廠商
//Intel廠商
class IntelCPU :public CPU
{
public:
	virtual void calculate()
	{
		cout << "Intel的CPU開始計算了！" << endl;
	}
};

class IntelVideoCard :public VideoCard
{
public:
	virtual void display()
	{
		cout << "Intel的顯卡開始顯示了！" << endl;
	}
};

class IntelMemory :public Memory
{
public:
	virtual void storage()
	{
		cout << "Intel的內存條開始存儲了！" << endl;
	}
};

//Lenovo廠商
class LenovoCPU :public CPU
{
public:
	virtual void calculate()
	{
		cout << "Lenovo的CPU開始計算了！" << endl;
	}
};

class LenovoVideoCard :public VideoCard
{
public:
	virtual void display()
	{
		cout << "Lenovo的顯卡開始顯示了！" << endl;
	}
};

class LenovoMemory :public Memory
{
public:
	virtual void storage()
	{
		cout << "Lenovo的內存條開始存儲了！" << endl;
	}
};


void test01()
{
	//第一臺電腦零件
	CPU * intelCpu = new IntelCPU;
	VideoCard * intelCard = new IntelVideoCard;
	Memory * intelMem = new IntelMemory;

	cout << "第一臺電腦開始工作：" << endl;
	//創建第一臺電腦
	Computer * computer1 = new Computer(intelCpu, intelCard, intelMem);
	computer1->work();
	delete computer1;

	cout << "-----------------------" << endl;
	cout << "第二臺電腦開始工作：" << endl;
	//第二臺電腦組裝
	Computer * computer2 = new Computer(new LenovoCPU, new LenovoVideoCard, new LenovoMemory);;
	computer2->work();
	delete computer2;

	cout << "-----------------------" << endl;
	cout << "第三臺電腦開始工作：" << endl;
	//第三臺電腦組裝
	Computer * computer3 = new Computer(new LenovoCPU, new IntelVideoCard, new LenovoMemory);;
	computer3->work();
	delete computer3;

}
```













## 5 文件操作



程序運行時產生的數據都屬於臨時數據，程序一旦運行結束都會被釋放

通過**文件可以將數據持久化**

C++中對文件操作需要包含頭文件 ==&lt; fstream &gt;==



文件類型分為兩種：

1. **文本文件**     -  文件以文本的**ASCII碼**形式存儲在計算機中
2. **二進制文件** -  文件以文本的**二進制**形式存儲在計算機中，用戶一般不能直接讀懂它們



操作文件的三大類:

1. ofstream：寫操作
2. ifstream： 讀操作
3. fstream ： 讀寫操作



### 5.1文本文件

#### 5.1.1寫文件

   寫文件步驟如下：

1. 包含頭文件   

     \#include <fstream\>

2. 創建流對象  

   ofstream ofs;

3. 打開文件

   ofs.open("文件路徑",打開方式);

4. 寫數據

   ofs << "寫入的數據";

5. 關閉文件

   ofs.close();

   ​

文件打開方式：

| 打開方式    | 解釋                       |
| ----------- | -------------------------- |
| ios::in     | 為讀文件而打開文件         |
| ios::out    | 為寫文件而打開文件         |
| ios::ate    | 初始位置：文件尾           |
| ios::app    | 追加方式寫文件             |
| ios::trunc  | 如果文件存在先刪除，再創建 |
| ios::binary | 二進制方式                 |

**注意：** 文件打開方式可以配合使用，利用|操作符

**例如：**用二進制方式寫文件 `ios::binary |  ios:: out`





**示例：**

```C++
#include <fstream>

void test01()
{
	ofstream ofs;
	ofs.open("test.txt", ios::out);

	ofs << "姓名：張三" << endl;
	ofs << "性別：男" << endl;
	ofs << "年齡：18" << endl;

	ofs.close();
}

int main() {

	test01();

	system("pause");

	return 0;
}
```

總結：

* 文件操作必須包含頭文件 fstream
* 讀文件可以利用 ofstream  ，或者fstream類
* 打開文件時候需要指定操作文件的路徑，以及打開方式
* 利用<<可以向文件中寫數據
* 操作完畢，要關閉文件

















#### 5.1.2讀文件



讀文件與寫文件步驟相似，但是讀取方式相對於比較多



讀文件步驟如下：

1. 包含頭文件   

     \#include <fstream\>

2. 創建流對象  

   ifstream ifs;

3. 打開文件並判斷文件是否打開成功

   ifs.open("文件路徑",打開方式);

4. 讀數據

   四種方式讀取

5. 關閉文件

   ifs.close();



**示例：**

```C++
#include <fstream>
#include <string>
void test01()
{
	ifstream ifs;
	ifs.open("test.txt", ios::in);

	if (!ifs.is_open())
	{
		cout << "文件打開失敗" << endl;
		return;
	}

	//第一種方式
	//char buf[1024] = { 0 };
	//while (ifs >> buf)
	//{
	//	cout << buf << endl;
	//}

	//第二種
	//char buf[1024] = { 0 };
	//while (ifs.getline(buf,sizeof(buf)))
	//{
	//	cout << buf << endl;
	//}

	//第三種
	//string buf;
	//while (getline(ifs, buf))
	//{
	//	cout << buf << endl;
	//}

	char c;
	while ((c = ifs.get()) != EOF)
	{
		cout << c;
	}

	ifs.close();


}

int main() {

	test01();

	system("pause");

	return 0;
}
```

總結：

- 讀文件可以利用 ifstream  ，或者fstream類
- 利用is_open函數可以判斷文件是否打開成功
- close 關閉文件 















### 5.2 二進制文件

以二進制的方式對文件進行讀寫操作

打開方式要指定為 ==ios::binary==



#### 5.2.1 寫文件

二進制方式寫文件主要利用流對象調用成員函數write

函數原型 ：`ostream& write(const char * buffer,int len);`

參數解釋：字符指針buffer指向內存中一段存儲空間。len是讀寫的字節數



**示例：**

```C++
#include <fstream>
#include <string>

class Person
{
public:
	char m_Name[64];
	int m_Age;
};

//二進制文件  寫文件
void test01()
{
	//1、包含頭文件

	//2、創建輸出流對象
	ofstream ofs("person.txt", ios::out | ios::binary);
	
	//3、打開文件
	//ofs.open("person.txt", ios::out | ios::binary);

	Person p = {"張三"  , 18};

	//4、寫文件
	ofs.write((const char *)&p, sizeof(p));

	//5、關閉文件
	ofs.close();
}

int main() {

	test01();

	system("pause");

	return 0;
}
```

總結：

* 文件輸出流對象 可以通過write函數，以二進制方式寫數據











#### 5.2.2 讀文件

二進制方式讀文件主要利用流對象調用成員函數read

函數原型：`istream& read(char *buffer,int len);`

參數解釋：字符指針buffer指向內存中一段存儲空間。len是讀寫的字節數

示例：

```C++
#include <fstream>
#include <string>

class Person
{
public:
	char m_Name[64];
	int m_Age;
};

void test01()
{
	ifstream ifs("person.txt", ios::in | ios::binary);
	if (!ifs.is_open())
	{
		cout << "文件打開失敗" << endl;
	}

	Person p;
	ifs.read((char *)&p, sizeof(p));

	cout << "姓名： " << p.m_Name << " 年齡： " << p.m_Age << endl;
}

int main() {

	test01();

	system("pause");

	return 0;
}
```



- 文件輸入流對象 可以通過read函數，以二進制方式讀數據

