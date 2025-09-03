

def pooling(proto_layer, layer_infos, edges_info):
  
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
  
  pool_method = {'max':0, 'avg':1, 'stochastic':2}
      
  proto_layer.pooling_param.pool = pool_method[cur_data['pool-method']]
  
  kernel_size = cur_data['kernel'].split(',')

  if len(kernel_size) == 2 and kernel_size[0] == kernel_size[1]:
    if kernel_size[0] == '1':
      proto_layer.pooling_param.ceil_mode = False
    proto_layer.pooling_param.kernel_size = int(kernel_size[0])
  else:
    proto_layer.pooling_param.kernel_h = int(kernel_size[0])
    proto_layer.pooling_param.kernel_w = int(kernel_size[1])
    
  if 'rounding_type' in cur_data.keys():
    rounding_type = cur_data['rounding_type']
    if rounding_type == 'floor':
      proto_layer.pooling_param.ceil_mode = False
    
  strides = cur_data['strides'].split(',')
  if len(strides) == 2:
    if strides[0] == strides[1]:
      if int(strides[0]) != 1:
        proto_layer.pooling_param.stride = int(strides[0])
    else:
      proto_layer.pooling_param.stride_h = int(strides[0])
      proto_layer.pooling_param.stride_w = int(strides[1])
      
  if cur_data['pads_begin'] == cur_data['pads_end']:
    pads = cur_data['pads_begin'].split(',')
    if len(pads) == 2:
      if pads[0] == pads[1]:
        if int(pads[0]) > 0:
          proto_layer.pooling_param.pad = int(pads[0])
      else:
        proto_layer.pooling_param.pad_h = int(pads[0])
        proto_layer.pooling_param.pad_w = int(pads[1])
  
  '''
  # model
  for edge in edges_info:
    if edge['to-layer'] == cur_layer_info['id']:
      model_layer.top.append(layer_infos[int(edge['to-layer'])]['name'])
      model_layer.bottom.append(layer_infos[int(edge['from-layer']) - skip_relu]['name'])
      
  model_layer.pooling_param.pool = pool_method[cur_data['pool-method']]
  
  kernel_size = cur_data['kernel'].split(',')

  if len(kernel_size) == 2 and kernel_size[0] == kernel_size[1]:
    model_layer.pooling_param.kernel_size = int(kernel_size[0])
  else:
    model_layer.pooling_param.kernel_h = int(kernel_size[0])
    model_layer.pooling_param.kernel_w = int(kernel_size[1])
    
  strides = cur_data['strides'].split(',')
  if len(strides) == 2:
    if strides[0] == strides[1]:
      if int(strides[0]) != 1:
        model_layer.pooling_param.stride = int(strides[0])
    else:
      model_layer.pooling_param.stride_h = int(strides[0])
      model_layer.pooling_param.stride_w = int(strides[1])
      
  if cur_data['pads_begin'] == cur_data['pads_end']:
    pads = cur_data['pads_begin'].split(',')
    if len(pads) == 2:
      if pads[0] == pads[1]:
        if int(pads[0]) > 0:
          model_layer.pooling_param.pad.append(int(pads[0]))
      else:
        model_layer.pooling_param.pad_h = int(pads[0])
        model_layer.pooling_param.pad_w = int(pads[1])
  '''