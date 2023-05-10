
def innerproduct(
  proto_layer, 
  proto_layer_infos, 
  edges_info):
  
  for key, proto_layer_info in proto_layer_infos.items():
    if proto_layer_info['name'] == proto_layer.name:
      cur_proto_layer_info = proto_layer_info
      break
      
  has_biases = 'biases' in cur_proto_layer_info
  layer_info = proto_layer_infos[int(cur_proto_layer_info['id'])]
  cur_data = layer_info['data']

  #proto
  for edge in edges_info:
    if edge['to-layer'] == cur_proto_layer_info['id']:
      
      top_name = proto_layer_infos[int(edge['to-layer'])]['name']
      if not top_name in proto_layer.top:
        proto_layer.top.append(top_name)
        
      bottom_name = proto_layer_infos[int(edge['from-layer'])]['name']
      if not bottom_name in proto_layer.bottom:
        proto_layer.bottom.append(bottom_name)

  proto_layer.inner_product_param.num_output = int(cur_data['out-size'])
  
  if not has_biases:
    proto_layer.inner_product_param.bias_term = False

def saveInnerproductParam(
  proto_layer,
  proto_layer_infos,
  innerproduct_param):
        
  for key, proto_layer_info in proto_layer_infos.items():
    if proto_layer_info['name'] == proto_layer.name:
      cur_proto_layer_info = proto_layer_info
      break
      
  has_biases = 'biases' in cur_proto_layer_info
  layer_info = proto_layer_infos[int(cur_proto_layer_info['id'])]
  cur_data = layer_info['data']
  
  if layer_info['precision'] == 'FP32':
    element_type_size = 4
  else:
    element_type_size = 1
  
  weights_real_size = int(layer_info['weights']['size']) // element_type_size
  weights_shape = ( int(cur_data['out-size']), weights_real_size // int(cur_data['out-size']))
   
  #innerproduct_param[0].num = 1
  #innerproduct_param[0].channels = 1
  #innerproduct_param[0].height = int(cur_data['out-size'])
  #innerproduct_param[0].width =  weights_shape // element_type_size // int(cur_data['out-size'])
  #print("innerproduct_param[0].data shape", innerproduct_param[0].data.shape)
  innerproduct_param[0].data[...] = layer_info['weights_value'].reshape(weights_shape)
  #print("weights_value shape", weights_value.shape)
  
  if has_biases:
    #biases_real_size = int(layer_info['biases']['size']) // element_type_size
  
    biases_value = layer_info['biases_value']
    
    #innerproduct_param[1].num = 1
    #innerproduct_param[1].channels = 1
    #innerproduct_param[1].height = 1
    #innerproduct_param[1].width =  int(biases_shape // element_type_size)
    innerproduct_param[1].data[...] = biases_value
    #print("biases_value shape",biases_value.shape)
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  