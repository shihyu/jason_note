import asyncio

async def add(number):
    await asyncio.sleep(1)
    return number + 1

result = add(1)

print(f"result = {result}, type = {type(result)}")


