## Redis + Python

```yaml
version: '3.9'

services:
  redis:
    image: redis
    container_name: redis
    ports:
      - 1234:6379
    restart: always

  python:
    image: python:3.11
    container_name: python
    ports:
      - 8001:80
    command: sh -c 'pip install redis && tail -f /dev/null'
    depends_on:
      - redis
    restart: always
```

## Redis + Python + Appium + Gitlab

```yaml
version: '3.9'

services:
  redis:
    image: redis
    container_name: redis
    ports:
      - 1234:6379
    restart: always
    networks:
      - my-network

  python:
    image: python:3.11
    container_name: python
    ports:
      - 8001:80
    command: sh -c 'pip install redis && tail -f /dev/null'
    depends_on:
      - redis
    restart: always
    networks:
      - my-network

  gitlab:
    image: gitlab/gitlab-ce
    container_name: gitlab
    ports:
      - 8081:80
    restart: always
    networks:
      - my-network

  appium:
    image: appium/appium
    container_name: appium
    ports:
      - 4723:4723
    restart: always
    networks:
      - my-network

networks:
  my-network:
    driver: bridge
```

