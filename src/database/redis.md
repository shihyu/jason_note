# 安裝 Redis

```shell
sudo apt install redis-server
sudo systemctl status redis-server
```



```python
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.set('foo', 'bar')
print(r.get('foo'))
```

