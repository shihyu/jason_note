docker-compose -f docker-compose.yml up -d
docker-compose -f docker-compose.yml down


docker exec -it my-python sh
# python
Python 3.11.2 (main, Mar 14 2023, 01:34:19) [GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import redis 
>>> r = redis.Redis(host='redis', port=6379)
>>> r.set("test", 1)
True
>>> exit()


docker exec -it my-redis sh
# redis-cli 
127.0.0.1:6379> get test
"1"

