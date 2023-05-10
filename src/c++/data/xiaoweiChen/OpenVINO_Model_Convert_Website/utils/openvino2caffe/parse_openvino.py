
import numpy as np
import struct
import xml.etree.cElementTree as ET

def parseBIN(
  bin_path,
  layer_info):

  with open(bin_path, 'rb') as f:
    for layer in layer_info:
    
      if layer['type'] == 'FullyConnected' or \
         layer['type'] == 'Convolution' or \
         layer['type'] == 'Deconvolution'or \
         layer['type'] == 'ScaleShift':
         
        value_mode = layer['precision']
        
        if value_mode == 'FP32':
          value_sizeof = 4
          value_type = 'f'
          np_type = np.float32
        elif value_mode == 'INT8':
          value_sizeof = 1
          value_type = 'b'
          np_type = np.int8
        
        weight_info = layer['weights']
        weight_offset = int(weight_info['offset'])
        weight_size = int(weight_info['size'])
        weight_number = weight_size // value_sizeof
        
        f.seek(weight_offset, 0)
        
        weight_value_binary = f.read(weight_size)
        weight_value_float = struct.unpack(value_type * weight_number, weight_value_binary)
        layer.update({'weights_value':np.array(weight_value_float, np_type)})
        
        if 'biases' in layer:
          bias_info = layer['biases']
          bias_offset = int(bias_info['offset'])
          bias_size = int(bias_info['size'])
          bias_number = bias_size // value_sizeof
          
          f.seek(bias_offset, 0)
          
          bias_value_binary = f.read(bias_size)
          bias_value_float = struct.unpack(value_type * bias_number, bias_value_binary)
          layer.update({'biases_value':np.array(bias_value_float, np_type)})
          
def parseXML(
  xml_path):
  
  tree = ET.parse(xml_path)
  root = tree.getroot()
  
  net_version_info = root.attrib
  
  input_shape = []
  output_shape = []
  layers_info = []
  edges_info = []
  
  for child1 in root:
    for child2 in child1:
      if child2.tag == 'layer':
        
        cur_layer_info = child2.attrib
        
        for data in child2.iterfind('data'):
          cur_layer_info.update({data.tag:data.attrib})

        layer_type = child2.attrib['type']
          
        # input layer
        if layer_type == 'Input':
          for dim in child2.iterfind('output/port/dim'):
            input_shape.append(int(dim.text))
            
        elif layer_type == 'Tile':
          for dim in child2.iterfind('output/port/dim'):
            output_shape.append(int(dim.text))
          cur_layer_info['data'].update({'output': input.text})

        # conv and fullconnected
        elif layer_type == 'FullyConnected' or \
           layer_type == 'Convolution' or \
           layer_type == 'Deconvolution'or \
           layer_type == 'ScaleShift':
           
          for index, input in enumerate(child2.iterfind('input/port/dim')):
            if index == 1 and (not layer_type == 'ScaleShift'):
              cur_layer_info['data'].update({'input': input.text})
              break
           
          weigth_map = {}
          for blobs in child2.iterfind('blobs'):
            
            for value in blobs:
              weigth_map[value.tag] = value.attrib
              
          cur_layer_info.update(weigth_map)
          #exit(0)
        #print(cur_layer_info)
        
        
        layers_info.append(cur_layer_info)
                
      elif child2.tag == 'edge':
        del child2.attrib['from-port']
        del child2.attrib['to-port']
        edges_info.append(child2.attrib)
        
  #print(edges_info) 
  #print(layesr_info)
  #print(input_shape)
  
  return net_version_info, input_shape, layers_info, edges_info
    

def praseOpenVINO(
  xml_path,
  bin_path):
  
  net_version_info, input_shape, layers_info, edges_info = parseXML(xml_path)
  parseBIN(bin_path, layers_info)
  
  return net_version_info, input_shape, layers_info, edges_info
  
  
  
  