

import sys
import os
from parse_openvino import praseOpenVINO
from generate_caffe import generateCaffe

def openvinoModel2Caffe(
  xml_path,
  bin_path,
  output_model_name,
  output_dir='.'):
  
  if not os.path.exists(xml_path):
    print("{} xml file path is not exists! Please check!!".format(xml_path))
    exit(-2)
    
  if xml_path.rsplit('.', 1)[1] != 'xml':
    print("{} xml file path is not suffix with .xml! Please check!!".format(xml_path))
    exit(-3)
    
  if not os.path.exists(bin_path):
    print("{} bin file path is not exists! Please check!!".format(bin_path))
    exit(-2)
    
  if bin_path.rsplit('.', 1)[1] != 'bin':
    print("{} bin file path is not suffix with .bin! Please check!!".format(bin_path))
    exit(-3)
      
  openvino_model_info = praseOpenVINO(xml_path, bin_path)
  generateCaffe(openvino_model_info, output_model_name, output_dir)

if __name__ == '__main__':
  
  if len(sys.argv) < 4:
    print("usage: {} openvino_xml_path openvino_bin_path output_model_name [output_dir]".format(sys.argv[0]))
    exit(-1)
    
  xml_path = sys.argv[1]
  bin_path = sys.argv[2]
  output_model_name = sys.argv[3]
  
  output_dir = '.'
  if len(sys.argv) == 5:
    output_dir = sys.argv[4]
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)
  
  openvinoModel2Caffe(xml_path, bin_path, output_model_name, output_dir)
  
  print("OpenVINO model to Caffe model Finished!")
  
  
  
  
  
  
  