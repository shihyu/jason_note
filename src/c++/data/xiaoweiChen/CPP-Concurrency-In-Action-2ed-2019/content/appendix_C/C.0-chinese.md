# 消息傳遞框架與完整的ATM示例

ATM：自動取款機。

回到第4章，我舉了一個使用消息傳遞框架在線程間發送信息的例子。這裡就會使用這個實現來完成ATM功能。下面完整代碼就是功能的實現，包括消息傳遞框架。

代碼C.1實現了一個消息隊列，可以將消息以指針(指向基類)的方式存儲在列表中，指定消息類型會由基類派生模板進行處理。推送包裝類的構造實例，以及存儲指向這個實例的指針，彈出實例的時候，將會返回指向其的指針。因為message_base類沒有任何成員函數，在訪問存儲消息之前，彈出線程就需要將指針轉為`wrapped_message<T>`指針。

代碼C.1 簡單的消息隊列

```c++
#include <mutex>
#include <condition_variable>
#include <queue>
#include <memory>

namespace messaging
{
  struct message_base  // 隊列項的基礎類
  {
    virtual ~message_base()
    {}
  };

  template<typename Msg>
  struct wrapped_message:  // 每個消息類型都需要特化
    message_base
  {
    Msg contents;

    explicit wrapped_message(Msg const& contents_):
      contents(contents_)
    {}
  };

  class queue  // 我們的隊列
  {
    std::mutex m;
    std::condition_variable c;
    std::queue<std::shared_ptr<message_base> > q;  // 實際存儲指向message_base類指針的隊列
  public:
    template<typename T>
    void push(T const& msg)
    {
      std::lock_guard<std::mutex> lk(m);
      q.push(std::make_shared<wrapped_message<T> >(msg));  // 包裝已傳遞的信息，存儲指針
      c.notify_all();
    }

    std::shared_ptr<message_base> wait_and_pop()
    {
      std::unique_lock<std::mutex> lk(m);
      c.wait(lk,[&]{return !q.empty();});  // 當隊列為空時阻塞
      auto res=q.front();
      q.pop();
      return res;
    }
  };
}
```

發送通過sender類(見代碼C.2)實例處理過的消息。只能對已推送到隊列中的消息進行包裝。對sender實例的拷貝，只是拷貝了指向隊列的指針，而非隊列本身。

代碼C.2 sender類

```c++
namespace messaging
{
  class sender
  {
    queue*q;  // sender是一個隊列指針的包裝類
  public:
    sender():  // sender無隊列(默認構造函數)
      q(nullptr)
    {}

    explicit sender(queue*q_):  // 從指向隊列的指針進行構造
      q(q_)
    {}

    template<typename Message>
    void send(Message const& msg)
    {
      if(q)
      {
        q->push(msg);  // 將發送信息推送給隊列
      }
    }
  };
}
```

接收信息部分有些麻煩。不僅要等待隊列中的消息，還要檢查消息類型是否與所等待的消息類型匹配，並調用處理函數進行處理。那麼就從receiver類的實現開始吧。

代碼C.3 receiver類

```c++
namespace messaging
{
  class receiver
  {
    queue q;  // 接受者擁有對應隊列
  public:
    operator sender()  // 允許將類中隊列隱式轉化為一個sender隊列
    {
      return sender(&q);
    }
    dispatcher wait()  // 等待對隊列進行調度
    {
      return dispatcher(&q);
    }
  };
}
```

sender只是引用一個消息隊列，而receiver是擁有一個隊列。可以使用隱式轉換的方式獲取sender引用的類。難點在於wait()中的調度，這裡創建了一個dispatcher對象引用receiver中的隊列，dispatcher類實現會在下一個清單中看到。如你所見，任務是在析構函數中完成的。在這個例子中，所要做的工作是對消息進行等待，以及對其進行調度。

代碼C.4 dispatcher類

