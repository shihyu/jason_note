import redis
 
host = 'localhost'
port = 6379
pool = redis.ConnectionPool(host=host, port=port)
r = redis.Redis(connection_pool=pool)


# name對應的hash中設置一個鍵值對（不存在，則創建；否則，修改）
# 參數：
    # name，redis的name
    # key，name對應的hash中的key
    # value，name對應的hash中的value
# 註：
    # hsetnx(name, key, value),當name對應的hash中不存在當前key時則創建（相當於添加）
r.hset('p_info', 'name', 'bigberg')
r.hset('p_info', 'age', '22')
r.hset('p_info', 'gender', 'M')


# 在name對應的hash中批量設置鍵值對
# 參數：
    # name，redis的name
    # mapping，字典，如：{'k1':'v1', 'k2': 'v2'}
  
# 如：
    # r.hmset('xx', {'k1':'v1', 'k2': 'v2'})
r.hmset('info_2', {'name': 'Jerry', 'species': 'mouse'})
