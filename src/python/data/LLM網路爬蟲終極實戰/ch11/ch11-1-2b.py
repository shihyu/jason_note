import asyncio

async def animal_task(message, delay_time):
    await asyncio.sleep(delay_time)
    print(message)

async def concurrent_example():
    # 建立多個協程任務
    tasks = [
        animal_task("貓", 1),
        animal_task("老虎", 2), 
        animal_task("獅子", 1.5)
    ]    
    # 並行執行所有任務
    await asyncio.gather(*tasks)

asyncio.run(concurrent_example())