```c++
namespace messaging
{
  class close_queue  // 用於關閉隊列的消息
  {};
  
  class dispatcher
  {
    queue* q;
    bool chained;

    dispatcher(dispatcher const&)=delete;  // dispatcher實例不能被拷貝
    dispatcher& operator=(dispatcher const&)=delete;
 
    template<
      typename Dispatcher,
      typename Msg,
      typename Func>  // 允許TemplateDispatcher實例訪問內部成員
    friend class TemplateDispatcher;

    void wait_and_dispatch()
    {
      for(;;)  // 1 循環，等待調度消息
      {
        auto msg=q->wait_and_pop();
        dispatch(msg);
      }
    }

    bool dispatch(  // 2 dispatch()會檢查close_queue消息，然後拋出
      std::shared_ptr<message_base> const& msg)
    {
      if(dynamic_cast<wrapped_message<close_queue>*>(msg.get()))
      {
        throw close_queue();
      }
      return false;
    }
  public:
    dispatcher(dispatcher&& other):  // dispatcher實例可以移動
      q(other.q),chained(other.chained)
    {
      other.chained=true;  // 源不能等待消息
    }

    explicit dispatcher(queue* q_):
      q(q_),chained(false)
    {}

    template<typename Message,typename Func>
    TemplateDispatcher<dispatcher,Message,Func>
    handle(Func&& f)  // 3 使用TemplateDispatcher處理指定類型的消息
    {
      return TemplateDispatcher<dispatcher,Message,Func>(
        q,this,std::forward<Func>(f));
    }

    ~dispatcher() noexcept(false)  // 4 析構函數可能會拋出異常
    {  
      if(!chained)
      {
        wait_and_dispatch();
      }
    }
  };
}
```

從wait()返回的dispatcher實例將馬上被銷燬，因為是臨時變量，也如前文提到的，析構函數在這裡做真正的工作。析構函數調用wait_and_dispatch()函數，這個函數中有一個循環①，等待消息的傳入(這樣才能進行彈出操作)，然後將消息傳遞給dispatch()函數。dispatch()函數本身②很簡單，會檢查小時是否是一個close_queue消息，當是close_queue消息時拋出一個異常。如果不是，函數將會返回false來表明消息沒有被處理。因為會拋出close_queue異常，所以析構函數會標示為`noexcept(false)`。在沒有任何標識的情況下，析構函數都為`noexcept(true)`④型，這表示沒有任何異常拋出，並且close_queue異常將會使程序終止。

雖然不會經常的去調用wait()函數，但在大多數時間裡，都希望對一條消息進行處理。這時就需要handle()成員函數③的加入。這個函數是一個模板，並且消息類型不可推斷，所以需要指定需要處理的消息類型，並且傳入函數(或可調用對象)進行處理，並將隊列傳入當前dispatcher對象的handle()函數。在測試析構函數中的chained值前要等待消息，不僅是避免“移動”類型的對象對消息進行等待，而且允許將等待狀態轉移到新的TemplateDispatcher實例中。

代碼C.5 TemplateDispatcher類模板

```c++
namespace messaging
{
  template<typename PreviousDispatcher,typename Msg,typename Func>
  class TemplateDispatcher
  {
    queue* q;
    PreviousDispatcher* prev;
    Func f;
    bool chained;

    TemplateDispatcher(TemplateDispatcher const&)=delete;
    TemplateDispatcher& operator=(TemplateDispatcher const&)=delete;
    
    template<typename Dispatcher,typename OtherMsg,typename OtherFunc>
    friend class TemplateDispatcher;  // 所有特化的TemplateDispatcher類型實例都是友元類

    void wait_and_dispatch()
    {
      for(;;)
      {
        auto msg=q->wait_and_pop();
        if(dispatch(msg))  // 1 如果消息處理過後，會跳出循環
          break;
      }
    }

    bool dispatch(std::shared_ptr<message_base> const& msg)
    {
      if(wrapped_message<Msg>* wrapper=
         dynamic_cast<wrapped_message<Msg>*>(msg.get()))  // 2 檢查消息類型，並且調用函數
      {
        f(wrapper->contents);
        return true;
      }
      else
      {
        return prev->dispatch(msg);  // 3 鏈接到之前的調度器上
      }
    }
  public:
    TemplateDispatcher(TemplateDispatcher&& other):
        q(other.q),prev(other.prev),f(std::move(other.f)),
        chained(other.chained)
    {
      other.chained=true;
    }
    TemplateDispatcher(queue* q_,PreviousDispatcher* prev_,Func&& f_):
        q(q_),prev(prev_),f(std::forward<Func>(f_)),chained(false)
    {
      prev_->chained=true;
    }

    template<typename OtherMsg,typename OtherFunc>
    TemplateDispatcher<TemplateDispatcher,OtherMsg,OtherFunc>
    handle(OtherFunc&& of)  // 4 可以鏈接其他處理器
    {
      return TemplateDispatcher<
          TemplateDispatcher,OtherMsg,OtherFunc>(
          q,this,std::forward<OtherFunc>(of));
    }

    ~TemplateDispatcher() noexcept(false)  // 5 這個析構函數也是noexcept(false)的
    {
      if(!chained)
      {
        wait_and_dispatch();
      }
    }
  };
}
```

