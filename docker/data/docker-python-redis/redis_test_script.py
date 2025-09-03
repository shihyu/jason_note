import redis
r = redis.StrictRedis(host='redis-test', port=6379, decode_responses=True)


# set 設定key-value
r.set("name", "上海-悠悠")
print(r.get("name"))
