//
// Created by Ivan Shynkarenka on 18.01.2016
//

#include "benchmark/cppbenchmark.h"

#include "threads/mpsc_linked_queue.h"

#include <functional>
#include <thread>
#include <vector>

using namespace CppCommon;

const uint64_t items_to_produce = 10000000;
const int producers_from = 1;
const int producers_to = 8;
const auto settings = CppBenchmark::Settings().ParamRange(producers_from, producers_to, [](int from, int to, int& result) { int r = result; result *= 2; return r; });

template<typename T>
void produce_consume(CppBenchmark::Context& context, const std::function<void()>& wait_strategy)
{
    const int producers_count = context.x();
    uint64_t crc = 0;

    // Create multiple producers / single consumer wait-free linked queue
    MPSCLinkedQueue<T> queue;

    // Start consumer thread
    auto consumer = std::thread([&queue, &wait_strategy, &crc]()
    {
        for (uint64_t i = 0; i < items_to_produce; ++i)
        {
            // Dequeue using the given waiting strategy
            T item;
            while (!queue.Dequeue(item))
                wait_strategy();

            // Consume the item
            crc += item;
        }
    });

    // Start producer threads
    std::vector<std::thread> producers;
    for (int producer = 0; producer < producers_count; ++producer)
    {
        producers.emplace_back([&queue, &wait_strategy, producer, producers_count]()
        {
            uint64_t items = (items_to_produce / producers_count);
            for (uint64_t i = 0; i < items; ++i)
            {
                // Enqueue using the given waiting strategy
                while (!queue.Enqueue((T)(items * producer + i)))
                    wait_strategy();
            }
        });
    }

    // Wait for all producers threads
    for (auto& producer : producers)
        producer.join();

    // Wait for the consumer thread
    consumer.join();

    // Update benchmark metrics
    context.metrics().AddOperations(items_to_produce - 1);
    context.metrics().AddItems(items_to_produce);
    context.metrics().AddBytes(items_to_produce * sizeof(T));
    context.metrics().SetCustom("CRC", crc);
}

BENCHMARK("MPSCLinkedQueue<SpinWait>-producers", settings)
{
    produce_consume<int>(context, []{});
}

BENCHMARK("MPSCLinkedQueue<YieldWait>-producers", settings)
{
    produce_consume<int>(context, []{ std::this_thread::yield(); });
}

BENCHMARK_MAIN()
