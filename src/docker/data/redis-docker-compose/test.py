import redis

r = redis.StrictRedis(host='127.0.0.1', port=1234, password='12345678')
print(r.get('yoyo'))
