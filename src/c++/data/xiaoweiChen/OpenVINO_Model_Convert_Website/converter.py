# import all moduls
import sqlite3, os, sys, random
from flask import Flask, request, session
from flask import g, redirect, url_for, abort
from flask import render_template, flash
from flask import send_file, make_response, send_from_directory
from flask import jsonify

from sys import version_info

from contextlib import closing
from werkzeug.utils import secure_filename
import subprocess
import zipfile
import datetime
import struct
import re
import platform

# caffe path
#sys.path.append("/home/xiaowei/caffe/python")

ENV = 'development'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
UPLOAD_FOLDER = os.path.join("temp", "upload")
CONVERTED_FOLDER = os.path.join("temp","converted")

CONVERT_TOOLS = [
  ('openvino', 'Model Converter'),
]
  
OPENVINO_SUPPORTED_PLATFORMS = [
  'VINO',
  'CoreML'
]

OPENVINO_SUPPORTED_FROMEWORKS_MAP = {
  'onnx': ['.onnx'],
  'caffe': ['.caffemodel .prototxt'],
  'kaldi': ['.nnet', '.mdl'],
  'mxnet': ['.params .json'],
  'Tensorflow': ['.pb', '.pbtxt'], # tf
}

if 'INTEL_OPENVINO_DIR' in os.environ:
  INTEL_OPENVINO_DIR = os.environ['INTEL_OPENVINO_DIR']
else:
  print("Please run OpenVINO setupvar.sh script before runing this tool.")
  exit(-1)
  
CONVERTER_DIR = os.path.join(
  INTEL_OPENVINO_DIR,
  'deployment_tools',
  'model_optimizer')

CONVERTER_PY = os.path.join(
  CONVERTER_DIR,
  'mo.py')
  
ENABLE_INT8 = False
CALIBRATE_PY = os.path.join(
  INTEL_OPENVINO_DIR,
  'deployment_tools',
  'tools',
  'calibration_tool',
  'calibrate.py')

if platform.system()=='Windows':
  CPU_EXTENSION = os.path.join(
    INTEL_OPENVINO_DIR,
    'deployment_tools',
    'inference_engine',
    'bin',
    'intel64',
    'Release',
    'cpu_extension_avx2.dll')
elif platform.system()=='Linux':
  CPU_EXTENSION = os.path.join(
    INTEL_OPENVINO_DIR,
    'deployment_tools',
    'inference_engine',
    'lib',
    'intel64',
    'Release',
    'cpu_extension_avx2.so')


# create application
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER
app.config['CONVERTER_PY'] = CONVERTER_PY
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

convert_tools_map = [dict(id=index, url=url, name=name) for index, (url, name) in enumerate(CONVERT_TOOLS)]

def upload_file(file, upload_dir):
  filename = secure_filename(file.filename) #获取上传文件的文件名
  if len(filename) == 0:
    return None
  save_file_path = os.path.join(upload_dir, filename)
  file.save(save_file_path) # 保存文件
  return save_file_path
# end upload_file

def add2zip(convert_file, files):
  with zipfile.ZipFile(convert_file + '.zip', 'w', zipfile.ZIP_DEFLATED) as f:
    for file in files:
      if not os.path.exists(file):
        continue
      _file = file.split(os.sep)[-1]
      f.write(file, _file)

# merge openvino model
def encodeOpenVINO(
  output_path,
  xml_path,
  bin_path):
  
  with open(xml_path) as f:
    xml_content_str = f.read()
    
  with open(bin_path, 'rb') as f:
    bin_content_bin = f.read()
    
  xml_content_bin = str.encode(xml_content_str)
  
  xml_path_size = len(xml_content_bin)

  xml_bin_size = struct.pack('Q', xml_path_size)
  
  bin_path_size = os.path.getsize(bin_path)
  
  with open(output_path, 'wb') as f:
    f.write(xml_bin_size)
    f.write(xml_content_bin)
    f.write(bin_content_bin)

