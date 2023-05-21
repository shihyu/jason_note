# 並行ASCII曼德爾布羅特渲染器——std::async

還記得第6章中的[ASCII曼德爾布羅特渲染器](content/chapter6/chapter6-5-chinese.md)嗎？本節中，我們將使用多線程來加速其計算的過程。

原始代碼中會限定每個座標的迭代次數，座標的迭代會讓程序變得很慢，現在我們使用並行方式對其進行實現。

然後，我們對代碼做少量的修改，並且將`std::async`和`std::future`加入到程序中，讓程序運行的更快。想要完全理解本節，就要對原始的程序有個較為完整的瞭解。

## How to do it...

本節中，我們將對曼德爾布羅特渲染器進行升級。首先，要提升對選定座標迭代計算的次數。然後，通過程序並行化，來提高運行的速度：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <algorithm>
   #include <iterator>
   #include <complex>
   #include <numeric>
   #include <vector>
   #include <future>
   
   using namespace std;
   ```

2. `scaler` 和`scaled_cmplx`沒有任何改動：

   ```c++
   using cmplx = complex<double>;
   
   static auto scaler(int min_from, int max_from,
   					double min_to, double max_to)
   {
   	const int w_from {max_from - min_from};
   	const double w_to {max_to - min_to};
   	const int mid_from {(max_from - min_from) / 2 + min_from};
   	const double mid_to {(max_to - min_to) / 2.0 + min_to};
   
       return [=] (int from) {
   		return double(from - mid_from) / w_from * w_to + mid_to;
   	};
   }
   
   template <typename A, typename B>
   static auto scaled_cmplx(A scaler_x, B scaler_y)
   {
   	return [=](int x, int y) {
   		return cmplx{scaler_x(x), scaler_y(y)};
   	};
   }
   ```

3. `mandelbrot_iterations`函數中會增加迭代的次數，為的就是增加計算負荷：

   ```c++
   static auto mandelbrot_iterations(cmplx c)
   {
       cmplx z {};
       size_t iterations {0};
       const size_t max_iterations {100000};
       while (abs(z) < 2 && iterations < max_iterations) {
           ++iterations;
           z = pow(z, 2) + c;
       }
       return iterations;
   }
   ```

4. 主函數中的部分代碼也不需要進行任何修改：

   ```c++
   int main()
   {
       const size_t w {100};
       const size_t h {40};
       
       auto scale (scaled_cmplx(
           scaler(0, w, -2.0, 1.0),
           scaler(0, h, -1.0, 1.0)
       ));
       
       auto i_to_xy ([=](int x) {
      		return scale(x % w, x / w);
       }); 
   ```

5. `to_iteration_count`函數中，不能直接調用`mandelbrot_iterations(x_to_xy(x))`，需要使用異步函數` std::async `：

   ```c++
       auto to_iteration_count ([=](int x) {
           return async(launch::async,
           			mandelbrot_iterations, i_to_xy(x));
       });	
   ```

6. 進行最後的修改之前，函數`to_iteration_count`會返回特定座標需要迭代的次數。那麼就會返回一個`future`變量，這個變量用於在後面獲取異步結果時使用。因此，需要一個`vector`來盛放所有`future`變量，所以我們就在這裡添加了一個。將輸出迭代器作為第三個參數傳入`transform`函數，並在`vector`變量`r`中放入新的輸出：

   ```c++
   	vector<int> v (w * h);
       vector<future<size_t>> r (w * h);
       iota(begin(v), end(v), 0);
       transform(begin(v), end(v), begin(r),
       		 to_iteration_count);
   ```

7. `accumulate`不會在對第二個參數中`size_t`的值進行打印，不過這次改成了`future<size_t>`。我們需要花點時間對這個類型進行適應(對於一些初學者來說，這裡使用`auto&`類型的話可能會讓其產生疑惑)，之後需要調用`x.get()`來訪問`x`中的值，如果`x`中的值還沒計算出來，程序將會阻塞進行等待：

   ```c++
       auto binfunc ([w, n{0}] (auto output_it, future<size_t> &x)
       		mutable {
       	*++output_it = (x.get() > 50 ? '*' : ' ');
       	if (++n % w == 0) { ++output_it = '\n'; }
      	 	return output_it;
       });
                     
       accumulate(begin(r), end(r),
       		  ostream_iterator<char>{cout}, binfunc);
   }
   ```

8. 編譯並運行程序，我們也能得到和之前一樣的輸出。唯一不同的就是執行的速度。我們增加了原始版本的迭代次數，程序應該會更慢，不過好在有並行化的幫助，我們能夠計算的更快。我的機器上有4個CPU核，並且支持超線程(也就是有8個虛擬核)，我使用GCC和clang得到了不同結果。最好的加速效果有5.3倍，最差也有3.8倍。當然，這個結果和機器的很多狀態有關。

## How it works...

理解本節代碼的關鍵就在於下面這句和CPU強相關的代碼行：

```c++
transform(begin(v), end(v), begin(r), to_iteration_count);
```

`vector v`中包含了所有複數座標，然後這些座標會通過曼德爾布羅特算法進行迭代。每次的迭代結果則會保存在`vector r`中。

原始代碼中，我們將所要繪製的分形圖形保存為一維數據。代碼則會對之前所有的工作結果進行打印。這也就意味著並行化是提升性能的一個關鍵因素。

唯一可能並行化的部分就是從`begin(v)`到`end(v)`的處理，每塊都具有相同尺寸，並能夠分佈在所有核上。這樣所有核將會對輸入數據進行共享。如果使用並行版本的`std::transform`，就需要帶上一個執行策略。不幸的是，這不是問題的正確解決方式，因為每一個曼德爾布羅特集合中的點，迭代的次數是不同的。

我們的方式是使用一個`vector`收集將要獲取每個點所要計算的數量的`future`變量。代碼中`vector`能容納`w * h`個元素，例子中就是`100 * 40`，也就是說`vector`實例中存儲了4000個`future`變量，這些變量都會在異步計算中得到屬於自己的值。如果我們的系統有4000個CPU核，就可以啟動4000個併發的對座標進行迭代計算。一個常見的機器上並沒有那麼多核，CPU只能是異步的對於一個元素進行處理，處理完成後再繼續下一個。

`to_iteration_count`中調用異步版本的`transform`時，並不是去計算，而是對線程進行部署，然後立即獲得對應的`future`對象。原始版本會在每個點上阻塞很久，因為迭代需要花費很長時間。

並行版本的程序，也有可能會在那裡發生阻塞。打印函數所打印出的結果必須要從`future`對象中獲取，為了完成這個目的，我們調用`x.get()`用來獲取所有結果。訣竅就在這裡：等待第一個值被打印時，其他值也同時在計算。所以，當調用`get()`返回時，下一個`future`的結果也會很快地被打印出來！

當`w * h`是一個非常大的數時，創建`future`對象和同步`future`對象的開銷將會非常可觀。本節的例子中，這裡的開銷並不明顯。我的筆記本上有一個i7 4核超線程的CPU(也就是有8個虛擬核)，並行版本與原始版本對比有3-5倍的加速，理想的並行加速應該是8倍。當然，影響機器的因素有很多，並且不同的機器也會有不同的加速比。