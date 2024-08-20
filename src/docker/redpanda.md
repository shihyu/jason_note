## 使用Docker部署Redpanda



```dockerfile
docker pull vectorized/redpanda
docker run -d --name redpanda-node -p 9092:9092 -p 9644:9644 vectorized/redpanda
```

https://github.com/redpanda-data/redpanda/

```python
from confluent_kafka import Producer, Consumer

producer = Producer({"bootstrap.servers": "localhost:9092"})
producer.produce("test-topic", key="key", value="hello redpanda!")
producer.flush()


consumer = Consumer(
    {
        "bootstrap.servers": "localhost:9092",
        "group.id": "test-group",
        "auto.offset.reset": "earliest",
    }
)
consumer.subscribe(["test-topic"])


while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue

    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue

    print(f"Received message: {msg.value().decode('utf-8')}")

consumer.close()

```

