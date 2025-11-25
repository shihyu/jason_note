import asyncio

async def async_func(value):
    if value:
        await asyncio.sleep(1)  # 模擬非同步操作
        return "成功執行"
    else:
        raise Exception("執行失敗")

async def main():
    try:
        result = await async_func(True)
        print(f"成功: {result}")
    except Exception as error:
        print(f"失敗: {error}")

asyncio.run(main())
