from distutils.core import setup
from Cython.Build import cythonize
setup(ext_modules = cythonize('run_cython.pyx', language_level="3"))
