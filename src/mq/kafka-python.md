# Python操作Kafka的通俗總結



kafka-python文檔：[KafkaConsumer - kafka-python 2.0.2-dev documentation](https://link.zhihu.com/?target=https%3A//kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html)



## 一、基本概念

- Topic：一組消息數據的標記符；
- Producer：生產者，用於生產數據，可將生產後的消息送入指定的Topic；
- Consumer：消費者，獲取數據，可消費指定的Topic；
- Group：消費者組，同一個group可以有多個消費者，一條消息在一個group中，只會被一個消費者獲取；
- Partition：分區，為了保證kafka的吞吐量，一個Topic可以設置多個分區。同一分區只能被一個消費者訂閱。

## 二、本地安裝與啟動（基於Docker）

1. 下載zookeeper鏡像與kafka鏡像：

```text
docker pull wurstmeister/zookeeper
docker pull wurstmeister/kafka
```

2. 本地啟動zookeeper

```text
docker run -d --name zookeeper -p 2181:2181 -t wurstmeister/zookeeper  
```

3. 本地啟動kafka

```python3
docker run -d --name kafka --publish 9092:9092 --link zookeeper \
--env KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
--env KAFKA_ADVERTISED_HOST_NAME=localhost \
--env KAFKA_ADVERTISED_PORT=9092 \
wurstmeister/kafka:latest 
```

注意：上述代碼，將kafka啟動在9092端口

4. 進入kafka bash

```text
docker exec -it kafka bash
cd /opt/kafka/bin
```

5. 創建Topic，分區為2，Topic name為'kafkademo'

```text
kafka-topics.sh --create --zookeeper zookeeper:2181 \
--replication-factor 1 --partitions 2 --topic kafkademo
```

6. 查看當前所有topic

```text
kafka-topics.sh --zookeeper zookeeper:2181 --list
```

7. 安裝kafka-python

```text
pip install kafka-python
```

## 三、生產者（Producer）與消費者（Consumer）

生產者和消費者的簡易Demo，這裡一起演示：

```python
from kafka import KafkaConsumer
import json


def consumer_demo():
    consumer = KafkaConsumer(
        "kafkademo",
        bootstrap_servers=["localhost:9092"],
        group_id="test",
        # api_version='2.0.2'
        api_version=(0, 10),
    )

    print(consumer.bootstrap_connected())
    print(consumer.topics())
    for message in consumer:
        print(consumer.bootstrap_connected())
        print(
            "receive, key: {}, value: {}".format(
                json.loads(message.key.decode()), json.loads(message.value.decode())
            )
        )


if __name__ == "__main__":
    consumer_demo()
```

```python
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
```



這裡建議起兩個terminal，或者兩個jupyter notebook頁面來驗證。

先執行消費者：

```text
consumer_demo()
```

再執行生產者：

```text
producer_demo()
```

會看到如下輸出：

```text
>>> producer_demo()
send 0
send 1
send 2
```



```text
>>> consumer_demo()
receive, key: count_num, value: 0
receive, key: count_num, value: 1
receive, key: count_num, value: 2
```

## 四、消費者進階操作

（1）初始化參數：

列舉一些KafkaConsumer初始化時的重要參數：

- group_id

高並發量，則需要有多個消費者協作，消費進度，則由group_id統一。例如消費者A與消費者B，在初始化時使用同一個group_id。在進行消費時，一條消息被消費者A消費後，在kafka中會被標記，這條消息不會再被B消費（前提是A消費後正確commit）。

- key_deserializer， value_deserializer

與生產者中的參數一致，自動解析。

- auto_offset_reset

消費者啟動的時刻，消息隊列中或許已經有堆積的未消費消息，有時候需求是從上一次未消費的位置開始讀（則該參數設置為earliest），有時候的需求為從當前時刻開始讀之後產生的，之前產生的數據不再消費（則該參數設置為latest）。

- enable_auto_commit， auto_commit_interval_ms

是否自動commit，當前消費者消費完該數據後，需要commit，才可以將消費完的信息傳回消息隊列的控制中心。enable_auto_commit設置為True後，消費者將自動commit，並且兩次commit的時間間隔為auto_commit_interval_ms。



（2）手動commit

```text
def consumer_demo():
    consumer = KafkaConsumer(
        'kafkademo', 
        bootstrap_servers=':9092',
        group_id='test',
        enable_auto_commit=False
    )
    for message in consumer:
        print("receive, key: {}, value: {}".format(
            json.loads(message.key.decode()),
            json.loads(message.value.decode())
            )
        )
        consumer.commit()
```



（3）查看kafka堆積剩餘量

在線環境中，需要保證消費者的消費速度大於生產者的生產速度，所以需要檢測kafka中的剩餘堆積量是在增加還是減小。可以用如下代碼，觀測隊列消息剩餘量：

```text
consumer = KafkaConsumer(topic, **kwargs)
partitions = [TopicPartition(topic, p) for p in consumer.partitions_for_topic(topic)]

print("start to cal offset:")

# total
toff = consumer.end_offsets(partitions)
toff = [(key.partition, toff[key]) for key in toff.keys()]
toff.sort()
print("total offset: {}".format(str(toff)))
    
# current
coff = [(x.partition, consumer.committed(x)) for x in partitions]
coff.sort()
print("current offset: {}".format(str(coff)))

# cal sum and left
toff_sum = sum([x[1] for x in toff])
cur_sum = sum([x[1] for x in coff if x[1] is not None])
left_sum = toff_sum - cur_sum
print("kafka left: {}".format(left_sum))
```

## Check if Kafka Broker is up and running in Python

**Using [`confluent-kafka-python`](https://github.com/confluentinc/confluent-kafka-python) and [`AdminClient`](https://docs.confluent.io/current/clients/confluent-kafka-python/#pythonclient-adminclient)**

https://stackoverflow.com/questions/61226910/how-to-programmatically-check-if-kafka-broker-is-up-and-running-in-python

```py
# Example using confuent_kafka
from confluent_kafka.admin import AdminClient

kafka_broker = {'bootstrap.servers': 'localhost:9092'}
admin_client = AdminClient(kafka_broker)
topics = admin_client.list_topics().topics

if not topics: 
    raise RuntimeError()
```

**Using [`kafka-python`](https://github.com/dpkp/kafka-python) and [`KafkaConsumer`](https://kafka-python.readthedocs.io/en/1.0.2/#kafkaconsumer)**

```py
# example using kafka-python
import kafka


consumer = kafka.KafkaConsumer(group_id='test', bootstrap_servers=['localhost:9092'])
topics = consumer.topics()

if not topics: 
    raise RuntimeError()
```
