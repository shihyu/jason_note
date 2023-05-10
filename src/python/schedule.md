```python
from multiprocessing import Process
from datetime import datetime
import time
import os

from schedule import Scheduler

class MPScheduler(Scheduler):
    def __init__(self, args=None, kwargs=None):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        super(MPScheduler, self).__init__(*args, **kwargs)
        # Among other things, this object inherits self.jobs (a list of jobs)
        self.args = args
        self.kwargs = kwargs
        self.processes = list()

    def _mp_run_job(self, job_func):
        """Spawn another process to run the job; multiprocessing avoids GIL issues"""
        job_process = Process(target=job_func, args=self.args,
            kwargs=self.kwargs)
        job_process.daemon = True
        job_process.start()
        self.processes.append(job_process)

    def run_pending(self):
        """Run any jobs which are ready"""
        runnable_jobs = (job_obj for job_obj in self.jobs if job_obj.should_run)
        for job_obj in sorted(runnable_jobs):
            job_obj.last_run = datetime.now()   # Housekeeping
            self._mp_run_job(job_obj.job_func)
            job_obj._schedule_next_run()        # Schedule the next execution datetime

        self._retire_finished_processes()

    def _retire_finished_processes(self):
        """Walk the list of processes and retire finished processes"""
        retirement_list = list()   # List of process objects to remove
        for idx, process in enumerate(self.processes):
            if process.is_alive():
                # wait a short time for process to finish
                process.join(0.01)
            else:
                retirement_list.append(idx)

        ## Retire finished processes
        for process_idx in sorted(retirement_list, reverse=True):
            self.processes.pop(process_idx)

def job(id, hungry=True):
    print("{} running {} and hungry={}".format(datetime.now(), id, hungry))
    time.sleep(10)   # This job runs without blocking execution of other jobs

if __name__=='__main__':
    # Build a schedule of overlapping jobs...
    mp_sched = MPScheduler()
    mp_sched.every(1).seconds.do(job, id=1, hungry=False)
    mp_sched.every(2).seconds.do(job, id=2)
    mp_sched.every(3).seconds.do(job, id=3)
    mp_sched.every(4).seconds.do(job, id=4)
    mp_sched.every(5).seconds.do(job, id=5)

    while True:
        mp_sched.run_pending()
        time.sleep(1)
```





# Parallel execution

https://schedule.readthedocs.io/en/stable/parallel-execution.html

 *am trying to execute 50 items every 10 seconds, but from the my logs it says it executes every item in 10 second schedule serially, is there a work around?*

By default, schedule executes all jobs serially. The reasoning behind this is that it would be difficult to find a model for parallel execution that makes everyone happy.

You can work around this limitation by running each of the jobs in its own thread:

```python
import threading
import time
import schedule

def job():
    print("I'm running on thread %s" % threading.current_thread())

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every(10).seconds.do(run_threaded, job)
schedule.every(10).seconds.do(run_threaded, job)
schedule.every(10).seconds.do(run_threaded, job)
schedule.every(10).seconds.do(run_threaded, job)
schedule.every(10).seconds.do(run_threaded, job)


while 1:
    schedule.run_pending()
    time.sleep(1)
```

If you want tighter control on the number of threads use a shared jobqueue and one or more worker threads:

```python
import time
import threading
import schedule
import queue

def job():
    print("I'm working")


def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()

jobqueue = queue.Queue()

schedule.every(10).seconds.do(jobqueue.put, job)
schedule.every(10).seconds.do(jobqueue.put, job)
schedule.every(10).seconds.do(jobqueue.put, job)
schedule.every(10).seconds.do(jobqueue.put, job)
schedule.every(10).seconds.do(jobqueue.put, job)

worker_thread = threading.Thread(target=worker_main)
worker_thread.start()

while 1:
    schedule.run_pending()
    time.sleep(1)
```

This model also makes sense for a distributed application where the workers are separate processes that receive jobs from a distributed work queue. I like using beanstalkd with the beanstalkc Python library.



