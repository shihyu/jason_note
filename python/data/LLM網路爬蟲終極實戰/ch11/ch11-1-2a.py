import asyncio

async def delay_task(message, delay_time):
    await asyncio.sleep(delay_time)
    print(message)

async def main():
    await delay_task("1: 貓", 1)     # 延遲1秒
    await delay_task("2: 老虎", 1)   # 延遲1秒  
    await delay_task("3: 獅子", 1)   # 延遲1秒

asyncio.run(main())