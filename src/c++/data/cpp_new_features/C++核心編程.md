# C++核心編程

本階段主要針對C++==面向物件==編程技術做詳細講解，探討C++中的核心和精髓。



## 1 記憶體分區模型

C++程式在執行時，將記憶體大方向劃分為**4個區域**

- 程式碼區：存放函式體的二進制程式碼，由作業系統進行管理的
- 全局區：存放全局變數和靜態變數以及常數
- 棧區：由編譯器自動分配釋放, 存放函式的參數值,局部變數等
- 堆區：由程式員分配和釋放,若程式員不釋放,程式結束時由作業系統回收







**記憶體四區意義：**

不同區域存放的數據，賦予不同的生命週期, 給我們更大的靈活編程





### 1.1 程式運行前

​	在程式編譯後，生成了exe可執行程式，**未執行該程式前**分為兩個區域

​	**程式碼區：**

​		存放 CPU 執行的機器指令

​		程式碼區是**共享**的，共享的目的是對於頻繁被執行的程式，只需要在記憶體中有一份程式碼即可

​		程式碼區是**只讀**的，使其只讀的原因是防止程式意外地修改了它的指令

​	**全局區：**

​		全局變數和靜態變數存放在此.

​		全局區還包含了常數區, 字串常數和其他常數也存放在此.

​		==該區域的數據在程式結束後由作業系統釋放==.













**示例：**

```c++
//全局變數
int g_a = 10;
int g_b = 10;

//全局常數
const int c_g_a = 10;
const int c_g_b = 10;

int main() {

	//局部變數
	int a = 10;
	int b = 10;

	//印出地址
	cout << "局部變數a地址為： " << (int)&a << endl;
	cout << "局部變數b地址為： " << (int)&b << endl;

	cout << "全局變數g_a地址為： " <<  (int)&g_a << endl;
	cout << "全局變數g_b地址為： " <<  (int)&g_b << endl;

	//靜態變數
	static int s_a = 10;
	static int s_b = 10;

	cout << "靜態變數s_a地址為： " << (int)&s_a << endl;
	cout << "靜態變數s_b地址為： " << (int)&s_b << endl;

	cout << "字串常數地址為： " << (int)&"hello world" << endl;
	cout << "字串常數地址為： " << (int)&"hello world1" << endl;

	cout << "全局常數c_g_a地址為： " << (int)&c_g_a << endl;
	cout << "全局常數c_g_b地址為： " << (int)&c_g_b << endl;

	const int c_l_a = 10;
	const int c_l_b = 10;
	cout << "局部常數c_l_a地址為： " << (int)&c_l_a << endl;
	cout << "局部常數c_l_b地址為： " << (int)&c_l_b << endl;

	system("pause");

	return 0;
}
```

印出結果：

![1545017602518](assets/1545017602518.png)



總結：

* C++中在程式運行前分為全局區和程式碼區
* 程式碼區特點是共享和只讀
* 全局區中存放全局變數、靜態變數、常數
* 常數區中存放 const修飾的全局常數  和 字串常數






### 1.2 程式運行後



​	**棧區：**

​		由編譯器自動分配釋放, 存放函式的參數值,局部變數等

​		注意事項：不要返回局部變數的地址，棧區開闢的數據由編譯器自動釋放



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

​		由程式員分配釋放,若程式員不釋放,程式結束時由作業系統回收

​		在C++中主要利用new在堆區開闢記憶體

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

堆區數據由程式員管理開闢和釋放

堆區數據利用new關鍵字進行開闢記憶體









### 1.3 new操作符



​	C++中利用==new==操作符在堆區開闢數據

​	堆區開闢的數據，由程式員手動開闢，手動釋放，釋放利用操作符 ==delete==

​	語法：` new 數據型別`

​	利用new創建的數據，會返回該數據對應的型別的指標



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



**示例2：開闢陣列**

```c++
//堆區開闢陣列
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
	//釋放陣列 delete 後加 []
	delete[] arr;

	system("pause");

	return 0;
}

```











## 2 參照

### 2.1 參照的基本使用

**作用： **給變數起別名

**語法：** `數據型別 &別名 = 原名`



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







### 2.2 參照注意事項

* 參照必須初始化
* 參照在初始化後，不可以改變

示例：

```C++
int main() {

	int a = 10;
	int b = 20;
	//int &c; //錯誤，參照必須初始化
	int &c = a; //一旦初始化後，就不可以更改
	c = b; //這是賦值操作，不是更改參照

	cout << "a = " << a << endl;
	cout << "b = " << b << endl;
	cout << "c = " << c << endl;

	system("pause");

	return 0;
}
```











### 2.3 參照做函式參數

**作用：**函式傳參時，可以利用參照的技術讓形式參數修飾實際參數

**優點：**可以簡化指標修改實際參數



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

//3. 參照傳遞
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



> 總結：通過參照參數產生的效果同按地址傳遞是一樣的。參照的語法更清楚簡單













### 2.4 參照做函式回傳值



作用：參照是可以作為函式的回傳值存在的



注意：**不要返回局部變數參照**

用法：函式調用作為左值



**示例：**

