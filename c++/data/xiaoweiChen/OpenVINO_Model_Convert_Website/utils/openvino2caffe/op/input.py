

def input(proto_layer, input_shape):

  # proto
  proto_layer.top.append(proto_layer.name)
  proto_layer.input_param.shape.add()
  proto_layer_shape = proto_layer.input_param.shape[0]
  for index, dim in enumerate(input_shape):
    if index == 0 and dim != 1:
      dim = 1
    proto_layer_shape.dim.append(dim)