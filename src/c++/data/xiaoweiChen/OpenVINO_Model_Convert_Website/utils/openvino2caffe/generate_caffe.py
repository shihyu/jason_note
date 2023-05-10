
import os
import caffe
import caffe_pb2
from google.protobuf import text_format

from op.input import input
from op.convolution import convolution, saveConvolutionParam
from op.deconvolution import deconvolution, saveDeconvolutionParam
from op.relu import relu
from op.pooling import pooling
from op.concat import concat
from op.softmax import softmax
from op.eltwise import eltwise
from op.lrn import lrn
from op.innerproduct import innerproduct, saveInnerproductParam
from op.scale import scale, saveScaleParam
from op.activation import activation
from op.reshape import reshape
from op.tile import tile

# openvino : caffe
openvino2caffe_layer_type_map = {
  "Input":"Input",
  #"Input":"GlobalInput",
  "FullyConnected":"InnerProduct",
  #"Ignored..":"Dropout",
  "Convolution":"Convolution",
  "Deconvolution":"Deconvolution",
  "Pooling":"Pooling",
  "BatchNormalization":"BatchNorm",
  "Norm":"LRN",
  "Power":"Power",
  "ReLU":"ReLU",
  "ScaleShift":"Scale",
  "Concat":"Concat",
  "Eltwise":"Eltwise",
  "Flatten":"Flatten",
  "Reshape":"Reshape",
  "Slice":"Slice",
  "SoftMax":"Softmax",
  "Permute":"Permute",
  "ROIPooling":"ROIPooling",
  #"Reshape + Split + Permute + Concat":"ShuffleChannel", #?
  #"ScaleShift + Eltwise":"Axpy", #?
  #"ScaleShift":"BN",
  "DetectionOutput":"DetectionOutput",
  "StridedSlice":"StridedSlice",
  #"Eltwise":"Bias", # operation=sum,
}

def generateCaffe(openvino_model_info, output_model_name, output_dir):
  
  net_version_info, input_shape, layers_info, edges_info = openvino_model_info
  
  proto = caffe_pb2.NetParameter()
  
  proto.name = '-'.join([
    net_version_info['name'], 
    "openvino_model_optimizer_version:"+ 
    net_version_info['version']])
    
  temp_layers_info = {}
  for layer in layers_info:
    id = int(layer['id'])
    temp_layers_info[id] = layer
    
  for index, key in enumerate(temp_layers_info.keys()):
  
    cur_layers_info = temp_layers_info[key]
  
    proto.layer.add()
    
    cur_proto_layer = proto.layer[index]
    cur_proto_layer.name = cur_layers_info['name']
    
    openvino_type = cur_layers_info['type']
    caffe_type = openvino2caffe_layer_type_map[openvino_type] if openvino_type in openvino2caffe_layer_type_map else openvino_type
    
    cur_proto_layer.type = caffe_type
    
    #print(cur_proto_layer.type)
    
    if cur_proto_layer.type == 'Input':
      input(cur_proto_layer, input_shape)
    elif cur_proto_layer.type == 'Convolution':
      convolution(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'ReLU':
      relu(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'Pooling':
      pooling(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'Concat':
      concat(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'Softmax':
      softmax(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'Eltwise':
      eltwise(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'Deconvolution':
      deconvolution(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'LRN':
      lrn(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'InnerProduct':
      innerproduct(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'Scale':
      scale(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'Activation':
      activation(cur_proto_layer, temp_layers_info, edges_info)
    elif cur_proto_layer.type == 'Tile':
      tile(cur_proto_layer, temp_layers_info, edges_info)
    else:
      print("{} not support!".format(cur_proto_layer.type))
      exit(0)
    
  #print(proto)
  #print(model)
  
  output_path = os.path.join(output_dir, output_model_name + "-openvino")
  output_proto_file = output_path + ".prototxt"
  output_model_file = output_path + ".caffemodel"
  
  with open(output_proto_file, "w") as file:
    file.write(text_format.MessageToString(proto))
    
  # model
  caffe.set_mode_cpu()
  output_net = caffe.Net(output_proto_file, caffe.TEST)
  output_params = output_net.params
  
  for index, key in enumerate(temp_layers_info.keys()):
  
    #print('-' * 80)
    
    cur_layers_info = temp_layers_info[key]
  
    cur_proto_layer = proto.layer[index]
    cur_proto_layer.name = cur_layers_info['name']
    
    openvino_type = cur_layers_info['type']
    caffe_type = openvino2caffe_layer_type_map[openvino_type] if openvino_type in openvino2caffe_layer_type_map else openvino_type
    
    cur_proto_layer.type = caffe_type
    
    #print("cur_proto_layer.name", cur_proto_layer.name)
    #print("cur_proto_layer.type", cur_proto_layer.type)
    
    if cur_proto_layer.type == 'Convolution':
      saveConvolutionParam(
        cur_proto_layer, 
        temp_layers_info,
        output_params[cur_proto_layer.name])
    if cur_proto_layer.type == 'Deconvolution':
      saveDeconvolutionParam(
        cur_proto_layer, 
        temp_layers_info,
        output_params[cur_proto_layer.name])
    elif cur_proto_layer.type == 'InnerProduct':
      saveInnerproductParam(
        cur_proto_layer, 
        temp_layers_info,
        output_params[cur_proto_layer.name])
    elif cur_proto_layer.type == 'Scale':
      saveScaleParam(
        cur_proto_layer, 
        temp_layers_info,
        output_params[cur_proto_layer.name])
    elif cur_proto_layer.type == 'BatchNorm':
      pass
      
  output_net.save(output_model_file)
    
  print("[FINISH] write to {}".format(output_proto_file))
  print("[FINISH] write to {}".format(output_model_file))
  
  return output_proto_file, output_model_file
# end generateCaffe

def bn2caffe(running_mean, running_var, bn_param):
    bn_param[0].data[...] = running_mean.numpy()
    bn_param[1].data[...] = running_var.numpy()
    bn_param[2].data[...] = np.array([1.0])

  
  
