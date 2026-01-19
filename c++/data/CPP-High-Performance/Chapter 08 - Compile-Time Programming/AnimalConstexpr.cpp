// 高效能關鍵技術示例
// 章節：Compile-Time Programming - 檔案：AnimalConstexpr.cpp

#include <iostream>
#include <type_traits>

struct Bear {
    void roar() const { std::cout << "roar!\n";}
};

struct Dog {
    void bark() const { std::cout << "woof!\n"; }
};

// _"the compiler will keep the call to the member function, quack(), ...
// ...hich will then fail to compile since Bear does not contain a quack() member function"_
template <typename Animal> void speak(const Animal &a) {
    // if (std::is_same_v<Animal, Bear>) {
    // 關鍵技術：編譯期計算降低執行期成本。
    if constexpr (std::is_same_v<Animal, Bear>) {
        a.roar();
    // } else if (std::is_same_v<Animal, Dog>){
    } else if constexpr (std::is_same_v<Animal, Dog>){
        a.bark();
    // } else { // finds our issues at compile-time
    //     static_assert(false, "not an animal\n");;
    }
}

int main()
{
    Bear bear;
    speak(bear);
    
    Dog dog;
    speak(dog);
    
    // int x = 69;
    // speak(x);
          
    return 0;
}
