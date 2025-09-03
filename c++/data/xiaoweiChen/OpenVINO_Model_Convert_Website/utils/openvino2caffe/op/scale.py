
def scale(
  proto_layer, 
  proto_layer_infos, 
  edges_info):
  
  for key, proto_layer_info in proto_layer_infos.items():
    if proto_layer_info['name'] == proto_layer.name:
      cur_proto_layer_info = proto_layer_info
      break
      
  has_biases = 'biases' in cur_proto_layer_info
  layer_info = proto_layer_infos[int(cur_proto_layer_info['id'])]
  
    #proto
  for edge in edges_info:
    if edge['to-layer'] == cur_proto_layer_info['id']:
      
      top_name = proto_layer_infos[int(edge['to-layer'])]['name']
      if not top_name in proto_layer.top:
        proto_layer.top.append(top_name)
        
      bottom_name = proto_layer_infos[int(edge['from-layer'])]['name']
      if not bottom_name in proto_layer.bottom:
        proto_layer.bottom.append(bottom_name)
        
  if has_biases:
    proto_layer.scale_param.bias_term = True
  
def saveScaleParam(
  proto_layer,
  proto_layer_infos,
  scale_param):
  
  for key, proto_layer_info in proto_layer_infos.items():
    if proto_layer_info['name'] == proto_layer.name:
      cur_proto_layer_info = proto_layer_info
      break
      
  has_biases = 'biases' in cur_proto_layer_info
  layer_info = proto_layer_infos[int(cur_proto_layer_info['id'])]
  
  scale_param[0].data[...] = layer_info['weights_value']
  
  if has_biases:
    scale_param[1].data[...] = layer_info['biases_value']
  
  
  
  
  
  
  
  
  
  
  
  
  