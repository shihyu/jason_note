import json

data = {
   "name": "Joe Chen", 
   "score": 95, 
   "tel": "0933123456"         
}

json_str = json.dumps(data)
print(json_str)
data2 = json.loads(json_str)
print(data2)
