import redis
import pandas as pd
import pickle

# Sample DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 22],
    'City': ['New York', 'San Francisco', 'Los Angeles']
}
df = pd.DataFrame(data)

# Connect to Redis (make sure you have a Redis server running locally or at the specified address)
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

# Write DataFrame to Redis using pickle
pickled_df = pickle.dumps(df)
redis_client.set('dataframe_key', pickled_df)

# Read DataFrame from Redis
pickled_df_from_redis = redis_client.get('dataframe_key')
df_from_redis = pickle.loads(pickled_df_from_redis)

print("Original DataFrame:")
print(df.to_markdown())

print("\nDataFrame read from Redis:")
print(df_from_redis.to_markdown())
