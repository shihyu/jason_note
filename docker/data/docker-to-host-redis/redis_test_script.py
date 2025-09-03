import redis


r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)


# set 設定key-value
r.set("name", "上海-悠悠 127.0.0.1")
print(r.get("name"))