```C++
//返回局部變數參照
int& test01() {
	int a = 10; //局部變數
	return a;
}

//返回靜態變數參照
int& test02() {
	static int a = 20;
	return a;
}

int main() {

	//不能返回局部變數的參照
	int& ref = test01();
	cout << "ref = " << ref << endl;
	cout << "ref = " << ref << endl;

	//如果函式做左值，那麼必須返回參照
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









### 2.5 參照的本質

本質：**參照的本質在c++內部實現是一個指標常數.**

講解示例：

```C++
//發現是參照，轉換為 int* const ref = &a;
void func(int& ref){
	ref = 100; // ref是參照，轉換為*ref = 100
}
int main(){
	int a = 10;
    
    //自動轉換為 int* const ref = &a; 指標常數是指標指向不可改，也說明為什麼參照不可更改
	int& ref = a; 
	ref = 20; //內部發現ref是參照，自動幫我們轉換為: *ref = 20;
    
	cout << "a:" << a << endl;
	cout << "ref:" << ref << endl;
    
	func(a);
	return 0;
}
```

結論：C++推薦用參照技術，因為語法方便，參照本質是指標常數，但是所有的指標操作編譯器都幫我們做了













### 2.6 常數參照



**作用：**常數參照主要用來修飾形式參數，防止誤操作



在函式形式參數列表中，可以加==const修飾形式參數==，防止形式參數改變實際參數



**示例：**



```C++
//參照使用的場景，通常用來修飾形式參數
void showValue(const int& v) {
	//v += 10;
	cout << v << endl;
}

int main() {

	//int& ref = 10;  參照本身需要一個合法的記憶體空間，因此這行錯誤
	//加入const就可以了，編譯器最佳化程式碼，int temp = 10; const int& ref = temp;
	const int& ref = 10;

	//ref = 100;  //加入const後不可以修改變數
	cout << ref << endl;

	//函式中利用常數參照防止誤操作修改實際參數
	int a = 10;
	showValue(a);

	system("pause");

	return 0;
}
```









## 3 函式提高

### 3.1 函式預設參數



在C++中，函式的形式參數列表中的形式參數是可以有預設值的。

語法：` 回傳值型別  函式名 （參數= 預設值）{}`



**示例：**

```C++
int func(int a, int b = 10, int c = 10) {
	return a + b + c;
}

//1. 如果某個位元元置參數有預設值，那麼從這個位元元置往後，從左向右，必須都要有預設值
//2. 如果函式聲明有預設值，函式實現的時候就不能有預設參數
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







### 3.2 函式佔位元元參數



C++中函式的形式參數列表裡可以有佔位元元參數，用來做佔位元元，調用函式時必須填補該位元元置



**語法：** `回傳值型別 函式名 (數據型別){}`



在現階段函式的佔位元元參數存在意義不大，但是後面的課程中會用到該技術



**示例：**

```C++
//函式佔位元元參數 ，佔位元元參數也可以有預設參數
void func(int a, int) {
	cout << "this is func" << endl;
}

int main() {

	func(10,10); //佔位元元參數必須填補

	system("pause");

	return 0;
}
```









### 3.3 函式多載

#### 3.3.1 函式多載概述



**作用：**函式名可以相同，提高複用性



**函式多載滿足條件：**

* 同一個作用域下
* 函式名稱相同
* 函式參數**型別不同**  或者 **個數不同** 或者 **順序不同**



**注意:**  函式的回傳值不可以作為函式多載的條件



**示例：**

```C++
//函式多載需要函式都在同一個作用域下
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

//函式回傳值不可以作為函式多載條件
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













#### 3.3.2 函式多載注意事項



* 參照作為多載條件
* 函式多載碰到函式預設參數





**示例：**

```C++
//函式多載注意事項
//1、參照作為多載條件

void func(int &a)
{
	cout << "func (int &a) 調用 " << endl;
}

void func(const int &a)
{
	cout << "func (const int &a) 調用 " << endl;
}


//2、函式多載碰到函式預設參數

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


	//func2(10); //碰到預設參數產生歧義，需要避免

	system("pause");

	return 0;
}
```







## **4** 類和物件



C++面向物件的三大特性為：==封裝、繼承、多型==



C++認為==萬事萬物都皆為物件==，物件上有其屬性和行為



**例如：**

​	人可以作為物件，屬性有姓名、年齡、身高、體重...，行為有走、跑、跳、吃飯、唱歌...

​	車也可以作為物件，屬性有輪胎、方向盤、車燈...,行為有載人、放音樂、放空調...

​	具有相同性質的==物件==，我們可以抽象稱為==類==，人屬於人類，車屬於車類

### 4.1 封裝

#### 4.1.1  封裝的意義

封裝是C++面向物件三大特性之一

封裝的意義：

* 將屬性和行為作為一個整體，表現生活中的事物
* 將屬性和行為加以權限控制



**封裝意義一：**

​	在設計類的時候，屬性和行為寫在一起，表現事物

**語法：** `class 類名{   訪問權限： 屬性  / 行為  };`



**示例1：**設計一個圓類，求圓的周長

**示例程式碼：**

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

	//通過圓類，創建圓的物件
	// c1就是一個具體的圓
	Circle c1;
	c1.m_r = 10; //給圓物件的半徑 進行賦值操作

	//2 * pi * 10 = = 62.8
	cout << "圓的周長為： " << c1.calculateZC() << endl;

	system("pause");

	return 0;
}
```





**示例2：**設計一個學生類，屬性有姓名和學號，可以給姓名和學號賦值，可以顯示學生的姓名和學號





**示例2程式碼：**

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



在C++中 struct和class唯一的**區別**就在於 **預設的訪問權限不同**

區別：

* struct 預設權限為公共
* class   預設權限為私有



