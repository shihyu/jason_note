#include <algorithm>
#include <iterator>
#include <vector>
#include <random>
#include <cassert>

template<typename ForwardIterator, typename UnaryPredicate>
constexpr ForwardIterator partition_(ForwardIterator first, ForwardIterator last, UnaryPredicate p)
{
    first = std::find_if_not(first, last, p);
    if (first == last)
    {
        return first;
    }
    for (ForwardIterator it = std::next(first); it != last; ++it)
    {
        if (p(*it))
        {
            std::iter_swap(first, it);
            ++first;
        }
    }
    return first;
}

template<typename RandomIterator, typename Compare>
constexpr void quicksort(RandomIterator first, RandomIterator last, Compare comp) // 2
{
    if (first == last)
    {
        return;
    }
    auto pivot = *std::next(first, std::distance(first, last) / 2);
    auto middle1 = partition_(first, last, [pivot, &comp](const auto& elem) { return comp(elem, pivot); });
    auto middle2 = partition_(middle1, last, [pivot, &comp](const auto& elem) { return !comp(pivot, elem); });
    quicksort(first, middle1, comp);
    quicksort(middle2, last, comp);
}

int main(int argc, char const *argv[])
{
    std::vector<int> vec(1000000, 0);
    std::iota(vec.begin(), vec.end(), 0);
    std::shuffle(vec.begin(), vec.end(), std::mt19937());
    quicksort(vec.begin(), vec.end(), std::less<>());
    assert(std::is_sorted(vec.begin(), vec.end(), std::less<>()));
    return 0;
}
