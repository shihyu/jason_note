# Producer.py
from kafka import KafkaProducer
from json import dumps
import time

topic_name = "topic_test"

producer = KafkaProducer(
    acks=0,
    compression_type="gzip",
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda x: dumps(x).encode("utf-8"),
)

start = time.time()

print("[begin] producerからメッセージ転送スタート")

for i in range(100):
    # data = {'str': 'result'+str(i)}
    data = {
        "uuid": "1",
        "currency": "USDT",
        "avgTwdPrice": "50000",
        "avgUSDTPrice": "50000",
        "side": "buy",
        "amount": "50",
        "timestamp": 1620000000001,
    }
    # print("メッセージ転送中..." + data["str"])
    producer.send(topic_name, value=data)


producer.flush()

print("[end] 掛かる時間:", time.time() - start)
