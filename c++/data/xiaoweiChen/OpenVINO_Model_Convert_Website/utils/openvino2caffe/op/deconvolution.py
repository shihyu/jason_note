

def deconvolution(
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
    
      top = proto_layer_infos[int(edge['to-layer'])]['name']
      proto_layer.top.append(top)
      
      bottom = proto_layer_infos[int(edge['from-layer'])]['name']
      proto_layer.bottom.append(bottom)

  proto_layer.convolution_param.num_output = int(cur_data['output'])
  
  if not has_biases:
    proto_layer.convolution_param.bias_term = False
  
  if int(cur_data['group']) > 1:
    proto_layer.convolution_param.group = int(cur_data['group'])
  
  dilations = cur_data['dilations'].split(',')
  if len(dilations) == 2 and dilations[0] == dilations[1]:
    if int(dilations[0]) != 1:
      proto_layer.convolution_param.dilation.append(int(dilations[0]))
  else:
    raise "dilations error"
   
  kernel = cur_data['kernel'].split(',')
  if len(kernel) == 2:
    if kernel[0] == kernel[1]:
      proto_layer.convolution_param.kernel_size.append(int(kernel[0]))
    else:
      proto_layer.convolution_param.kernel_h = int(kernel[0])
      proto_layer.convolution_param.kernel_w = int(kernel[1])
    
  strides = cur_data['strides'].split(',')
  if len(strides) == 2:
    if strides[0] == strides[1]:
      if int(strides[0]) != 1:
        proto_layer.convolution_param.stride.append(int(strides[0]))
    else:
      proto_layer.convolution_param.stride_h = int(strides[0])
      proto_layer.convolution_param.stride_w = int(strides[1])
      
  if cur_data['pads_begin'] == cur_data['pads_end']:
    pads = cur_data['pads_begin'].split(',')
    if len(pads) == 2:
      if pads[0] == pads[1]:
        if int(pads[0]) > 0:
          proto_layer.convolution_param.pad.append(int(pads[0]))
      else:
        proto_layer.convolution_param.pad_h = int(pads[0])
        proto_layer.convolution_param.pad_w = int(pads[1])
        
        
def saveDeconvolutionParam(
  proto_layer,
  proto_layer_infos,
  conv_param):
        
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
  
  kernel = cur_data['kernel'].split(',')
  weight_blobs_shape = [
    int(cur_data['output']),
    int(cur_data['input']),
    int(kernel[0]),
    int(kernel[1]),
  ]
  
  weights_value = layer_info['weights_value'].reshape(weight_blobs_shape)
  
  if conv_param[0].data.shape != 0:
    conv_param[0].data.shape = weight_blobs_shape
    weights_value = layer_info['weights_value'].reshape(conv_param[0].data.shape)
  
  conv_param[0].data[...] = weights_value
  #print("weights_value shape", weights_value.shape)
  
  if has_biases:
    biases_shape = int(layer_info['biases']['size'])
  
    biases_value = layer_info['biases_value'].reshape(
      [biases_shape // element_type_size])
    
    conv_param[1].data[...] = biases_value
    #print("biases_value shape",biases_value.shape)