`TemplateDispatcher<>`類模板仿照了dispatcher類，二者幾乎相同。特別是析構函數上，都是調用wait_and_dispatch()來等待處理消息。

處理消息的過程中，如果不拋出異常，就需要檢查一下在循環中①消息是否已經得到了處理。當成功的處理了一條消息，處理過程就可以停止了，這樣就可以等待下一組消息的傳入了。當獲取了一個和指定類型匹配的消息，使用函數調用的方式②就要好於拋出異常(處理函數也可能會拋出異常)。如果消息類型不匹配，就可以鏈接前一個調度器③。在第一個實例中，dispatcher實例確實作為一個調度器，當在handle()④函數中進行鏈接後，就允許處理多種類型的消息。在鏈接了之前的`TemplateDispatcher<>`實例後，當消息類型和當前的調度器類型不匹配的時候，調度鏈會依次的向前尋找類型匹配的調度器。因為任何調度器都可能拋出異常(包括dispatcher中對close_queue消息進行處理的默認處理器)，析構函數在這裡會再次被聲明為`noexcept(false)`⑤。

這種簡單的架構允許你想隊列推送任何類型的消息，並且調度器有選擇的與接收端的消息進行匹配。同樣，也允許為了推送消息，將消息隊列的引用進行傳遞的同時，保持接收端的私有性。

為了完成第4章的例子，消息的組成將在清單C.6中給出，各種狀態機將在代碼C.7,C.8和C.9中給出。最後，驅動代碼將在C.10給出。

代碼C.6 ATM消息

```c++
struct withdraw
{
  std::string account;
  unsigned amount;
  mutable messaging::sender atm_queue;
  
  withdraw(std::string const& account_,
           unsigned amount_,
           messaging::sender atm_queue_):
    account(account_),amount(amount_),
    atm_queue(atm_queue_)
  {}
};

struct withdraw_ok
{};

struct withdraw_denied
{};

struct cancel_withdrawal
{
  std::string account;
  unsigned amount;
  cancel_withdrawal(std::string const& account_,
                    unsigned amount_):
    account(account_),amount(amount_)
  {}
};

struct withdrawal_processed
{
  std::string account;
  unsigned amount;
  withdrawal_processed(std::string const& account_,
                       unsigned amount_):
    account(account_),amount(amount_)
  {}
};

struct card_inserted
{
  std::string account;
  explicit card_inserted(std::string const& account_):
    account(account_)
  {}
};

struct digit_pressed
{
  char digit;
  explicit digit_pressed(char digit_):
    digit(digit_)
  {}
};

struct clear_last_pressed
{};

struct eject_card
{};

struct withdraw_pressed
{
  unsigned amount;
  explicit withdraw_pressed(unsigned amount_):
    amount(amount_)
  {}
};

struct cancel_pressed
{};

struct issue_money
{
  unsigned amount;
  issue_money(unsigned amount_):
    amount(amount_)
  {}
};

struct verify_pin
{
  std::string account;
  std::string pin;
  mutable messaging::sender atm_queue;
  
  verify_pin(std::string const& account_,std::string const& pin_,
             messaging::sender atm_queue_):
    account(account_),pin(pin_),atm_queue(atm_queue_)
  {}
};

struct pin_verified
{};

struct pin_incorrect
{};

struct display_enter_pin
{};

struct display_enter_card
{};

struct display_insufficient_funds
{};

struct display_withdrawal_cancelled
{};

struct display_pin_incorrect_message
{};

struct display_withdrawal_options
{};

struct get_balance
{
  std::string account;
  mutable messaging::sender atm_queue;

  get_balance(std::string const& account_,messaging::sender atm_queue_):
    account(account_),atm_queue(atm_queue_)
  {} 
};

struct balance
{
  unsigned amount;
  explicit balance(unsigned amount_):
    amount(amount_)
  {}
};

struct display_balance
{
  unsigned amount;
  explicit display_balance(unsigned amount_):
    amount(amount_)
  {}
};

struct balance_pressed
{};
```

代碼C.7 ATM狀態機

