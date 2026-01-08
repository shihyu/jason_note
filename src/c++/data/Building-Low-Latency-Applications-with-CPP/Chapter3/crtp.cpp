#include <cstdio>

// ❌ 傳統虛擬函式：執行期多型
// 成本：查詢 vtable（記憶體存取）+ 間接跳躍（無法內聯）= 5-10 ns
class RuntimeExample
{
public:
    virtual void placeOrder()
    {
        printf("RuntimeExample::placeOrder()\n");
    }
};

class SpecificRuntimeExample : public RuntimeExample
{
public:
    void placeOrder() override
    {
        printf("SpecificRuntimeExample::placeOrder()\n");
    }
};

// ✅ CRTP（Curiously Recurring Template Pattern）：編譯期多型
// ⚡ 效能關鍵：完全內聯，零執行期開銷（與直接呼叫相同）
template<typename actual_type>
class CRTPExample
{
public:
    void placeOrder()
    {
        // 編譯期決定呼叫哪個函式（static_cast）
        static_cast<actual_type*>(this)->actualPlaceOrder();
    }

    void actualPlaceOrder()
    {
        printf("CRTPExample::actualPlaceOrder()\n");
    }
};

// 繼承時將自己作為模板參數（CRTP 特徵）
class SpecificCRTPExample : public CRTPExample<SpecificCRTPExample>
{
public:
    void actualPlaceOrder()
    {
        printf("SpecificCRTPExample::actualPlaceOrder()\n");
    }
};

int main(int, char**)
{
    RuntimeExample* runtime_example = new SpecificRuntimeExample();
    runtime_example->placeOrder();

    CRTPExample <SpecificCRTPExample> crtp_example;
    crtp_example.placeOrder();

    return 0;
}
