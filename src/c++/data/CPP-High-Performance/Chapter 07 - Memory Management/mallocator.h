// 高效能關鍵技術示例
// 關鍵技術：自訂配置器降低記憶體配置成本。
// 章節：Memory Management - 檔案：mallocator.h

// The infamous "Mallocator" - a stateless allocator

#include <cstddef>
#include <limits>
#include <cstdlib>
#include <new>

#include <iostream>

template <class T> struct Mallocator {
    // 關鍵技術：自訂配置器與記憶體池。
    using value_type = T;
    
    Mallocator() = default;
    
    template <class U> Mallocator(const Mallocator<U>&) noexcept;
    
    template <class U> bool operator==(const Mallocator<U>&) const noexcept
    {
        return true;
    }
    
    template <class U> bool operator!=(const Mallocator<U>&) const noexcept
    {
        return false;
    }
    
    T* allocate(std::size_t n) const
    {
        if (!n) { return nullptr; }
        
        if (n > std::numeric_limits<std::size_t>::max() / sizeof(T)) {
            throw std::bad_array_new_length();
        }
        
        void const *pv = std::malloc(n * sizeof(T));
        
        if (!pv) { throw std::bad_alloc(); }
        
        return static_cast<T*>(pv);
    }
    
    void deallocate(void *p) const noexcept
    {
        std::free(p);
    }
};
