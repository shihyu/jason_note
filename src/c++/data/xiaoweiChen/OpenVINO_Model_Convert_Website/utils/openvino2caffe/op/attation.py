
def attation(proto_layers, layer_infos, edges_info, attation_num):
  
  for proto_index, proto_layer in enumerate(proto_layers):
  
    for key, layer_info in layer_infos.items():
      if layer_info['name'] == proto_layer.name:
        cur_layer_info = layer_info
        break
        
    cur_data = layer_info['data']
        
    for edge in edges_info:
      if edge['to-layer'] == cur_layer_info['id']:
        
        top_name = layer_infos[int(edge['to-layer'])]['name']
        if not top_name in proto_layer.top:
          proto_layer.top.append(top_name)
          
        bottom_name = layer_infos[int(edge['from-layer']) - proto_index - attation_num]['name']
        if not bottom_name in proto_layer.bottom:
          proto_layer.bottom.append(bottom_name)
          
    if proto_index == 0:
      proto_layer_shape = proto_layer.reshape_param.shape
      proto_layer_shape.dim.append(0)
      proto_layer_shape.dim.append(0)
    else:
      proto_layer.type = 'Scale'
      proto_layer.scale_param.axis = 0
      proto_layer.scale_param.bias_term = False
