import aiohttp
import asyncio
import time

# 抓取指定編號的網址


async def get_pokemon(session, number):
    pass


async def main():
    async with aiohttp.ClientSession() as session:
        # 建立 Task 列表
        tasks = []
        for number in range(1, 100):
            tasks.append(asyncio.create_task(get_pokemon(session, number)))

        # 同時執行所有 Tasks
        original_pokemon = await asyncio.gather(*tasks)

        # 輸出結果
        for pokemon in original_pokemon:
            print(pokemon)

start = time.perf_counter()  # 開始測量執行時間

# 執行協同程序
asyncio.run(main())

elapsed = time.perf_counter() - start  # 計算程式執行時間
print(f"執行時間：{elapsed:.2f} 秒")
