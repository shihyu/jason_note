
def lrn(proto_layer, layer_infos, edges_info):
  
  for key, layer_info in layer_infos.items():
    if layer_info['name'] == proto_layer.name:
      cur_layer_info = layer_info
      break
  
  # proto
  for edge in edges_info:
    if edge['to-layer'] == cur_layer_info['id']:
      
      top_name = layer_infos[int(edge['to-layer'])]['name']
      if not top_name in proto_layer.top:
        proto_layer.top.append(top_name)
        
      bottom_name = layer_infos[int(edge['from-layer'])]['name']
      if not bottom_name in proto_layer.bottom:
        proto_layer.bottom.append(bottom_name)
    
    cur_data = layer_infos[int(cur_layer_info['id'])]['data']

    proto_layer.lrn_param.local_size = int(cur_data['local-size'])
    proto_layer.lrn_param.alpha = float(cur_data['alpha'])
    proto_layer.lrn_param.beta = float(cur_data['beta'])

    cur_region = cur_data['region']
    if cur_region == 'same':
        proto_layer.norm_region = 1