def processPreTrainModels(
  framework,
  model_path,
  output_path,
  platform_conversion_parameters="",
  general_conversion_parameters="",
  convert_int8_image_zip=None):

  #os.environ.setdefault('GLOG_minloglevel', '1')
  
  caffe2openvino_cmd = ' '.join([
    'python',
    CONVERTER_PY,
    "--framework",
    framework,
    platform_conversion_parameters,
    general_conversion_parameters,
    "--input_model",
    model_path,
    '--output_dir',
    output_path])
    
  if not os.path.exists(output_path):
    os.makedirs(output_path)
    
  model_name = model_path.split(os.sep)[-1].rsplit('.', 1)[0]
  output_save_path = output_path#os.path.join(output_path, model_name)
    
  print("Convert to openvino_cmd :", caffe2openvino_cmd)
  
  import subprocess
  lines = ""
  error_context = ""
  content = subprocess.Popen(caffe2openvino_cmd,
    stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    shell=True)
    
  returncode = content.wait()
  print("returncode is", returncode)
    
  for line in content.stdout.readlines():
    lines += bytes.decode(line)
  for line in content.stderr.readlines():
    lines += bytes.decode(line)
    error_str =bytes.decode(line)
    #if "ERROR" in error_str:
    error_context += error_str
  
  print(lines)
  
  if returncode != 0:
    return "", returncode, error_context.split('\n')
  
  print("model_name :", model_name)
  print("output_save_path :", output_save_path)
  
  convert_file = os.path.join(output_save_path, model_name)
  converted_xml_path = convert_file + '.xml'
  
  converted_bin_path = convert_file + '.bin'
      
  #converted_model_merge_model = convert_file + '.openvino-merge.bin'
    
  #encodeOpenVINO(
  #  converted_model_merge_model,
  #  converted_xml_path,
  #  converted_bin_path)
  # merge openvino model

        
  add2zip(
  convert_file,
  [converted_bin_path,
   converted_xml_path,
   #converted_model_merge_model
   ])
    
  return convert_file + '.zip', returncode, ""

