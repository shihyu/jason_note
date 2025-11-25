import json

data = {
   "name": "Joe Chen", 
   "score": 95, 
   "tel": "0933123456"        
}

jsonfile = "Example.json"
with open(jsonfile, 'w') as fp:
    json.dump(data, fp)
    