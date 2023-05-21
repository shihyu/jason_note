# 轉換絕對時間和相對時間——std::chrono

C++11之前，想要獲取時間並對其打印是有些困難的，因為C++並沒有標準時間庫。想要對時間進行統計就需要調用C庫，並且我們要考慮這樣的調用是否能很好的封裝到我們的類中。

C++11之後，STL提供了`chrono`庫，其讓對時間的操作更加簡單。

本節，我們將會使用本地時間，並對本地時間進行打印，還會給時間加上不同的偏移，這些操作很容易使用`std::chrono`完成。

## How to do it...

我們將會對當前時間進行保存，並對其進行打印。另外，我們的程序還會為已經保存的時間點添加不同的偏移，並且打印偏移之後的時間：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <iomanip>
   #include <chrono>
   
   using namespace std; 
   ```

2. 我們將打印絕對時間點。使用`chrono::time_point`模板類型來獲取，因此需要對輸出流操作符進行重載。對時間點的打印方式有很多，我們將會使用`%c`來表示標準時間格式。當然，可以只打印時間、日期或是我們需要的信息。調用`put_time`之前對不同類型的變量進行轉換的方式看起來有些笨拙，不過這裡只這麼做一次：

   ```c++
   ostream& operator<<(ostream &os,
   	const chrono::time_point<chrono::system_clock> &t)
   {
       const auto tt (chrono::system_clock::to_time_t(t));
       const auto loct (std::localtime(&tt));
       return os << put_time(loct, "%c");
   }
   ```

3. STL已經定義了`seconds`，`minutes`，`hours`等時間類型，所以我們只需要為其添加`days`類型就好。這很簡單，只需要對`chrono::duration`模板類型進行特化，將hours類型乘以24，就表示一天具有24個小時：

   ```c++
   using days = chrono::duration<
       chrono::hours::rep,
       ratio_multiply<chrono::hours::period, ratio<24>>>;
   ```

4. 為了用很有優雅的方式表示很多天，我們定義屬於`days`類型的字面值操作符。現在我們程序中寫`3_days`就代表著3天：

   ```c++
   constexpr days operator ""_days(unsigned long long d)
   {
   	return days{d};
   }
   ```

5. 實際程序中，我們將會對時間點進行記錄，然後就會對這個時間點進行打印。因為已經對操作符進行了重載，所以完成這樣的事情就變得很簡單：

   ```c++
   int main()
   {
       auto now (chrono::system_clock::now());
       
       cout << "The current date and time is " << now << '\n'; 
   ```

6. 我們使用`now`函數來獲得當前的時間點，並可以為這個時間添加一個偏移，然後再對其進行打印。為當前的時間添加12個小時，其表示的為12個小時之後的時間：

   ```c++
   	chrono::hours chrono_12h {12};
   	
   	cout << "In 12 hours, it will be "
   		<< (now + chrono_12h)<< '\n';
   ```

7. 這裡將使用`chrono_literals`命名空間中的函數，聲明使用這個命名空間會解鎖小時、秒等等時間類型的間隔字面值類型。這樣我們就能很優雅的對12個小時15分之前的時間或7天之前的時間進行打印：

   ```c++
       using namespace chrono_literals;
       
   	cout << "12 hours and 15 minutes ago, it was "
           << (now - 12h - 15min) << '\n'
           << "1 week ago, it was "
           << (now - 7_days) << '\n';
   } 
   ```

8. 編譯並運行程序，我們將會獲得如下的輸出。因為使用`%c`格式對時間進行打印，所以得到還不錯的時間輸出格式。通過對不同格式的的字符串進行操作，我們可以獲得想要的格式。要注意的是，這裡的時間格式並不是以12小時AM/PM方式表示，因為程序運行在歐洲操作系統上，所以使用24小時表示的方式：

   ```c++
   $ ./relative_absolute_times
   The current date and time is Fri May 5 13:20:38 2017
   In 12 hours, it will be Sat May6 01:20:38 2017
   12 hours and 15 minutes ago, it was Fri May5 01:05:38 2017
   1 week ago, it was Fri Apr 28 13:20:38 2017
   ```

## How it works...

我們可以通過`std::chrono::system_clock`來獲取當前時間點。這個STL時鐘類是唯一一個能將時間點的值轉換成一個時間結構體的類型，其能將時間點以能夠看懂的方式進行輸出。

為了打印這樣的時間點，我們可以對`operator<<`操作符進行重載：

```c++
ostream& operator<<(ostream &os,
				   const chrono::time_point<chrono::system_clock> &t)
{
    const auto tt (chrono::system_clock::to_time_t(t));
    const auto loct (std::localtime(&tt));
    return os << put_time(loct, "%c");
}
```

首先，將`chrono::time_point<chrono::system_clock>`轉換為`std::time_t`。然後，使用`std::localtime`將這個時間值進行轉換，這樣就能獲取到一個本地時鐘的相對時間值。這個函數會給我們返回一個轉換後的指針(對於這個指針背後的內存不用我們多操心，因為其是一個靜態對象，並不是從堆上分配的內存)，這樣我們就能完成最終的打印。

`std::put_time`函數接受一個流對象和一個時間格式字符串。`%c`表示標準時間格式字符串，例如`Sun Mar 12 11:33:40 2017 `。我們也可以寫成`%m/%d/%y`；之後，時間就會按照這個格式進行打印，比如`03/12/17`。時間格式符的描述很長，想要了解其具體描述的最好方式就是去查看C++參考手冊。

除了打印，我們也會為我們的時間點添加偏移。這也很簡單，比如：12小時15分鐘就可以表示為`12h+15min`。`chrono_literals`命名空間為我們提供了字面類型：`hours(h), minutes(min), seconds(s), milliseconds(ms), microseconds(us), nanoseconds(ns)`。

通過對兩個時間間隔的相加，我們會得到一個新的時間點。要實現這樣的操作就需要對左加`operator+`和左減`operator-`操作符進行重載，這樣對時間偏移的操作就會變得非常簡單。