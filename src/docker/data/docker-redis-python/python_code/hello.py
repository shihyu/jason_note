import redis 

r = redis.Redis(host="localhost", port=6379, db=1)
r.set('foo', 'bar')
print(r.get('foo'))


print ("hello world!")
print ("Welcome to python cron job")