# python 任務調度之 schedule



http://puremonkey2010.blogspot.com/2019/05/python-python-schedule.html



在工作中多少都會涉及到一些定時任務，比如定時郵件提醒等.本文通過開源項目 [**schedule**](https://github.com/dbader/schedule) 來學習定時任務調度是如何工作的，以及基於此實現一個 web 版本的提醒工具. 

```py
import threading
import schedule
import time


def job():
    print(f"I'm working... ThreadID:{threading.get_ident()}")


schedule.every(1).seconds.do(job)
schedule.every(10).minutes.do(job)
schedule.every().hour.do(job)
schedule.every().day.at("10:30").do(job)
schedule.every(5).to(10).minutes.do(job)
schedule.every().monday.do(job)
schedule.every().wednesday.at("13:15").do(job)
# schedule.every().day.at("12:42", "Europe/Amsterdam").do(job)
schedule.every().minute.at(":17").do(job)


def job_with_argument(name):
    print(f"I am {name} ThreadID:{threading.get_ident()}")


schedule.every(5).seconds.do(job_with_argument, name="Peter")

while True:
    schedule.run_pending()
    time.sleep(1)

```



```py
import schedule  
import time  
  
def job():  
    print("I'm working...")  
  
schedule.every(10).minutes.do(job)  
schedule.every().hour.do(job)  
schedule.every().day.at("10:30").do(job)  
schedule.every().monday.do(job)  
schedule.every().wednesday.at("13:15").do(job)  
  
while True:  
    schedule.run_pending()  
    time.sleep(1)  
```



```
每隔10分鐘執行一次任務
每隔一小時執行一次任務
每天10:30執行一次任務
每週一的這個時候執行一次任務
每週三13:15執行一次任務
```



```py
class Scheduler(object):  
    """  
    Objects instantiated by the :class:`Scheduler ` are  
    factories to create jobs, keep record of scheduled jobs and  
    handle their execution.  
    """  
    def __init__(self):  
        self.jobs = []  
  
    def run_pending(self):  
        runnable_jobs = (job for job in self.jobs if job.should_run)  
        for job in sorted(runnable_jobs):  
            self._run_job(job)  
  
    def run_all(self, delay_seconds=0):  
        logger.info('Running *all* %i jobs with %is delay inbetween',  
                    len(self.jobs), delay_seconds)  
        for job in self.jobs[:]:  
            self._run_job(job)  
            time.sleep(delay_seconds)  
  
    def clear(self, tag=None):  
        if tag is None:  
            del self.jobs[:]  
        else:  
            self.jobs[:] = (job for job in self.jobs if tag not in job.tags)  
  
    def cancel_job(self, job):  
        try:  
            self.jobs.remove(job)  
        except ValueError:  
            pass  
  
    def every(self, interval=1):  
        job = Job(interval, self)  
        return job  
  
    def _run_job(self, job):  
        ret = job.run()  
        if isinstance(ret, CancelJob) or ret is CancelJob:  
            self.cancel_job(job)  
  
    @property  
    def next_run(self):  
        if not self.jobs:  
            return None  
        return min(self.jobs).next_run  
  
    @property  
    def idle_seconds(self):  
        return (self.next_run - datetime.datetime.now()).total_seconds()  

```

**Scheduler** 作用就是在 job 可以執行的時候執行它. 這裡的函數也都比較簡單: 

> *** run_pending:** 運行所有可以運行的任務
> *** run_all:** 運行所有任務,不管是否應該運行
> *** clear:** 刪除所有調度的任務
> *** cancel_job:** 刪除一個任務
> *** every:** 創建一個調度任務, 返回的是一個 **Job** 物件
> *** _run_job:** 運行一個 **Job** 物件
> *** next_run:** 獲取下一個要運行任務的時間, 這裡使用的是 min 去得到最近將執行的 job, 之所以這樣使用，是 **Job** 重載了[__lt__](https://docs.python.org/3/reference/datamodel.html#object.__lt__) 方法,這樣寫起來確實很簡潔.
> *** idle_seconds:** 還有多少秒即將開始運行任務.


**Class Job** 
**Job** 是整個定時任務的核心. 主要功能就是根據創建 **Job** 時的參數, 得到下一次運行的時間. 代碼如下,稍微有點長 (會省略部分代碼，可以看 [源碼](https://github.com/dbader/schedule/blob/master/schedule/__init__.py)). 這個類別提供的ˊ方法也不是很多, 有很多邏輯是一樣的. 簡單介紹一下建構子的參數: 

> *** interval:** 間隔多久,每 interval 秒或分等.
> *** job_func:** job 執行函數
> *** unit :** 間隔單元，比如 minutes, hours
> *** at_time:** job 具體執行時間點,比如 10:30等
> *** last_run:** job上一次執行時間
> *** next_run:** job下一次即將運行時間
> *** period:** 距離下次運行間隔時間
> *** start_day:** 週的特殊天，也就是 monday 等的含義


再來看一下幾個重要的方法: 
*** __lt__:** 

> 被使用在比較哪個 job 最先即將執行, **Scheduler** 中 next_run 方法裡使用 [min](https://docs.python.org/3/library/functions.html#min) 會用到, 有時合適的使用 python 這些特殊方法可以簡化代碼，看起來更 pythonic.


*** second、seconds:** 

> second、seconds 的區別就是 second 時默認 interval ==1, 即 schedule.every().second 和 schedule.every(1).seconds 是等價的,作用就是設置 *unit* 為 seconds. minute 和 minutes、hour 和hours 、day 和 days、week 和 weeks 也類似.


*** monday:** 

> **設置 \*start_day\* 為 monday, unit 為 weeks, interval 為1 .** 含義就是每週一執行 job. 類似 tuesday、wednesday、thursday、friday、saturday、sunday 一樣.


*** at:** 

> 表示 **某天的某個時間點**，所以不適合 minutes、weeks 且 start_day 為空 (即單純的周) 這些 unit. 對於 unit 為 hours 時, *time_str* 中小時部分為 0.


*** do:** 

> 設置 job 對應的函數以及參數, 這裡使用 [**functools**.update_wrapper](https://docs.python.org/3/library/functools.html#functools.update_wrapper) 去更新函數名等信息.主要是 [**functools**.partial](https://docs.python.org/3/library/functools.html#functools.partial) 返回的函數和原函數名稱不一樣.具體可以看看官網文檔. 然後調用 _schedule_next_run 去計算 job 下一次執行時間.


*** should_run:** 

> 判斷 job 是否可以運行了.依據是當前時間點大於等於 job 的 *next_run*


*** _schedule_next_run:** 

> 這是整個 job 的定時的邏輯部分是計算 job 下次運行的時間點的. 這邊描述一下流程, 首先是計算下一次執行時間:
>
> [view plain](http://localhost/jforum/posts/list/4399.page#)[copy to clipboard](http://localhost/jforum/posts/list/4399.page#)[print](http://localhost/jforum/posts/list/4399.page#)[?](http://localhost/jforum/posts/list/4399.page#)
>
> 1. self.period = datetime.timedelta(**{self.unit: interval}) 
> 2. self.next_run = datetime.datetime.now() + self.period 
>
> 這裡根據 
>
> unit
>
>  和 
>
> interval
>
>  計算出下一次運行時間. 舉個例子,比如 
>
> schedule.every().hour.do(job, message='things')
>
>  下一次運行時間就是當前時間加上一小時的間隔. 但是當 
>
> start_day
>
>  不為空時，即表示某個星期. 這時 
>
> period
>
>  就不能直接加在當前時間了. 看代碼:
>
> [view plain](http://localhost/jforum/posts/list/4399.page#)[copy to clipboard](http://localhost/jforum/posts/list/4399.page#)[print](http://localhost/jforum/posts/list/4399.page#)[?](http://localhost/jforum/posts/list/4399.page#)
>
> 1. weekday = weekdays.index(self.start_day) 
> 2. days_ahead = weekday - self.next_run.weekday() 
> 3. **if** days_ahead <= 0: # Target day already happened **this** week 
> 4.   days_ahead += 7 
> 5. self.next_run += datetime.timedelta(days_ahead) - self.period 
>
> 其中 
>
> days_ahead
>
>  表示 job 表示的星期幾與當表示的星期幾差幾天. 比如今天是 星期三，job 表示的是 星期五,那麼 
>
> days_ahead
>
>  就為2，最終 
>
> self.next_run
>
>  效果就是在 now 基礎上加了2天.
>
> 接著當 
>
> at_time
>
>  不為空時, 需要更新執行的時間點,具體就是計算時、分、秒然後調用 replace 進行更新.


**Real User Cases** 
這邊介紹實際使用範例. 

**在 \*N\* 小時/分鐘 後執行並只一次** 
這個範例很像 Linux 命令 [**at**](https://linux.die.net/man/1/at) 的功能, 簡單來說就是延遲一段時間後再執行某個 job. 這邊我們會繼承 **Job** 並客製成我們需要的功能 **MyJob** 類別: 
**- test_run_after.py** 

```py
#!/usr/bin/env python3  
import schedule  
import logging  
import functools  
import os  
import re  
import time  
from schedule import Job, CancelJob, IntervalError  
from datetime import datetime, timedelta  
  
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(os.path.basename(__file__))  
logger.setLevel(20)  
  
class MyJob(Job):  
    def __init__(self, scheduler=None):  
        super(MyJob, self).__init__(1, scheduler)  
        self.regex = re.compile(r'((?P\d+?)hr)?((?P\d+?)m)?((?P\d+?)s)?')  
  
    def parse_time(self, time_str):  
        # https://stackoverflow.com/questions/4628122/how-to-construct-a-timedelta-object-from-a-simple-string  
        parts = self.regex.match(time_str)  
        if not parts:  
            raise IntervalError()  
  
        parts = parts.groupdict()  
        time_params = {}  
        for (name, param) in parts.items():  
            if param:  
                time_params[name] = int(param)  
  
        return timedelta(**time_params)  
  
    def do(self, job_func, *args, **kwargs):  
        self.job_func = functools.partial(job_func, *args, **kwargs)  
        try:  
            functools.update_wrapper(self.job_func, job_func)  
        except AttributeError:  
            # job_funcs already wrapped by functools.partial won't have  
            # __name__, __module__ or __doc__ and the update_wrapper()  
            # call will fail.  
            pass  
  
        self.scheduler.jobs.append(self)  
        return self  
  
    def after(self, atime):  
        if isinstance(atime, timedelta):  
            self.next_run = datetime.now() + atime  
        elif isinstance(atime, str):  
            times = atime.split(':')  
            if len(times) == 3:  # HH:MM:SS  
                self.next_run = datetime.now() + timedelta(hours=int(times[0]), minutes=int(times[1]), seconds=int(times[2]))  
            else:  
                self.next_run = datetime.now() + self.parse_time(atime)  
        else:  
            raise IntervalError()  
  
        return self  
  
    def run(self):  
        logger.info('Running job %s', self)  
        ret = self.job_func()  
        self.last_run = datetime.now()  
        return CancelJob()  
  
def main():  
    def work():  
        logger.info('Work done at {}'.format(datetime.now()))  
  
    myjob = MyJob(schedule.default_scheduler)  
    myjob.after('2m').do(work)  # Do work after 2 minutes  
  
    logger.info('Now is {}'.format(datetime.now()))  
    while len(schedule.default_scheduler.jobs) > 0:  
        schedule.run_pending()  
        time.sleep(1)  
  
    logger.info('All job done!')  
  
  
if __name__ == '__main__':  
    main()  
```

Execution result: 

```sh
**#** ./test_run_after.py
INFO:test_run_after.py:Now is 2019-05-23 13:57:06.289055
INFO:test_run_after.py:Running job functools.partial(.work at 0x7f7d85a43950>)
INFO:test_run_after.py:Work done at 2019-05-23 13:59:06.438432
INFO:test_run_after.py:All job done!
```



---

https://zhuanlan.zhihu.com/p/537722631

## 安裝

```text
pip install schedule
```

### 不適合 schedule 的情況

說實話，**Schedule**不是一個“一刀切”的調度庫。此庫旨在成為簡單調度問題的簡單解決方案。如果需要以下需求，您可能應該在其他地方尋找可用方案：

- 作業持久性（記住重新啟動之間的計畫）
- 精確計時（亞秒級精度執行）
- 並行執行（多個執行緒）
- 本地化（時區、工作日或節假日）

**Schedule**不考慮執行作業函數所需的時間。為了保證穩定的執行計畫，您需要將長時間運行的作業移出主執行緒（計畫程式執行的位置）。有關示例實現，請參閱[平行執行](https://link.zhihu.com/?target=https%3A//schedule.readthedocs.io/en/stable/parallel-execution.html)。

## 使用示例

**普通方法**

```python
import schedule
import time

def job():
    print("I'm working...")

schedule.every(10).minutes.do(job) # 每十分鐘
schedule.every().hour.do(job) # 每小時
schedule.every().day.at("10:30").do(job) # 每天10：30
schedule.every().monday.do(job) # 每月
schedule.every().wednesday.at("13:15").do(job) # 每週三 13：15
schedule.every().minute.at(":17").do(job) # 每分鐘的第17秒

while True:
    schedule.run_pending()
    time.sleep(1)
```

**裝飾器方法**

```python
from schedule import every, repeat, run_pending
import time

@repeat(every(10).minutes)
def job():
    print("I am a scheduled job")

while True:
    run_pending()
    time.sleep(1)
```

**向任務傳參**

```python
import schedule

def greet(name):
    print('Hello', name)

schedule.every(2).seconds.do(greet, name='Alice')
schedule.every(4).seconds.do(greet, name='Bob')

from schedule import every, repeat

@repeat(every().second, "World")
@repeat(every().day, "Mars")
def hello(planet):
    print("Hello", planet)
```

**取消任務**

```text
import schedule

def some_task():
    print('Hello world')

job = schedule.every().day.at('22:30').do(some_task)
schedule.cancel_job(job) # 取消任務
```

**只運行某任務一次**

```python
import schedule
import time

def job_that_executes_once():
    # Do some work that only needs to happen once...
    return schedule.CancelJob # 通過返回schedule.CancelJob，將其在 scheduler 中取消

schedule.every().day.at('22:30').do(job_that_executes_once)

while True:
    schedule.run_pending()
    time.sleep(1)
```

**獲取所有任務**

要從調度程序中檢索所有作業，請使用 `schedule.get_jobs()`

```python
import schedule

def hello():
    print('Hello world')

schedule.every().second.do(hello)

all_jobs = schedule.get_jobs()
```

**取消所有任務**

要從調度程序中刪除所有作業，請使用 `schedule.clear()`

```text
import schedule

def greet(name):
    print('Hello {}'.format(name))

schedule.every().second.do(greet)

schedule.clear()
```

**獲得多個工作，按標籤過濾**

您可以從調度程序中檢索一組作業，並通過唯一識別碼選擇它們。

```python
import schedule

def greet(name):
    print('Hello {}'.format(name))

schedule.every().day.do(greet, 'Andrea').tag('daily-tasks', 'friend')
schedule.every().hour.do(greet, 'John').tag('hourly-tasks', 'friend')
schedule.every().hour.do(greet, 'Monica').tag('hourly-tasks', 'customer')
schedule.every().day.do(greet, 'Derek').tag('daily-tasks', 'guest')

friends = schedule.get_jobs('friend')
```

**取消多個作業，按標籤過濾**

```python
import schedule

def greet(name):
    print('Hello {}'.format(name))

schedule.every().day.do(greet, 'Andrea').tag('daily-tasks', 'friend')
schedule.every().hour.do(greet, 'John').tag('hourly-tasks', 'friend')
schedule.every().hour.do(greet, 'Monica').tag('hourly-tasks', 'customer')
schedule.every().day.do(greet, 'Derek').tag('daily-tasks', 'guest')

schedule.clear('daily-tasks')
```

**以隨機間隔運行作業**

```python
def my_job():
    print('Foo')

# Run every 5 to 10 seconds.
schedule.every(5).to(10).seconds.do(my_job)
```

**運行作業直到特定時間**

```python
import schedule
from datetime import datetime, timedelta, time

def job():
    print('Boo')

# run job until a 18:30 today
schedule.every(1).hours.until("18:30").do(job)

# run job until a 2030-01-01 18:33 today
schedule.every(1).hours.until("2030-01-01 18:33").do(job)

# Schedule a job to run for the next 8 hours
schedule.every(1).hours.until(timedelta(hours=8)).do(job)

# Run my_job until today 11:33:42
schedule.every(1).hours.until(time(11, 33, 42)).do(job)

# run job until a specific datetime
schedule.every(1).hours.until(datetime(2020, 5, 17, 11, 36, 20)).do(job)
```

`until `方法設定作業的截止時間。 該作業將不會在截止時間之後運行。

**距離下一次執行的時間**

使用 `schedule.idle_seconds()` 獲取下一個作業計畫運行之前的秒數。 如果下一個計畫的作業計畫在過去運行，則返回值為負。 如果沒有安排作業，則返回 `None`。

```python
import schedule
import time

def job():
    print('Hello')

schedule.every(5).seconds.do(job)

while 1:
    n = schedule.idle_seconds()
    if n is None:
        # no more jobs
        break
    elif n > 0:
        # sleep exactly the right amount of time
        time.sleep(n)
    schedule.run_pending()
```

**立即運行所有作業，無論它們的日程安排如何**

要運行所有作業，無論它們是否計畫運行，請使用 `schedule.run_all()`。 完成後會重新安排作業，就像使用 `run_pending()` 執行作業一樣。

```python
import schedule

def job_1():
    print('Foo')

def job_2():
    print('Bar')

schedule.every().monday.at("12:40").do(job_1)
schedule.every().tuesday.at("16:40").do(job_2)

schedule.run_all()

# Add the delay_seconds argument to run the jobs with a number
# of seconds delay in between.
schedule.run_all(delay_seconds=10)
```

## 在背景執行

不可能在背景執行 **schedule**。 [Out of the box](https://link.zhihu.com/?target=https%3A//idioms.thefreedictionary.com/Out-of-the-Box) it is not possible to run the schedule in the background. 但是，您可以自己建立一個執行緒並使用它來運行作業而不會阻塞主執行緒。 這是您如何執行此操作的示例：

```python
import threading
import time

import schedule


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def background_job():
    print('Hello from the background thread')


schedule.every().second.do(background_job)

# Start the background thread
stop_run_continuously = run_continuously()

# Do some other things...
time.sleep(10)

# Stop the background thread
stop_run_continuously.set()
```

## 平行執行

我試圖每 10 秒執行 50 個項目，但是從我的日誌中它說它在 10 秒的計畫中連續執行每個項目，有解決方法嗎？

默認情況下，**schedule**順序執行所有作業。 這背後的原因是，很難找到一個讓每個人都滿意的平行執行模型。

您可以通過在其自己的執行緒中運行每個作業來解決此限制：

```python
import threading
import time
import schedule

def job():
    print("I'm running on thread %s" % threading.current_thread())

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every(10).seconds.do(run_threaded, job)
schedule.every(10).seconds.do(run_threaded, job)
schedule.every(10).seconds.do(run_threaded, job)
schedule.every(10).seconds.do(run_threaded, job)
schedule.every(10).seconds.do(run_threaded, job)


while 1:
    schedule.run_pending()
    time.sleep(1)
```

如果您想更嚴格地控制執行緒數，請使用共享作業佇列和一個或多個工作執行緒：

```python
import time
import threading
import schedule
import queue

def job():
    print("I'm working")


def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()

jobqueue = queue.Queue()

schedule.every(10).seconds.do(jobqueue.put, job)
schedule.every(10).seconds.do(jobqueue.put, job)
schedule.every(10).seconds.do(jobqueue.put, job)
schedule.every(10).seconds.do(jobqueue.put, job)
schedule.every(10).seconds.do(jobqueue.put, job)

worker_thread = threading.Thread(target=worker_main)
worker_thread.start()

while 1:
    schedule.run_pending()
    time.sleep(1)
```

該模型對於分佈式應用程式也很有意義，其中工作人員是從分佈式工作佇列接收作業的獨立處理程序。 我喜歡將 beanstalkd 與 beanstalkc Python 庫一起使用。

## 異常處理

**Schedule\**\**不會**捕獲作業執行期間發生的異常。 因此，**在作業執行期間拋出的任何異常都會冒泡並中斷 schedule 的 run_xyz 函數**。

如果你想防止異常，你可以**將你的工作函數包裝在一個裝飾器**中，如下所示：

```python
import functools

def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator

@catch_exceptions(cancel_on_failure=True)
def bad_task():
    return 1 / 0

schedule.every(5).minutes.do(bad_task)
```

## 日誌（Logging）

Schedule 將消息記錄到名為 schedule 在 DEBUG 等級的 Python 記錄器。 要從 Schedule 接收日誌，請將日誌（logging）記錄等級設定為 DEBUG。

```python
import schedule
import logging

logging.basicConfig()
schedule_logger = logging.getLogger('schedule')
schedule_logger.setLevel(level=logging.DEBUG)

def job():
    print("Hello, Logs")

schedule.every().second.do(job)

schedule.run_all()

schedule.clear()
```

這將生成以下日誌消息：

```text
DEBUG:schedule:Running *all* 1 jobs with 0s delay in between
DEBUG:schedule:Running job Job(interval=1, unit=seconds, do=job, args=(), kwargs={})
Hello, Logs
DEBUG:schedule:Deleting *all* jobs
```

### 自訂日誌記錄

向作業新增**可重用**日誌的最簡單方法是實現一個處理日誌的裝飾器。 例如，下面的程式碼新增了 print_elapsed_time 裝飾器：

```python
import functools
import time
import schedule

# This decorator can be applied to any job function to log the elapsed time of each job
def print_elapsed_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_timestamp = time.time()
        print('LOG: Running job "%s"' % func.__name__)
        result = func(*args, **kwargs)
        print('LOG: Job "%s" completed in %d seconds' % (func.__name__, time.time() - start_timestamp))
        return result

    return wrapper


@print_elapsed_time
def job():
    print('Hello, Logs')
    time.sleep(5)

schedule.every().second.do(job)

schedule.run_all()
```

輸出：

```text
LOG: Running job "job"
Hello, Logs
LOG: Job "job" completed in 5 seconds
```

## 多個調度器

您可以根據需要從單個調度程式執行任意數量的作業。 但是，對於較大的安裝，可能需要多個調度程序。 這是支援的

```python
import time
import schedule

def fooJob():
    print("Foo")

def barJob():
    print("Bar")

# Create a new scheduler
scheduler1 = schedule.Scheduler()

# Add jobs to the created scheduler
scheduler1.every().hour.do(fooJob)
scheduler1.every().hour.do(barJob)

# Create as many schedulers as you need
scheduler2 = schedule.Scheduler()
scheduler2.every().second.do(fooJob)
scheduler2.every().second.do(barJob)

while True:
    # run_pending needs to be called on every scheduler
    scheduler1.run_pending()
    scheduler2.run_pending()
    time.sleep(1)
```
