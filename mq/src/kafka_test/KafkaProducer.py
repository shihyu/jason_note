from kafka import KafkaProducer
from kafka.errors import kafka_errors
import traceback
import json


def producer_demo():
    # 假設生產的消息為鍵值對（不是一定要鍵值對），且序列化方式為json
    producer = KafkaProducer(
        bootstrap_servers=["localhost:9092"],
        key_serializer=lambda k: json.dumps(k).encode(),
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    print(producer.bootstrap_connected())
    # 發送三條消息
    for i in range(0, 3):
        future = producer.send(
            "kafkademo", key="count_num", value=str(i), partition=1  # 同一個key值，會被送至同一個分區
        )  # 向分區1發送消息
        print("send {}".format(str(i)))
        try:
            future.get(timeout=10)  # 監控是否發送成功
        except kafka_errors:  # 發送失敗拋出kafka_errors
            traceback.format_exc()


if __name__ == "__main__":
    producer_demo()