def Convert2OpenVINO(
  request,
  cur_upload_dir,
  cur_convert_dir):
  
  response = None
  select_framework = request.values.get("framework")
  select_platform = request.values.get("platform")
  select_suffix_group = request.values.get("suffix")
  upload_files = request.files
  
  os.makedirs(cur_upload_dir, exist_ok=True)
  os.makedirs(cur_convert_dir, exist_ok=True)
  
  framework_suffix_groups = OPENVINO_SUPPORTED_FROMEWORKS_MAP[select_framework]
  select_suffix_id = int(select_suffix_group.split('-')[-1])
  select_suffix_set = framework_suffix_groups[select_suffix_id]
  
  print("upload_files is", upload_files)
  uploadFile_suffix_list = []
  
  uploaded_suffixs = []
  suffix_list = select_suffix_set.split()
  for file in upload_files:
    if file in suffix_list:
      uploaded_suffixs.append(file)
    
  print("select_suffix_set is", select_suffix_set)
  if uploaded_suffixs != suffix_list:
    not_upload_suffix = ""
    
    for need_suffix in suffix_list:
      if not need_suffix in uploaded_suffixs:
        not_upload_suffix += need_suffix + ' '
        
    error_message = "{} not upload!".format(not_upload_suffix)
    
    flash(error_message, category='error')
    
    return openvino(select_framework=select_framework)
    
  upload_file_map = {}
  for suffix in suffix_list:
    upload_file_map[suffix] = upload_file(upload_files[suffix], cur_upload_dir)
  
  # generical options
  general_conversion_parameters = ""
  
  batch = request.form['batch']
  print("batch is", batch)
  if batch.isdigit():
    batch_num = int(batch)
    if batch_num != 0:
      general_conversion_parameters += "--batch {} ".format(batch_num)
  elif select_framework == "Tensorflow":
    general_conversion_parameters += "--batch 1 "
    
  data_type = request.values.get("data_type")
  print("data_type is", data_type)
  general_conversion_parameters += "--data_type {} ".format(data_type)
  
  input_shape = request.values.get("input_shape")
  print("input_shape is", input_shape)
  input_shape_list = input_shape.split(',')
  input_right_number = 0
  if len(input_shape_list) == 4:
    for num in input_shape_list:
      if num.isdigit() and int(num) != 0:
        input_right_number += 1
  if input_right_number == 4:
    general_conversion_parameters += "--input_shape [{}] ".format(input_shape)
    
  scale = request.values.get("scale")
  print("scale is", scale, type(scale))
  int_value = re.compile(r'^[-+]?[0-9]+$')
  float_value = re.compile(r'^[-+]?[0-9]+\.[0-9]+$')
  if int_value.match(scale) != None or float_value.match(scale) != None:
    general_conversion_parameters += "--scale {} ".format(scale)
    
  #mean_values = request.values.get("mean_values")
  #print("mean_values is", mean_values, type(mean_values))
    
  disable_resnet_optimization = request.values.get("disable_resnet_optimization")
  print("disable_resnet_optimization is", disable_resnet_optimization, type(disable_resnet_optimization))
  if disable_resnet_optimization == None:
    general_conversion_parameters += "--disable_resnet_optimization "
    
  disable_fusing = request.values.get("disable_fusing")
  print("disable_fusing is", disable_fusing, type(disable_fusing))
  if disable_fusing == None:
    general_conversion_parameters += "--disable_fusing "
    
  print("general_conversion_parameters is", general_conversion_parameters)
  
  zip_src = None
  if "enable-to-int8" in upload_files:
    zip_src = upload_file(upload_files["enable-to-int8"], cur_upload_dir)
    
  print("zip_src is", zip_src)
  
  platform_conversion_parameters = ""
  
  if select_framework == "caffe":
    if "custom-caffe-proto" in upload_files:
      uploaded_custom_caffe_proto = upload_file(upload_files["custom-caffe-proto"], cur_upload_dir)
      platform_conversion_parameters += "--caffe_parser_path {} ".format(uploaded_custom_caffe_proto)
        
    platform_conversion_parameters += "--input_proto {} ".format(upload_file_map['.prototxt'])
    
    model_path = upload_file_map['.caffemodel']
  elif select_framework == "kaldi":
    
    if "counts-file" in upload_files:
      uploaded_counts_file= upload_file(upload_files["counts-file"], cur_upload_dir)
      platform_conversion_parameters += "--counts {} ".format(uploaded_counts_file)
      
    if request.values.get("remove_output_softmax") != None:
      platform_conversion_parameters += "--remove_output_softmax "
        
    if request.values.get("remove_memory") != None:
      platform_conversion_parameters += "--remove_memory "
        
    if ".nnet" in upload_files and len(upload_files[".nnet"]) != 0:
      model_suffix = ".nnet"
    elif ".mdl" in upload_files and len(upload_files[".mdl"]) != 0:
      model_suffix = ".mdl"
      
    model_path = upload_file_map[model_suffix]
  
  elif select_framework == "mxnet":
    platform_conversion_parameters += "--input_symbol {} ".format(upload_file_map['.json'])
        
    if request.values.get("enable_ssd_gluoncv") != None:
      platform_conversion_parameters += "--enable_ssd_gluoncv "
        
    model_path = upload_file_map[".params"]
  
  elif select_framework == "onnx":
    model_path = upload_file_map[".onnx"]
    
  elif select_framework == "Tensorflow":
    if ".pb" in upload_files:
      model_suffix = ".pb"
    elif ".pbtxt" in upload_files:
      model_suffix = ".pbtxt"
        
    model_path = upload_file_map[model_suffix]
    
    if "config-file" in upload_files:
      uploaded_upload_files = upload_file(upload_files["config-file"], cur_upload_dir)
      platform_conversion_parameters += "--tensorflow_object_detection_api_pipeline_config {} ".format(uploaded_upload_files)
      
    if "tensorflow-use-custom-operations-config-file" in upload_files:
      uploaded_upload_files = upload_file(upload_files["tensorflow-use-custom-operations-config-file"], cur_upload_dir)
      platform_conversion_parameters += "--tensorflow_use_custom_operations_config {} ".format(uploaded_upload_files)
    else:
      select_model_type = request.values.get("model_type")
      print("select_model_type is", select_model_type)
      if select_model_type != "other":
        
        if "yolo" in select_model_type:
          tf_front_json = os.path.join(
            CONVERTER_DIR,
            'extensions',
            'front',
            'tf',
            select_model_type+'.json')
        else:
          tf_front_json = os.path.join(
            CONVERTER_DIR,
            'extensions',
            'front',
            'tf',
            select_model_type+'_support.json')
      
        platform_conversion_parameters += "--tensorflow_use_custom_operations_config {} ".format(tf_front_json)
  else:
    flash("Unknown Framwork: {}".format(select_framework), category='error')
    return openvino(select_framework=select_framework)
      
  print("platform_conversion_parameters is", platform_conversion_parameters)
    
  model_name = os.path.split(model_path)[-1].rsplit('.', 1)[0]
  output_save_path = os.path.join(cur_convert_dir, model_name)
    
  zip_file_path, error_status, error_message = \
    processPreTrainModels(
                    "tf" if select_framework == "Tensorflow" else select_framework,
                    model_path,
                    output_save_path,
                    platform_conversion_parameters,
                    general_conversion_parameters,
                    zip_src)
                        
  if error_status != 0:
    flash("Convert Failed!", category='error')
    flash(error_message, category='error_message')
    return openvino(select_framework=select_framework)
                      
  response = make_response(
    send_file(
      zip_file_path,
      as_attachment=True,
      download_name=model_name + '.zip'))
        
  return response
  
