# 附錄B 併發庫的簡單比較

雖然，C++11才開始正式支持併發，不過高級編程語言都支持併發和多線程已經不是什麼新鮮事了。例如，Java在第一個發佈版本中就支持多線程編程，在某些平臺上也提供符合POSIX C標準的多線程接口，還有[Erlang](http://www.erlang.org/)支持消息的同步傳遞(有點類似於MPI)。當然還有使用C++類的庫，比如Boost，其將底層多線程接口進行包裝，適用於任何給定的平臺(不論是使用POSIX C的接口，或其他接口)，其對支持的平臺會提供可移植接口。

這些庫或者編程語言，已經寫了很多多線程應用，並且在使用這些庫寫多線程代碼的經驗，可以借鑑到C++中，本附錄就對Java，POSIX C，使用Boost線程庫的C++，以及C++11中的多線程工具進行簡單的比較，當然也會交叉引用本書的相關章節。

<table border=1>
  <td> 特性 </td>
  <td> 啟動線程 </td>
  <td> 互斥量 </td>
  <td> 監視/等待謂詞 </td>
  <td> 原子操作和併發感知內存模型 </td>
  <td> 線程安全容器 </td>
  <td> Futures(期望) </td>
  <td> 線程池 </td>
  <td> 線程中斷 </td>
<tr>
  <td>章節引用</td>
  <td>第2章</td>
  <td>第3章</td>
  <td>第4章</td>
  <td>第5章</td>
  <td>第6章和第7章</td>
  <td>第4章</td>
  <td>第9章</td>
  <td>第9章</td>
</tr>
<tr>
  <td rowspan=3> C++11 </td>
  <td rowspan=3> std::thread和其成員函數 </td>
  <td> std::mutex類和其成員函數 </td>
  <td> std::condition_variable </td>
  <td> std::atomic_xxx類型 </td>
  <td rowspan=3> N/A </td>
  <td> std::future<> </td>
  <td rowspan=3> N/A </td>
  <td rowspan=3> N/A </td>
</tr>
<tr>
  <td> std::lock_guard<>模板 </td>
  <td rowspan=2> std::condition_variable_any類和其成員函數 </td>
  <td> std::atomic<>類模板 </td>
  <td> std::shared_future<> </td>
</tr>
<tr>
  <td> std::unique_lock<>模板 </td>
  <td> std::atomic_thread_fence()函數 </td>
  <td> std::atomic_future<>類模板 </td>
</tr>
<tr>
  <td rowspan=3> Boost線程庫 </td>
  <td rowspan=3> boost::thread類和成員函數 </td>
  <td> boost::mutex類和其成員函數 </td>
  <td> boost::condition_variable類和其成員函數 </td>
  <td rowspan=3> N/A </td>
  <td rowspan=3> N/A </td>
  <td> boost::unique_future<>類模板</td>
  <td rowspan=3> N/A </td>
  <td rowspan=3> boost::thread類的interrupt()成員函數</td>
</tr>
<tr>
  <td> boost::lock_guard<>類模板 </td>
  <td rowspan=2> boost::condition_variable_any類和其成員函數 </td>
  <td rowspan=2> boost::shared_future<>類模板</td>
</tr>
<tr>
  <td> boost::unique_lock<>類模板 </td>
</tr>
<tr>
  <td rowspan=4> POSIX C </td>
  <td> pthread_t類型相關的API函數 </td>
  <td> pthread_mutex_t類型相關的API函數</td>
  <td> pthread_cond_t類型相關的API函數</td>
  <td rowspan=4> N/A </td>
  <td rowspan=4> N/A </td>
  <td rowspan=4> N/A </td>
  <td rowspan=4> N/A </td>
  <td rowspan=4> pthread_cancel() </td>
</tr>
<tr>
  <td> pthread_create() </td>
  <td> pthread_mutex_lock() </td>
  <td> pthread_cond_wait() </td>
</tr>
<tr>
  <td> pthread_detach() </td>
  <td> pthread_mutex_unlock() </td>
  <td> pthread_cond_timed_wait() </td>
</tr>
<tr>
  <td> pthread_join() </td>
  <td> 等等 </td>
  <td> 等等 </td>
</tr>
<tr>
  <td> Java </td>
  <td> java.lang.thread類 </td>
  <td> synchronized塊 </td>
  <td> java.lang.Object類的wait()和notify()函數，用在內部synchronized塊中 </td>
  <td> java.util.concurrent.atomic包中的volatile類型變量 </td>
  <td> java.util.concurrent包中的容器 </td>
  <td> 與java.util.concurrent.future接口相關的類 </td>
  <td> java.util.concurrent.ThreadPoolExecutor類 </td>
  <td> java.lang.Thread類的interrupt()函數 </td>
</tr>
</table>

