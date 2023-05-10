import caffe
#import caffe.caffe_pb2 as caffe_pb2
#import mmap
import sys


#model = caffe_pb2.NetParameter()
#with open(sys.argv[1], "rb") as infile:
#  map = mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ)
#  model.MergeFromString(map)

caffe.set_mode_cpu()
output_net = caffe.Net(sys.argv[1], caffe.TEST)
