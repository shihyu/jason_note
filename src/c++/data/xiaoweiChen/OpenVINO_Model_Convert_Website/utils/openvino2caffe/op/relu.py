

def relu(proto_layer, layer_infos, edges_info):
  
  for key, layer_info in layer_infos.items():
    if layer_info['name'] == proto_layer.name:
      cur_layer_info = layer_info
      break
      
  for edge in edges_info:
    if edge['to-layer'] == cur_layer_info['id']:
      
      top_name = layer_infos[int(edge['to-layer'])]['name']
      if not top_name in proto_layer.top:
        proto_layer.top.append(top_name)
        
      bottom_name = layer_infos[int(edge['from-layer'])]['name']
      if not bottom_name in proto_layer.bottom:
        proto_layer.bottom.append(bottom_name)