```C++
class C1
{
	int  m_A; //預設是私有權限
};

struct C2
{
	int m_A;  //預設是公共權限
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

分別用全局函式和成員函式判斷兩個立方體是否相等。



![1545533548532](assets/1545533548532.png)











**練習案例2：點和圓的關係**

設計一個圓形類（Circle），和一個點類（Point），計算點和圓的關係。



![1545533829184](assets/1545533829184.png)







### 4.2 物件的初始化和清理



*  生活中我們買的電子產品都基本會有出廠設置，在某一天我們不用時候也會刪除一些自己資訊數據保證安全
*  C++中的面向物件來源於生活，每個物件也都會有初始設置以及 物件銷燬前的清理數據的設置。





#### 4.2.1 建構函式和解構函式

物件的**初始化和清理**也是兩個非常重要的安全問題

​	一個物件或者變數沒有初始狀態，對其使用後果是未知

​	同樣的使用完一個物件或變數，沒有及時清理，也會造成一定的安全問題



c++利用了**建構函式**和**解構函式**解決上述問題，這兩個函式將會被編譯器自動調用，完成物件初始化和清理工作。

物件的初始化和清理工作是編譯器強制要我們做的事情，因此如果**我們不提供建構和解構，編譯器會提供**

**編譯器提供的建構函式和解構函式是空實現。**



* 建構函式：主要作用在於創建物件時為物件的成員屬性賦值，建構函式由編譯器自動調用，無須手動調用。
* 解構函式：主要作用在於物件**銷燬前**系統自動調用，執行一些清理工作。





**建構函式語法：**`類名(){}`

1. 建構函式，沒有回傳值也不寫void
2. 函式名稱與類名相同
3. 建構函式可以有參數，因此可以發生多載
4. 程式在調用物件時候會自動調用建構，無須手動調用,而且只會調用一次





**解構函式語法：** `~類名(){}`

1. 解構函式，沒有回傳值也不寫void
2. 函式名稱與類名相同,在名稱前加上符號  ~
3. 解構函式不可以有參數，因此不可以發生多載
4. 程式在物件銷燬前會自動調用解構，無須手動調用,而且只會調用一次





```C++
class Person
{
public:
	//建構函式
	Person()
	{
		cout << "Person的建構函式調用" << endl;
	}
	//解構函式
	~Person()
	{
		cout << "Person的解構函式調用" << endl;
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











#### 4.2.2 建構函式的分類及調用

兩種分類方式：

​	按參數分為： 有參建構和無參建構

​	按型別分為： 普通建構和複製建構

三種調用方式：

​	括號法

​	顯示法

​	隱式轉換法



**示例：**

```C++
//1、建構函式分類
// 按照參數分類分為 有參和無參建構   無參又稱為預設建構函式
// 按照型別分類分為 普通建構和複製建構

class Person {
public:
	//無參（預設）建構函式
	Person() {
		cout << "無參建構函式!" << endl;
	}
	//有參建構函式
	Person(int a) {
		age = a;
		cout << "有參建構函式!" << endl;
	}
	//複製建構函式
	Person(const Person& p) {
		age = p.age;
		cout << "複製建構函式!" << endl;
	}
	//解構函式
	~Person() {
		cout << "解構函式!" << endl;
	}
public:
	int age;
};

//2、建構函式的調用
//調用無參建構函式
void test01() {
	Person p; //調用無參建構函式
}

//調用有參的建構函式
void test02() {

	//2.1  括號法，常用
	Person p1(10);
	//注意1：調用無參建構函式不能加括號，如果加了編譯器認為這是一個函式聲明
	//Person p2();

	//2.2 顯式法
	Person p2 = Person(10); 
	Person p3 = Person(p2);
	//Person(10)單獨寫就是匿名物件  當前行結束之後，馬上解構

	//2.3 隱式轉換法
	Person p4 = 10; // Person p4 = Person(10); 
	Person p5 = p4; // Person p5 = Person(p4); 

	//注意2：不能利用 複製建構函式 初始化匿名物件 編譯器認為是物件聲明
	//Person p5(p4);
}

int main() {

	test01();
	//test02();

	system("pause");

	return 0;
}
```









#### 4.2.3 複製建構函式調用時機



C++中複製建構函式調用時機通常有三種情況

* 使用一個已經創建完畢的物件來初始化一個新物件
* 值傳遞的方式給函式參數傳值
* 以值方式返回局部物件



**示例：**

```C++
class Person {
public:
	Person() {
		cout << "無參建構函式!" << endl;
		mAge = 0;
	}
	Person(int age) {
		cout << "有參建構函式!" << endl;
		mAge = age;
	}
	Person(const Person& p) {
		cout << "複製建構函式!" << endl;
		mAge = p.mAge;
	}
	//解構函式在釋放記憶體之前調用
	~Person() {
		cout << "解構函式!" << endl;
	}
public:
	int mAge;
};

//1. 使用一個已經創建完畢的物件來初始化一個新物件
void test01() {

	Person man(100); //p物件已經創建完畢
	Person newman(man); //調用複製建構函式
	Person newman2 = man; //複製建構

	//Person newman3;
	//newman3 = man; //不是調用複製建構函式，賦值操作
}

//2. 值傳遞的方式給函式參數傳值
//相當於Person p1 = p;
void doWork(Person p1) {}
void test02() {
	Person p; //無參建構函式
	doWork(p);
}

//3. 以值方式返回局部物件
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





#### 4.2.4 建構函式調用規則

預設情況下，c++編譯器至少給一個類添加3個函式

1．預設建構函式(無參，函式體為空)

2．預設解構函式(無參，函式體為空)

3．預設複製建構函式，對屬性進行值複製



建構函式調用規則如下：

* 如果用戶定義有參建構函式，c++不在提供預設無參建構，但是會提供預設複製建構


* 如果用戶定義複製建構函式，c++不會再提供其他建構函式



示例：

```C++
class Person {
public:
	//無參（預設）建構函式
	Person() {
		cout << "無參建構函式!" << endl;
	}
	//有參建構函式
	Person(int a) {
		age = a;
		cout << "有參建構函式!" << endl;
	}
	//複製建構函式
	Person(const Person& p) {
		age = p.age;
		cout << "複製建構函式!" << endl;
	}
	//解構函式
	~Person() {
		cout << "解構函式!" << endl;
	}
public:
	int age;
};

void test01()
{
	Person p1(18);
	//如果不寫複製建構，編譯器會自動添加複製建構，並且做淺複製操作
	Person p2(p1);

	cout << "p2的年齡為： " << p2.age << endl;
}

void test02()
{
	//如果用戶提供有參建構，編譯器不會提供預設建構，會提供複製建構
	Person p1; //此時如果用戶自己沒有提供預設建構，會出錯
	Person p2(10); //用戶提供的有參
	Person p3(p2); //此時如果用戶沒有提供複製建構，編譯器會提供

	//如果用戶提供複製建構，編譯器不會提供其他建構函式
	Person p4; //此時如果用戶自己沒有提供預設建構，會出錯
	Person p5(10); //此時如果用戶自己沒有提供有參，會出錯
	Person p6(p5); //用戶自己提供複製建構
}

int main() {

	test01();

	system("pause");

	return 0;
}
```









#### 4.2.5 深複製與淺複製



深淺複製是面試經典問題，也是常見的一個坑



淺複製：簡單的賦值複製操作



深複製：在堆區重新申請空間，進行複製操作



**示例：**

```C++
class Person {
public:
	//無參（預設）建構函式
	Person() {
		cout << "無參建構函式!" << endl;
	}
	//有參建構函式
	Person(int age ,int height) {
		
		cout << "有參建構函式!" << endl;

		m_age = age;
		m_height = new int(height);
		
	}
	//複製建構函式  
	Person(const Person& p) {
		cout << "複製建構函式!" << endl;
		//如果不利用深複製在堆區創建新記憶體，會導致淺複製帶來的重複釋放堆區問題
		m_age = p.m_age;
		m_height = new int(*p.m_height);
		
	}

	//解構函式
	~Person() {
		cout << "解構函式!" << endl;
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

> 總結：如果屬性有在堆區開闢的，一定要自己提供複製建構函式，防止淺複製帶來的問題









#### 4.2.6 初始化列表



**作用：**

C++提供了初始化列表語法，用來初始化屬性



**語法：**`建構函式()：屬性1(值1),屬性2（值2）... {}`



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





#### 4.2.7 類物件作為類成員



C++類中的成員可以是另一個類的物件，我們稱該成員為 物件成員



例如：

```C++
class A {}
class B
{
    A a；
}
```



B類中有物件A作為成員，A為物件成員



那麼當創建B物件時，A與B的建構和解構的順序是誰先誰後？



**示例：**

```C++
class Phone
{
public:
	Phone(string name)
	{
		m_PhoneName = name;
		cout << "Phone建構" << endl;
	}

	~Phone()
	{
		cout << "Phone解構" << endl;
	}

	string m_PhoneName;

};


class Person
{
public:

	//初始化列表可以告訴編譯器調用哪一個建構函式
	Person(string name, string pName) :m_Name(name), m_Phone(pName)
	{
		cout << "Person建構" << endl;
	}

	~Person()
	{
		cout << "Person解構" << endl;
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
	//當類中成員是其他類物件時，我們稱該成員為 物件成員
	//建構的順序是 ：先調用物件成員的建構，再調用本類建構
	//解構順序與建構相反
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

靜態成員就是在成員變數和成員函式前加上關鍵字static，稱為靜態成員

靜態成員分為：



*  靜態成員變數
   *  所有物件共享同一份數據
   *  在編譯階段分配記憶體
   *  類內聲明，類外初始化
*  靜態成員函式
   *  所有物件共享同一個函式
   *  靜態成員函式只能訪問靜態成員變數







**示例1 ：**靜態成員變數

```C++
class Person
{
	
public:

	static int m_A; //靜態成員變數

	//靜態成員變數特點：
	//1 在編譯階段分配記憶體
	//2 類內聲明，類外初始化
	//3 所有物件共享同一份數據

private:
	static int m_B; //靜態成員變數也是有訪問權限的
};
int Person::m_A = 10;
int Person::m_B = 10;

void test01()
{
	//靜態成員變數兩種訪問方式

	//1、通過物件
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



**示例2：**靜態成員函式

```C++
class Person
{

public:

	//靜態成員函式特點：
	//1 程式共享一個函式
	//2 靜態成員函式只能訪問靜態成員變數
	
	static void func()
	{
		cout << "func調用" << endl;
		m_A = 100;
		//m_B = 100; //錯誤，不可以訪問非靜態成員變數
	}

	static int m_A; //靜態成員變數
	int m_B; // 
private:

	//靜態成員函式也是有訪問權限的
	static void func2()
	{
		cout << "func2調用" << endl;
	}
};
int Person::m_A = 10;


void test01()
{
	//靜態成員變數兩種訪問方式

	//1、通過物件
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









### 4.3 C++物件模型和this指標



#### 4.3.1 成員變數和成員函式分開存儲



在C++中，類內的成員變數和成員函式分開存儲

只有非靜態成員變數才屬於類的物件上



```C++
class Person {
public:
	Person() {
		mA = 0;
	}
	//非靜態成員變數佔物件空間
	int mA;
	//靜態成員變數不佔物件空間
	static int mB; 
	//函式也不佔物件空間，所有函式共享一個函式實體
	void func() {
		cout << "mA:" << this->mA << endl;
	}
	//靜態成員函式也不佔物件空間
	static void sfunc() {
	}
};

int main() {

	cout << sizeof(Person) << endl;

	system("pause");

	return 0;
}
```







#### 4.3.2 this指標概念

通過4.3.1我們知道在C++中成員變數和成員函式是分開存儲的

每一個非靜態成員函式只會誕生一份函式實體，也就是說多個同型別的物件會共用一塊程式碼

那麼問題是：這一塊程式碼是如何區分那個物件調用自己的呢？



c++通過提供特殊的物件指標，this指標，解決上述問題。**this指標指向被調用的成員函式所屬的物件**



this指標是隱含每一個非靜態成員函式內的一種指標

this指標不需要定義，直接使用即可



this指標的用途：

*  當形式參數和成員變數同名時，可用this指標來區分
*  在類的非靜態成員函式中返回物件本身，可使用return *this

```C++
class Person
{
public:

	Person(int age)
	{
		//1、當形式參數和成員變數同名時，可用this指標來區分
		this->age = age;
	}

	Person& PersonAddPerson(Person p)
	{
		this->age += p.age;
		//返回物件本身
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









#### 4.3.3 空指標訪問成員函式



C++中空指標也是可以調用成員函式的，但是也要注意有沒有用到this指標



如果用到this指標，需要加以判斷保證程式碼的健壯性



**示例：**

```C++
//空指標訪問成員函式
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
	p->ShowClassName(); //空指標，可以調用成員函式
	p->ShowPerson();  //但是如果成員函式中用到了this指標，就不可以了
}

int main() {

	test01();

	system("pause");

	return 0;
}
```









#### 4.3.4 const修飾成員函式



**常函式：**

* 成員函式後加const後我們稱為這個函式為**常函式**
* 常函式內不可以修改成員屬性
* 成員屬性聲明時加關鍵字mutable後，在常函式中依然可以修改



**常物件：**

* 聲明物件前加const稱該物件為常物件
* 常物件只能調用常函式







**示例：**

```C++
class Person {
public:
	Person() {
		m_A = 0;
		m_B = 0;
	}

	//this指標的本質是一個指標常數，指標的指向不可修改
	//如果想讓指標指向的值也不可以修改，需要聲明常函式
	void ShowPerson() const {
		//const Type* const pointer;
		//this = NULL; //不能修改指標的指向 Person* const this;
		//this->mA = 100; //但是this指標指向的物件的數據是可以修改的

		//const修飾成員函式，表示指標指向的記憶體空間的數據不能修改，除了mutable修飾的變數
		this->m_B = 100;
	}

	void MyFunc() const {
		//mA = 10000;
	}

public:
	int m_A;
	mutable int m_B; //可修改 可變的
};


//const修飾物件  常物件
void test01() {

	const Person person; //常數物件  
	cout << person.m_A << endl;
	//person.mA = 100; //常物件不能修改成員變數的值,但是可以訪問
	person.m_B = 100; //但是常物件可以修改mutable修飾成員變數

	//常物件訪問成員函式
	person.MyFunc(); //常物件不能調用const的函式

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



在程式裡，有些私有屬性 也想讓類外特殊的一些函式或者類進行訪問，就需要用到友元的技術



友元的目的就是讓一個函式或者類 訪問另一個類中私有成員



友元的關鍵字為  ==friend==



友元的三種實現

* 全局函式做友元
* 類做友元
* 成員函式做友元





#### 4.4.1 全局函式做友元

```C++
class Building
{
	//告訴編譯器 goodGay全局函式 是 Building類的好朋友，可以訪問類中的私有內容
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





#### 4.4.3 成員函式做友元



```C++

class Building;
class goodGay
{
public:

	goodGay();
	void visit(); //只讓visit函式作為Building的好朋友，可以發訪問Building中私有內容
	void visit2(); 

private:
	Building *building;
};


class Building
{
	//告訴編譯器  goodGay類中的visit成員函式 是Building好朋友，可以訪問私有內容
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









### 4.5 運算子多載



運算子多載概念：對已有的運算子重新進行定義，賦予其另一種功能，以適應不同的數據型別



#### 4.5.1 加號運算子多載



作用：實現兩個自定義數據型別相加的運算



```C++
class Person {
public:
	Person() {};
	Person(int a, int b)
	{
		this->m_A = a;
		this->m_B = b;
	}
	//成員函式實現 + 號運算子多載
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

//全局函式實現 + 號運算子多載
//Person operator+(const Person& p1, const Person& p2) {
//	Person temp(0, 0);
//	temp.m_A = p1.m_A + p2.m_A;
//	temp.m_B = p1.m_B + p2.m_B;
//	return temp;
//}

//運算子多載 可以發生函式多載 
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

	//成員函式方式
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



> 總結1：對於內置的數據型別的表達式的的運算子是不可能改變的

> 總結2：不要濫用運算子多載







#### 4.5.2 左移運算子多載



作用：可以輸出自定義數據型別



```C++
class Person {
	friend ostream& operator<<(ostream& out, Person& p);

public:

	Person(int a, int b)
	{
		this->m_A = a;
		this->m_B = b;
	}

	//成員函式 實現不了  p << cout 不是我們想要的效果
	//void operator<<(Person& p){
	//}

private:
	int m_A;
	int m_B;
};

//全局函式實現左移多載
//ostream物件只能有一個
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



> 總結：多載左移運算子配合友元可以實現輸出自定義數據型別













#### 4.5.3 遞增運算子多載



作用： 通過多載遞增運算子，實現自己的整型數據



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



> 總結： 前置遞增返回參照，後置遞增回傳值













#### 4.5.4 賦值運算子多載



c++編譯器至少給一個類添加4個函式

1. 預設建構函式(無參，函式體為空)
2. 預設解構函式(無參，函式體為空)
3. 預設複製建構函式，對屬性進行值複製
4. 賦值運算子 operator=, 對屬性進行值複製





如果類中有屬性指向堆區，做賦值操作時也會出現深淺複製問題





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

	//多載賦值運算子 
	Person& operator=(Person &p)
	{
		if (m_Age != NULL)
		{
			delete m_Age;
			m_Age = NULL;
		}
		//編譯器提供的程式碼是淺複製
		//m_Age = p.m_Age;

		//提供深複製 解決淺複製的問題
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

	//年齡的指標
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









#### 4.5.5 關係運算子多載



**作用：**多載關係運算子，可以讓兩個自定義型別物件進行對比操作



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





#### 4.5.6 函式調用運算子多載



* 函式調用運算子 ()  也可以多載
* 由於多載後使用的方式非常像函式的調用，因此稱為仿函式
* 仿函式沒有固定寫法，非常靈活



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
	//多載的（）操作符 也稱為仿函式
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

	//匿名物件調用  
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

**繼承是面向物件三大特性之一**

有些類與類之間存在特殊的關係，例如下圖中：

![1544861202252](assets/1544861202252.png)

我們發現，定義這些類時，下級別的成員除了擁有上一級的共性，還有自己的特性。

這個時候我們就可以考慮利用繼承的技術，減少重複程式碼



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
		cout << "JAVA學科影片" << endl;
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
		cout << "Python學科影片" << endl;
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
		cout << "C++學科影片" << endl;
	}
};

void test01()
{
	//Java頁面
	cout << "Java下載影片頁面如下： " << endl;
	Java ja;
	ja.header();
	ja.footer();
	ja.left();
	ja.content();
	cout << "--------------------" << endl;

	//Python頁面
	cout << "Python下載影片頁面如下： " << endl;
	Python py;
	py.header();
	py.footer();
	py.left();
	py.content();
	cout << "--------------------" << endl;

	//C++頁面
	cout << "C++下載影片頁面如下： " << endl;
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
		cout << "JAVA學科影片" << endl;
	}
};
//Python頁面
class Python : public BasePage
{
public:
	void content()
	{
		cout << "Python學科影片" << endl;
	}
};
//C++頁面
class CPP : public BasePage
{
public:
	void content()
	{
		cout << "C++學科影片" << endl;
	}
};

void test01()
{
	//Java頁面
	cout << "Java下載影片頁面如下： " << endl;
	Java ja;
	ja.header();
	ja.footer();
	ja.left();
	ja.content();
	cout << "--------------------" << endl;

	//Python頁面
	cout << "Python下載影片頁面如下： " << endl;
	Python py;
	py.header();
	py.footer();
	py.left();
	py.content();
	cout << "--------------------" << endl;

	//C++頁面
	cout << "C++下載影片頁面如下： " << endl;
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

繼承的好處：==可以減少重複的程式碼==

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









#### 4.6.3 繼承中的物件模型



**問題：**從父類繼承過來的成員，哪些屬於子類物件中？



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



打開工具窗口後，定位元元到當前CPP檔案的盤符

然後輸入： cl /d1 reportSingleClassLayout查看的類名   所屬檔案名



效果如下圖：



![1545882158050](assets/1545882158050.png)



> 結論： 父類中私有成員也是被子類繼承下去了，只是由編譯器給隱藏後訪問不到



















#### 4.6.4 繼承中建構和解構順序



子類繼承父類後，當創建子類物件，也會調用父類的建構函式



問題：父類和子類的建構和解構順序是誰先誰後？



**示例：**

```C++
class Base 
{
public:
	Base()
	{
		cout << "Base建構函式!" << endl;
	}
	~Base()
	{
		cout << "Base解構函式!" << endl;
	}
};

class Son : public Base
{
public:
	Son()
	{
		cout << "Son建構函式!" << endl;
	}
	~Son()
	{
		cout << "Son解構函式!" << endl;
	}

};


void test01()
{
	//繼承中 先調用父類建構函式，再調用子類建構函式，解構順序與建構相反
	Son s;
}

int main() {

	test01();

	system("pause");

	return 0;
}
```



> 總結：繼承中 先調用父類建構函式，再調用子類建構函式，解構順序與建構相反











#### 4.6.5 繼承同名成員處理方式



問題：當子類與父類出現同名的成員，如何通過子類物件，訪問到子類或父類中同名的數據呢？



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

	//當子類與父類擁有同名的成員函式，子類會隱藏父類中所有版本的同名成員函式
	//如果想訪問父類中被隱藏的同名成員函式，需要加父類的作用域
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

1. 子類物件可以直接訪問到子類中同名成員
2. 子類物件加作用域可以訪問到父類同名成員
3. 當子類與父類擁有同名的成員函式，子類會隱藏父類中同名成員函式，加作用域可以訪問到父類中同名函式













#### 4.6.6 繼承同名靜態成員處理方式



問題：繼承中同名的靜態成員在子類物件上如何進行訪問？



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
	//通過物件訪問
	cout << "通過物件訪問： " << endl;
	Son s;
	cout << "Son  下 m_A = " << s.m_A << endl;
	cout << "Base 下 m_A = " << s.Base::m_A << endl;

	//通過類名訪問
	cout << "通過類名訪問： " << endl;
	cout << "Son  下 m_A = " << Son::m_A << endl;
	cout << "Base 下 m_A = " << Son::Base::m_A << endl;
}

//同名成員函式
void test02()
{
	//通過物件訪問
	cout << "通過物件訪問： " << endl;
	Son s;
	s.func();
	s.Base::func();

	cout << "通過類名訪問： " << endl;
	Son::func();
	Son::Base::func();
	//出現同名，子類會隱藏掉父類中所有同名成員函式，需要加作作用域訪問
	Son::Base::func(100);
}
int main() {

	//test01();
	test02();

	system("pause");

	return 0;
}
```

> 總結：同名靜態成員處理方式和非靜態處理方式一樣，只不過有兩種訪問的方式（通過物件 和 通過類名）













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



















### 4.7  多型

#### 4.7.1 多型的基本概念



**多型是C++面向物件三大特性之一**

多型分為兩類

* 靜態多型: 函式多載 和 運算子多載屬於靜態多型，複用函式名
* 動態多型: 派生類和虛擬函式實現運行時多型



靜態多型和動態多型區別：

* 靜態多型的函式地址早綁定  -  編譯階段確定函式地址
* 動態多型的函式地址晚綁定  -  運行階段確定函式地址



下面通過案例進行講解多型



```C++
class Animal
{
public:
	//Speak函式就是虛擬函式
	//函式前面加上virtual關鍵字，變成虛擬函式，那麼編譯器在編譯的時候就不能確定函式調用了。
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
//我們希望傳入什麼物件，那麼就調用什麼物件的函式
//如果函式地址在編譯階段就能確定，那麼靜態聯編
//如果函式地址在運行階段才能確定，就是動態聯編

void DoSpeak(Animal & animal)
{
	animal.speak();
}
//
//多型滿足條件： 
//1、有繼承關係
//2、子類覆寫父類中的虛擬函式
//多型使用：
//父類指標或參照指向子類物件

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

多型滿足條件

* 有繼承關係
* 子類覆寫父類中的虛擬函式

多型使用條件

* 父類指標或參照指向子類物件

覆寫：函式回傳值型別  函式名 參數列表 完全一致稱為覆寫









#### 4.7.2 多型案例一-計算器類



案例描述：

分別利用普通寫法和多型技術，設計實現兩個操作數進行運算的計算器類



多型的優點：

* 程式碼組織結構清晰
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



//多型實現
//抽象計算器類
//多型優點：程式碼組織結構清晰，可讀性強，利於前期和後期的擴展以及維護
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

> 總結：C++開發提倡利用多型設計程式架構，因為多型優點很多

















#### 4.7.3 純虛擬函式和抽象類



在多型中，通常父類中虛擬函式的實現是毫無意義的，主要都是調用子類覆寫的內容



因此可以將虛擬函式改為**純虛擬函式**



純虛擬函式語法：`virtual 回傳值型別 函式名 （參數列表）= 0 ;`



當類中有了純虛擬函式，這個類也稱為==抽象類==



**抽象類特點**：

 * 無法實體化物件
 * 子類必須覆寫抽象類中的純虛擬函式，否則也屬於抽象類





**示例：**

```C++
class Base
{
public:
	//純虛擬函式
	//類中只要有一個純虛擬函式就稱為抽象類
	//抽象類無法實體化物件
	//子類必須覆寫父類中的純虛擬函式，否則也屬於抽象類
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
	//base = new Base; // 錯誤，抽象類無法實體化物件
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















#### 4.7.4 多型案例二-製作飲品

**案例描述：**

製作飲品的大致流程為：煮水 -  沖泡 - 倒入杯中 - 加入輔料



利用多型技術實現本案例，提供抽象製作飲品基類，提供子類製作咖啡和茶葉



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

//業務函式
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



















#### 4.7.5 虛解構和純虛解構



多型使用時，如果子類中有屬性開闢到堆區，那麼父類指標在釋放時無法調用到子類的解構程式碼



解決方式：將父類中的解構函式改為**虛解構**或者**純虛解構**



虛解構和純虛解構共性：

* 可以解決父類指標釋放子類物件
* 都需要有具體的函式實現

虛解構和純虛解構區別：

* 如果是純虛解構，該類屬於抽象類，無法實體化物件



虛解構語法：

`virtual ~類名(){}`

純虛解構語法：

` virtual ~類名() = 0;`

`類名::~類名(){}`



**示例：**

```C++
class Animal {
public:

	Animal()
	{
		cout << "Animal 建構函式調用！" << endl;
	}
	virtual void Speak() = 0;

	//解構函式加上virtual關鍵字，變成虛解構函式
	//virtual ~Animal()
	//{
	//	cout << "Animal虛解構函式調用！" << endl;
	//}


	virtual ~Animal() = 0;
};

Animal::~Animal()
{
	cout << "Animal 純虛解構函式調用！" << endl;
}

//和包含普通純虛擬函式的類一樣，包含了純虛解構函式的類也是一個抽象類。不能夠被實體化。

class Cat : public Animal {
public:
	Cat(string name)
	{
		cout << "Cat建構函式調用！" << endl;
		m_Name = new string(name);
	}
	virtual void Speak()
	{
		cout << *m_Name <<  "小貓在說話!" << endl;
	}
	~Cat()
	{
		cout << "Cat解構函式調用!" << endl;
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

	//通過父類指標去釋放，會導致子類物件可能清理不乾淨，造成記憶體洩漏
	//怎麼解決？給基類增加一個虛解構函式
	//虛解構函式就是用來解決通過父類指標釋放子類物件
	delete animal;
}

int main() {

	test01();

	system("pause");

	return 0;
}
```



總結：

​	1. 虛解構或純虛解構就是用來解決通過父類指標釋放子類物件

​	2. 如果子類中沒有堆區數據，可以不寫為虛解構或純虛解構

​	3. 擁有純虛解構函式的類也屬於抽象類















#### 4.7.6 多型案例三-電腦組裝



**案例描述：**



電腦主要組成部件為 CPU（用於計算），顯示卡（用於顯示），記憶體條（用於存儲）

將每個零件封裝出抽象基類，並且提供不同的廠商生產不同的零件，例如Intel廠商和Lenovo廠商

創建電腦類提供讓電腦工作的函式，並且調用每個零件工作的介面

測試時組裝三臺不同的電腦進行工作





**示例：**

```C++
#include<iostream>
using namespace std;

//抽象CPU類
class CPU
{
public:
	//抽象的計算函式
	virtual void calculate() = 0;
};

//抽象顯示卡類
class VideoCard
{
public:
	//抽象的顯示函式
	virtual void display() = 0;
};

//抽象記憶體條類
class Memory
{
public:
	//抽象的存儲函式
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

	//提供工作的函式
	void work()
	{
		//讓零件工作起來，調用介面
		m_cpu->calculate();

		m_vc->display();

		m_mem->storage();
	}

	//提供解構函式 釋放3個電腦零件
	~Computer()
	{

		//釋放CPU零件
		if (m_cpu != NULL)
		{
			delete m_cpu;
			m_cpu = NULL;
		}

		//釋放顯示卡零件
		if (m_vc != NULL)
		{
			delete m_vc;
			m_vc = NULL;
		}

		//釋放記憶體條零件
		if (m_mem != NULL)
		{
			delete m_mem;
			m_mem = NULL;
		}
	}

private:

	CPU * m_cpu; //CPU的零件指標
	VideoCard * m_vc; //顯示卡零件指標
	Memory * m_mem; //記憶體條零件指標
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
		cout << "Intel的顯示卡開始顯示了！" << endl;
	}
};

class IntelMemory :public Memory
{
public:
	virtual void storage()
	{
		cout << "Intel的記憶體條開始存儲了！" << endl;
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
		cout << "Lenovo的顯示卡開始顯示了！" << endl;
	}
};

class LenovoMemory :public Memory
{
public:
	virtual void storage()
	{
		cout << "Lenovo的記憶體條開始存儲了！" << endl;
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













## 5 檔案操作



程式運行時產生的數據都屬於臨時數據，程式一旦運行結束都會被釋放

通過**檔案可以將數據持久化**

C++中對檔案操作需要包含頭檔案 ==&lt; fstream &gt;==



檔案型別分為兩種：

1. **文本檔案**     -  檔案以文本的**ASCII碼**形式存儲在電腦中
2. **二進制檔案** -  檔案以文本的**二進制**形式存儲在電腦中，用戶一般不能直接讀懂它們



操作檔案的三大類:

1. ofstream：寫操作
2. ifstream： 讀操作
3. fstream ： 讀寫操作



### 5.1文本檔案

#### 5.1.1寫檔案

   寫檔案步驟如下：

1. 包含頭檔案   

     \#include <fstream\>

2. 創建流物件  

   ofstream ofs;

3. 打開檔案

   ofs.open("檔案路徑",打開方式);

4. 寫數據

   ofs << "寫入的數據";

5. 關閉檔案

   ofs.close();

   ​

檔案打開方式：

| 打開方式    | 解釋                       |
| ----------- | -------------------------- |
| ios::in     | 為讀檔案而打開檔案         |
| ios::out    | 為寫檔案而打開檔案         |
| ios::ate    | 初始位元元置：檔案尾           |
| ios::app    | 追加方式寫檔案             |
| ios::trunc  | 如果檔案存在先刪除，再創建 |
| ios::binary | 二進制方式                 |

**注意：** 檔案打開方式可以配合使用，利用|操作符

**例如：**用二進制方式寫檔案 `ios::binary |  ios:: out`





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

* 檔案操作必須包含頭檔案 fstream
* 讀檔案可以利用 ofstream  ，或者fstream類
* 打開檔案時候需要指定操作檔案的路徑，以及打開方式
* 利用<<可以向檔案中寫數據
* 操作完畢，要關閉檔案

















#### 5.1.2讀檔案



讀檔案與寫檔案步驟相似，但是讀取方式相對於比較多



讀檔案步驟如下：

1. 包含頭檔案   

     \#include <fstream\>

2. 創建流物件  

   ifstream ifs;

3. 打開檔案並判斷檔案是否打開成功

   ifs.open("檔案路徑",打開方式);

4. 讀數據

   四種方式讀取

5. 關閉檔案

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
		cout << "檔案打開失敗" << endl;
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

- 讀檔案可以利用 ifstream  ，或者fstream類
- 利用is_open函式可以判斷檔案是否打開成功
- close 關閉檔案 















### 5.2 二進制檔案

以二進制的方式對檔案進行讀寫操作

打開方式要指定為 ==ios::binary==



#### 5.2.1 寫檔案

二進制方式寫檔案主要利用流物件調用成員函式write

函式原型 ：`ostream& write(const char * buffer,int len);`

參數解釋：字符指標buffer指向記憶體中一段存儲空間。len是讀寫的位元元組數



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

//二進制檔案  寫檔案
void test01()
{
	//1、包含頭檔案

	//2、創建輸出流物件
	ofstream ofs("person.txt", ios::out | ios::binary);
	
	//3、打開檔案
	//ofs.open("person.txt", ios::out | ios::binary);

	Person p = {"張三"  , 18};

	//4、寫檔案
	ofs.write((const char *)&p, sizeof(p));

	//5、關閉檔案
	ofs.close();
}

int main() {

	test01();

	system("pause");

	return 0;
}
```

總結：

* 檔案輸出流物件 可以通過write函式，以二進制方式寫數據











#### 5.2.2 讀檔案

二進制方式讀檔案主要利用流物件調用成員函式read

函式原型：`istream& read(char *buffer,int len);`

參數解釋：字符指標buffer指向記憶體中一段存儲空間。len是讀寫的位元元組數

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
		cout << "檔案打開失敗" << endl;
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



- 檔案輸入流物件 可以通過read函式，以二進制方式讀數據

