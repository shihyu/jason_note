from kafka import KafkaConsumer
import multiprocessing as mp
import threading
import json
import os
import time


def monitor_task(consumer):
    topics = consumer.topics()
    while topics:
        topics = consumer.topics()
        print(topics)
        # if not topics:
        #    raise RuntimeError()
        # print(topics, os.getpid(), type(consumer.topics()))
        time.sleep(30)


def consumer_demo():
    try:
        consumer = KafkaConsumer(
            "kafkademo",
            bootstrap_servers=["localhost:9092"],
            group_id="test",
            # api_version='2.0.2'
            api_version=(0, 10),
            enable_auto_commit=False,
        )
        # process = mp.Process(target=monitor_task, args=(consumer,))
        # process.start()
        thread = threading.Thread(target=monitor_task, args=(consumer,))
        thread.start()

        # print(consumer.bootstrap_connected())
        print(consumer.topics(), os.getpid())
        # print(type(consumer))
        for message in consumer:
            # print(consumer.bootstrap_connected())
            print(
                "receive, key: {}, value: {}".format(
                    json.loads(message.key.decode()), json.loads(message.value.decode())
                )
            )
            consumer.commit()
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    print(os.getpid())
    process = mp.Process(target=consumer_demo)
    process.start()
    process.join()
