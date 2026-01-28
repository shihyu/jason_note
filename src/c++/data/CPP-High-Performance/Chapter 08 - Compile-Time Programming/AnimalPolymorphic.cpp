// 高效能關鍵技術示例
// 章節：Compile-Time Programming - 檔案：AnimalPolymorphic.cpp

#include <iostream>

struct AnimalBase {
    virtual ~AnimalBase() { }
    virtual void speak() const { }
};

struct Bear : public AnimalBase {
    virtual void speak() const override { roar(); }
    void roar() const { std::cout << "rarrrr!\n"; }
};

struct Dog : public AnimalBase {
    virtual void speak() const override { woof(); }
    void woof() const { std::cout << "woof woof!\n"; }
};

void speak(const AnimalBase &a) {
    // 關鍵技術：編譯期計算與型別約束。
    a.speak();
}

int main()
{
    Bear bear;
    speak(bear);
    
    Dog dog;
    speak(dog);
    
    return 0;
}
