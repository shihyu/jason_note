// 高效能關鍵技術示例
// 章節：A Brief Introduction to C++ - 檔案：linked_list.cpp

#include <forward_list>
#include <string>
#include <algorithm>

int num_hamlet(const std::forward_list<std::string> &books) {
    // 關鍵技術：線性走訪與節點配置成本。
    return std::count(books.begin(), books.end(), "Hamlet");
}
