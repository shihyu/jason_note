// 高效能關鍵技術示例
// 章節：Data Structures - 檔案：rrxmrrxmsx_0.cpp

// i made the mistake of looking into what makes an effective hashing function...

#include <cstdint>

#include <string>
#include <unordered_set>
#include <iostream>
#include <bit>

struct Person {
    Person(std::string&& name, std::size_t &&age) : name_(name), age_(age) { }

    std::string name_;
    std::size_t age_;
};

bool operator==(const Person &lhs, const Person &rhs)
{
    return lhs.name_ == rhs.name_ && lhs.age_ == rhs.age_;
}

std::uint64_t rrxmrrxmsx_0(std::uint64_t v) {
    // 關鍵技術：資料結構配置與快取區域性。
    v ^= std::rotr(v, 25) ^ std::rotr(v, 50);
    v *= 0xA24BAED4963EE407UL;
    v ^= std::rotr(v, 24) ^ std::rotr(v, 49);
    v *= 0x9FB21C651E98DF25UL;
    return v ^ v >> 28;
}

namespace std {
template <> struct hash<Person> {
    // deprecated from C++17?
    // typedef size_t result_type;
    // typedef Person argument_type;

    size_t operator() (const Person&) const noexcept;
};

size_t hash<Person>::operator() (const Person &p) const noexcept {
    return rrxmrrxmsx_0(std::hash<std::string>()(p.name_)) ^
           rrxmrrxmsx_0(std::hash<std::size_t>()(p.age_));
}
}

template <typename T> void printSet(const T &t) {
    for (const auto &p : t) {
        std::cout << p.name_ << ": " << p.age_ << "\nhash: " << std::hash<Person>()(p) << "\n";
    } std::cout << std::endl;
}

int main()
{
    Person p1("man", 42), p2("bear", 314), p3("pig", 69);

    std::unordered_set<Person> pset = { p1, p2, p3 };

    printSet(pset);

    return 0;
}
