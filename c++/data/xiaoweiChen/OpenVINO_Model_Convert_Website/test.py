
import sys
from converter import processPreTrainModels

if __name__ == '__main__':
  if len(sys.argv) < 4:
    print("usage: {} proto caffemodel output_dir".format(sys.argv[0]))
    exit(0)
    
  proto = sys.argv[1]
  model = sys.argv[2]
  output = sys.argv[3]
    
  file_path = processPreTrainModels(
    proto,
    model,
    output)
    
  print("file_path is", file_path)