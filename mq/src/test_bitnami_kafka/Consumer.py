# Consumer.py
from kafka import KafkaConsumer
from json import loads
import time

topic_name = "topic_test"
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=["localhost:9092"],
    value_deserializer=lambda x: loads(x.decode("utf-8")),
    enable_auto_commit=False,
    group_id="trading_room",
)

start = time.time()
print("[begin] Topic: %sで consumerがメッセージを受け取る。" % (topic_name))

for message in consumer:
    print(
        "Partition: %d, Offset: %d, Value: %s"
        % (message.partition, message.offset, message.value)
    )
    consumer.commit()

print("[end]掛かる時間 : ", time.time() - start)
