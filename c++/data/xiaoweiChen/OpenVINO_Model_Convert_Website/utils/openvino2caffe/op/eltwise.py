

def eltwise(
  proto_layer, 
  proto_layer_infos, 
  edges_info):
  
  for key, layer_info in proto_layer_infos.items():
    if layer_info['name'] == proto_layer.name:
      cur_proto_layer_info = layer_info
      break
      
  layer_info = proto_layer_infos[int(cur_proto_layer_info['id'])]
  cur_data = layer_info['data']
      
  for edge in edges_info:
    if edge['to-layer'] == cur_proto_layer_info['id']:
    
      top_name = proto_layer_infos[int(edge['to-layer'])]['name']
      if not top_name in proto_layer.top:
        proto_layer.top.append(top_name)
        
      bottom_name = proto_layer_infos[int(edge['from-layer'])]['name']
      if not bottom_name in proto_layer.bottom:
        proto_layer.bottom.append(bottom_name)
        
  operations_map = {
    "mul":0, #"prod"
    "sum":1,
    "max":2,
  }

  eltwise_operation = operations_map[cur_data['operation']]
  
  proto_layer.eltwise_param.operation = eltwise_operation