```c++
class atm
{
  messaging::receiver incoming;
  messaging::sender bank;
  messaging::sender interface_hardware;

  void (atm::*state)();
  
  std::string account;
  unsigned withdrawal_amount;
  std::string pin;

  void process_withdrawal() 
  {
    incoming.wait()
      .handle<withdraw_ok>(
       [&](withdraw_ok const& msg)
       {
         interface_hardware.send(
           issue_money(withdrawal_amount));
         
         bank.send(
           withdrawal_processed(account,withdrawal_amount));

         state=&atm::done_processing;
       })
      .handle<withdraw_denied>(
       [&](withdraw_denied const& msg)
       {
         interface_hardware.send(display_insufficient_funds());

         state=&atm::done_processing;
       })
      .handle<cancel_pressed>(
       [&](cancel_pressed const& msg)
       {
         bank.send(
           cancel_withdrawal(account,withdrawal_amount));

         interface_hardware.send(
           display_withdrawal_cancelled());

         state=&atm::done_processing;
       });
   }

  void process_balance()
  {
    incoming.wait()
      .handle<balance>(
       [&](balance const& msg)
       {
         interface_hardware.send(display_balance(msg.amount));
         
         state=&atm::wait_for_action;
       })
      .handle<cancel_pressed>(
       [&](cancel_pressed const& msg)
       {
         state=&atm::done_processing;
       });
  }

  void wait_for_action()
  {
    interface_hardware.send(display_withdrawal_options());

    incoming.wait()
      .handle<withdraw_pressed>(
       [&](withdraw_pressed const& msg)
       {
         withdrawal_amount=msg.amount;
         bank.send(withdraw(account,msg.amount,incoming));
         state=&atm::process_withdrawal;
       })
      .handle<balance_pressed>(
       [&](balance_pressed const& msg)
       {
         bank.send(get_balance(account,incoming));
         state=&atm::process_balance;
       })
      .handle<cancel_pressed>(
       [&](cancel_pressed const& msg)
       {
         state=&atm::done_processing;
       });
  }

  void verifying_pin()
  {
    incoming.wait()
      .handle<pin_verified>(
       [&](pin_verified const& msg)
       {
         state=&atm::wait_for_action;
       })
      .handle<pin_incorrect>(
       [&](pin_incorrect const& msg)
       {
         interface_hardware.send(
         display_pin_incorrect_message());
         state=&atm::done_processing;
       })
      .handle<cancel_pressed>(
       [&](cancel_pressed const& msg)
       {
         state=&atm::done_processing;
       });
  }

  void getting_pin()
  {
    incoming.wait()
      .handle<digit_pressed>(
       [&](digit_pressed const& msg)
       {
         unsigned const pin_length=4;
         pin+=msg.digit;

         if(pin.length()==pin_length)
         {
           bank.send(verify_pin(account,pin,incoming));
           state=&atm::verifying_pin;
         }
       })
      .handle<clear_last_pressed>(
       [&](clear_last_pressed const& msg)
       {
         if(!pin.empty())
         {
           pin.pop_back();
         }
       })
      .handle<cancel_pressed>(
       [&](cancel_pressed const& msg)
       {
         state=&atm::done_processing;
       });
  }

  void waiting_for_card()
  {
    interface_hardware.send(display_enter_card());
    
    incoming.wait()
      .handle<card_inserted>(
       [&](card_inserted const& msg)
       {
         account=msg.account;
         pin="";
         interface_hardware.send(display_enter_pin());
         state=&atm::getting_pin;
       });
  }

  void done_processing()
  {
    interface_hardware.send(eject_card());
    state=&atm::waiting_for_card;
  }

  atm(atm const&)=delete;
  atm& operator=(atm const&)=delete;
public:
  atm(messaging::sender bank_,
  messaging::sender interface_hardware_):
  bank(bank_),interface_hardware(interface_hardware_)
  {}

  void done()
  {
    get_sender().send(messaging::close_queue());
  }

  void run()
  {
    state=&atm::waiting_for_card;
    try
    {
      for(;;)
      {
        (this->*state)();
      }
    }
    catch(messaging::close_queue const&)
    {
    }
  }

  messaging::sender get_sender()
  {
    return incoming;
  } 
};
```

代碼C.8 銀行狀態機

```c++
class bank_machine
{
  messaging::receiver incoming;
  unsigned balance;
public:
  bank_machine():

  balance(199)
  {}

  void done()
  {
    get_sender().send(messaging::close_queue());
  }

  void run()
  {
    try
    {
      for(;;)
      {
        incoming.wait()
          .handle<verify_pin>(
           [&](verify_pin const& msg)
           {
             if(msg.pin=="1937")
             {
               msg.atm_queue.send(pin_verified());
             }
             else
             {
               msg.atm_queue.send(pin_incorrect());
             }
           })
          .handle<withdraw>(
           [&](withdraw const& msg)
           {
             if(balance>=msg.amount)
             {
               msg.atm_queue.send(withdraw_ok());
               balance-=msg.amount;
             }
             else
             {
               msg.atm_queue.send(withdraw_denied());
             }
           })
          .handle<get_balance>(
           [&](get_balance const& msg)
           {
             msg.atm_queue.send(::balance(balance));
           })
          .handle<withdrawal_processed>(
           [&](withdrawal_processed const& msg)
           {
           })
          .handle<cancel_withdrawal>(
           [&](cancel_withdrawal const& msg)
           {
           });
      }
    }
    catch(messaging::close_queue const&)
    {
    }
  }

  messaging::sender get_sender()
  {
  return incoming;
  }
};
```

