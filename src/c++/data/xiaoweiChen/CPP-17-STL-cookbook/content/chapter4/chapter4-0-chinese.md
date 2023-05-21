# 第4章 Lambda表達式

Lambda表達式是C++11添加的非常重要的一個特性。C++14和C++17對Lambda進行補充，使得Lambda表達式如虎添翼。那就先了解一下，什麼是Lambda表達式呢？

Lambda表達式或者Lambda函數為閉包結構。閉包是描述未命名對象的通用術語，也可以稱為匿名函數。為了在C++中加入這個特性，就需要相應對象實現`()`括號操作符。C++11之前想要實現類似具有Lambda的對象，代碼如下所示：

```c++
#include <iostream>
#include <string>
int main() {
    struct name_greeter {
        std::string name;
        
        void operator()() {
        	std::cout << "Hello, " << name << '\n';
        }
    };
    
    name_greeter greet_john_doe {"John Doe"};
    greet_john_doe();
}
```

構造`name_greeter`對象需要傳入一個字符串。這裡需要注意的是，這個結構類型，Lambda可以使用一個沒有名字的實例來表示。對於閉包結構來說，我們稱之為捕獲一個字符串。其就像我們在構造這個例子中的實例時傳入的字符串一樣，不過Lambda不需要參數，就能完成打印`Hello, John Doe`。

C++11之後，使用閉包的方式來實現會更加簡單：

```c++
#include <iostream>
int main() {
    auto greet_john_doe ([] {
    	std::cout << "Hello, John Doe\n";
    });
    greet_john_doe();
}
```

這樣就行了！不再需要`name_greeter`結構體，直接使用Lambda表達式替代。這看起來像魔術一樣，本章的第一節中會對細節進行詳細的描述。

Lambda表達式對於完成通用和簡介類代碼是非常有幫助的。其能對通用的數據結構進行處理，這樣就不懼用戶指定的特殊類型。閉包結構也會被用來將運行在線程上的數據進行打包。C++11標準推出後，越來越多的庫支持了Lambda表達式，因為這對於C++來說已經是很自然的事情了。另一種使用方式是用於元編程，因為Lambda在編譯時是可以進行預估的。不過，我們不會往元編程的方向去講述，元編程的內容可能會撐爆這本書。

本章我們著重於函數式編程，對於那些對函數式編程不瞭解的開發者或初學者來說，這看起來非常的神奇。如果你在代碼中看到Lambda表達式橫飛，請先別沮喪。在這個函數式編程越來越流行的年代，需要拓展對於現代C++的瞭解。如果你看到的代碼有點複雜，建議你多花點時間去分析它們。當你馴服了Lambda表達式，你就能駕馭它馳騁疆場，不再會為之困惑。