def Convert2CoreML(
  request,
  cur_upload_dir,
  cur_convert_dir):
  
  response = None
  select_framework = request.values.get("framework")
  select_platform = request.values.get("platform")
  select_suffix_group = request.values.get("suffix")
  upload_files = request.files
  
  os.makedirs(cur_upload_dir, exist_ok=True)
  os.makedirs(cur_convert_dir, exist_ok=True)
  
  framework_suffix_groups = OPENVINO_SUPPORTED_FROMEWORKS_MAP[select_framework]
  select_suffix_id = int(select_suffix_group.split('-')[-1])
  select_suffix_set = framework_suffix_groups[select_suffix_id]
  
  print("upload_files is", upload_files)
  uploadFile_suffix_list = []
  
  uploaded_suffixs = []
  suffix_list = select_suffix_set.split()
  for file in upload_files:
    if file in suffix_list:
      uploaded_suffixs.append(file)
    
  print("select_suffix_set is", select_suffix_set)
  if uploaded_suffixs != suffix_list:
    not_upload_suffix = ""
    
    for need_suffix in suffix_list:
      if not need_suffix in uploaded_suffixs:
        not_upload_suffix += need_suffix + ' '
        
    error_message = "{} not upload!".format(not_upload_suffix)
    
    flash(error_message, category='error')
    
    return openvino(select_framework=select_framework)
    
  upload_file_map = {}
  for suffix in suffix_list:
    upload_file_map[suffix] = upload_file(upload_files[suffix], cur_upload_dir)

  if select_framework == "onnx":
    import coremltools as ct
    model_path = upload_file_map[".onnx"]
    
    model_name = os.path.split(model_path)[-1].rsplit('.', 1)[0]
    convert_file = os.path.join(cur_convert_dir, model_name)
  
    converted_ml_path = convert_file + '.mlmodel'
    
    coreml_model = ct.converters.onnx.convert(model=model_path)
    coreml_model.save(converted_ml_path)
    
    response = make_response(
    send_file(
      converted_ml_path,
      as_attachment=True))
      
    return response
    
  else:
    flash("Unknown Framwork: {}".format(select_framework), category='error')
    return openvino()
    
  
@app.route('/')
def index():
  return openvino()

@app.route('/openvino')
def openvino(
  select="openvino",
  select_framework="onnx"):

  openvino_supported_frameworks = []
  
  for framework_index, (framework, suffixs) in enumerate(OPENVINO_SUPPORTED_FROMEWORKS_MAP.items()):
    
    suffix_list = []
    for suffix_index, suffix_group in enumerate(suffixs):
      suffix_list.append(
        dict(
          id=suffix_index,
          suffix_group=suffix_group,
          suffix=suffix_group.split())
      )
      
    openvino_supported_frameworks.append(
      dict(
        id=framework_index,
        name=framework,
        suffix_list=suffix_list
      )
    )
    
  #print(openvino_supported_frameworks)
  
  openvino_supported_platforms = [
    dict(id=index, name=platform) 
    for index, platform in enumerate(OPENVINO_SUPPORTED_PLATFORMS)]

  return render_template(
    'openvino.html', 
    tools=convert_tools_map,
    frameworks=openvino_supported_frameworks,
    platforms=openvino_supported_platforms,
    select=select,
    select_framework=select_framework,
    enable_int8=ENABLE_INT8)

@app.route('/', methods=['POST'])
def upload():

  cur_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
  cur_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], cur_time)
  cur_convert_dir = os.path.join(app.config['CONVERTED_FOLDER'], cur_time)
  
  try:
    if 'VINO' in request.values.get("platform"):
      return Convert2OpenVINO(request, cur_upload_dir, cur_convert_dir)
    elif 'CoreML' in request.values.get("platform"):
      return Convert2CoreML(request, cur_upload_dir, cur_convert_dir)
  except:
    import traceback
    
    traceback.print_exc()
    
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error = traceback.format_exception(exc_type, exc_value, exc_traceback)
    
    #error_context = ""
    #for line in error:
    #  error_context += line + '<br>'
      
    #print("error_context", error_context)
    
    flash("ERROR: {}".format(error[-1]), category='error')

  return openvino()

if __name__ == '__main__':
  print("CONVERTER_PY is", CONVERTER_PY)
  app.run(host='0.0.0.0', port=5000)
  
  
  
  
  
  
