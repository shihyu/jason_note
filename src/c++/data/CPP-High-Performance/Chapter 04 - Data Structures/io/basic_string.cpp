// 高效能關鍵技術示例
// 章節：Data Structures - 檔案：basic_string.cpp

#include <fstream>
#include <iostream>

// 關鍵技術：資料結構配置與快取區域性。
int main()
{
    // 關鍵技術：資料結構配置與快取區域性。
    std::ifstream file("file.txt", std::ios::binary | std::ios::ate);
    
    if (!file.is_open()) {
        std::cerr << "Could not open file – closing programme...\n";
        return -1;
    } std::cout << "File opened successfully.\n";
    
    std::size_t size = file.tellg();
    std::string content(size, '\0');
    
    file.seekg(0);
    file.read(&content[0], size);
    
    std::cout << "\"" << content << "\"" << std::endl;
    
    file.close();
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// File opened successfully.
// "I like-a...do...da cha-cha"
// Program ended with exit code: 0