代碼C.9 用戶狀態機

```c++
class interface_machine
{
  messaging::receiver incoming;
public:
  void done()
  {
    get_sender().send(messaging::close_queue());
  }

  void run()
  {
    try
    {
      for(;;)
      {
        incoming.wait()
          .handle<issue_money>(
           [&](issue_money const& msg)
           {
             {
               std::lock_guard<std::mutex> lk(iom);
               std::cout<<"Issuing "
                 <<msg.amount<<std::endl;
             }
           })
          .handle<display_insufficient_funds>(
           [&](display_insufficient_funds const& msg)
           {
             {
               std::lock_guard<std::mutex> lk(iom);
               std::cout<<"Insufficient funds"<<std::endl;
             }
           })
          .handle<display_enter_pin>(
           [&](display_enter_pin const& msg)
           {
             {
               std::lock_guard<std::mutex> lk(iom);
               std::cout<<"Please enter your PIN (0-9)"<<std::endl;
             }
           })
          .handle<display_enter_card>(
           [&](display_enter_card const& msg)
           {
             {
               std::lock_guard<std::mutex> lk(iom);
               std::cout<<"Please enter your card (I)"
                 <<std::endl;
             }
           })
          .handle<display_balance>(
           [&](display_balance const& msg)
           {
             {
               std::lock_guard<std::mutex> lk(iom);
               std::cout
                 <<"The balance of your account is "
                 <<msg.amount<<std::endl;
             }
           })
          .handle<display_withdrawal_options>(
           [&](display_withdrawal_options const& msg)
           {
             {
               std::lock_guard<std::mutex> lk(iom);
               std::cout<<"Withdraw 50? (w)"<<std::endl;
               std::cout<<"Display Balance? (b)"
                 <<std::endl;
               std::cout<<"Cancel? (c)"<<std::endl;
             }
           })
          .handle<display_withdrawal_cancelled>(
           [&](display_withdrawal_cancelled const& msg)
           {
             {
               std::lock_guard<std::mutex> lk(iom);
               std::cout<<"Withdrawal cancelled"
                 <<std::endl;
             }
           })
          .handle<display_pin_incorrect_message>(
           [&](display_pin_incorrect_message const& msg)
           {
             {
               std::lock_guard<std::mutex> lk(iom);
               std::cout<<"PIN incorrect"<<std::endl;
             }
           })
          .handle<eject_card>(
           [&](eject_card const& msg)
           {
             {
               std::lock_guard<std::mutex> lk(iom);
               std::cout<<"Ejecting card"<<std::endl;
             }
           });
      }
    }
    catch(messaging::close_queue&)
    {
    }
  }

  messaging::sender get_sender()
  {
    return incoming;
  }
};
```

代碼C.10 驅動代碼

```c++
int main()
{
  bank_machine bank;
  interface_machine interface_hardware;

  atm machine(bank.get_sender(),interface_hardware.get_sender());

  std::thread bank_thread(&bank_machine::run,&bank);
  std::thread if_thread(&interface_machine::run,&interface_hardware);
  std::thread atm_thread(&atm::run,&machine);

  messaging::sender atmqueue(machine.get_sender());

  bool quit_pressed=false;

  while(!quit_pressed)
  {
    char c=getchar();
    switch(c)
    {
    case '0':
    case '1':
    case '2':
    case '3':
    case '4':
    case '5':
    case '6':
    case '7':
    case '8':
    case '9':
      atmqueue.send(digit_pressed(c));
      break;
    case 'b':
      atmqueue.send(balance_pressed());
      break;
    case 'w':
      atmqueue.send(withdraw_pressed(50));
      break;
    case 'c':
      atmqueue.send(cancel_pressed());
      break;
    case 'q':
      quit_pressed=true;
      break;
    case 'i':
      atmqueue.send(card_inserted("acc1234"));
      break;
    }
  }

  bank.done();
  machine.done();
  interface_hardware.done();

  atm_thread.join();
  bank_thread.join();
  if_thread.join();
}
```