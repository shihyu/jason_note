#include <iostream>
#include <vector>
#include <memory>
#include <execinfo.h>
#include <cxxabi.h>

class DebugHelper {
public:
    static void printAddress(const std::string& name, void* addr) {
        std::cout << name << ": " << addr << std::endl;
    }

    // 打印當前調用棧
    static void printCallStack() {
        void* buffer[100];
        int nptrs = backtrace(buffer, 100);

        std::cout << "\n=== C++ Call Stack ===\n";
        std::cout << "Raw addresses for addr2line:\n";

        for (int i = 0; i < nptrs; i++) {
            std::cout << buffer[i] << std::endl;
        }

        std::cout << "\n# Decode with addr2line:\n";
        std::cout << "addr2line -Cfpe " << program_invocation_name;
        for (int i = 0; i < nptrs; i++) {
            std::cout << " " << buffer[i];
        }
        std::cout << std::endl;
    }
};

// 測試類模板
template<typename T>
class Container {
private:
    std::vector<T> data;

public:
    void add(const T& item) {
        data.push_back(item);
        if (data.size() == 5) {
            crashHere();  // Line 43 - 故意崩潰點
        }
    }

    void crashHere() {
        DebugHelper::printCallStack();
        // 故意製造崩潰
        T* ptr = nullptr;
        *ptr = data[0];  // Line 50 - Segfault
    }

    void process() {
        for (int i = 0; i < 10; i++) {
            add(T(i));
        }
    }
};

// 測試異常處理
class ExceptionTest {
public:
    void throwException() {
        DebugHelper::printAddress("ExceptionTest::throwException",
                                  (void*)&ExceptionTest::throwException);
        throw std::runtime_error("Test exception for addr2line");
    }

    void level3() {
        throwException();
    }

    void level2() {
        level3();
    }

    void level1() {
        try {
            level2();
        } catch (const std::exception& e) {
            std::cout << "Caught exception: " << e.what() << std::endl;
            DebugHelper::printCallStack();
        }
    }
};

// 測試內聯和模板
template<int N>
inline int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci<N-1>(n-1) + fibonacci<N-2>(n-2);
}

namespace TestNamespace {
    class NestedClass {
    public:
        static void staticMethod() {
            std::cout << "In TestNamespace::NestedClass::staticMethod" << std::endl;
            DebugHelper::printAddress("staticMethod",
                                      (void*)&NestedClass::staticMethod);
        }

        virtual void virtualMethod() {
            std::cout << "In virtual method" << std::endl;
        }
    };
}

int main(int argc, char* argv[]) {
    std::cout << "=== C++ addr2line Demo ===\n";

    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <test_number>\n";
        std::cout << "  1 - Print function addresses\n";
        std::cout << "  2 - Template crash test\n";
        std::cout << "  3 - Exception stack trace\n";
        std::cout << "  4 - Print current addresses\n";

        // 打印一些地址供測試
        std::cout << "\nSample addresses:\n";
        DebugHelper::printAddress("main", (void*)main);
        DebugHelper::printAddress("DebugHelper::printCallStack",
                                  (void*)&DebugHelper::printCallStack);
        DebugHelper::printAddress("Container<int>::process",
                                  (void*)&Container<int>::process);

        // 打印 demangling 示例
        const std::type_info& ti = typeid(Container<std::string>);
        std::cout << "\nMangled name: " << ti.name() << std::endl;

        int status;
        char* demangled = abi::__cxa_demangle(ti.name(), nullptr, nullptr, &status);
        if (status == 0 && demangled) {
            std::cout << "Demangled name: " << demangled << std::endl;
            free(demangled);
        }

        return 0;
    }

    int test = std::stoi(argv[1]);

    switch (test) {
        case 1: {
            // 打印各種函數地址
            TestNamespace::NestedClass::staticMethod();
            TestNamespace::NestedClass obj;
            obj.virtualMethod();
            break;
        }
        case 2: {
            // 模板類崩潰測試
            Container<int> container;
            container.process();
            break;
        }
        case 3: {
            // 異常調用棧測試
            ExceptionTest test;
            test.level1();
            break;
        }
        case 4: {
            // 打印當前調用棧
            DebugHelper::printCallStack();
            break;
        }
        default:
            std::cout << "Invalid test number\n";
    }

    return 0;
}