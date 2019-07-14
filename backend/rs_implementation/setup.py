from distutils.core import setup, Extension

rs_module = Extension('rating_system',
                      sources=['rating_system.c'])

setup(name='rating_system',
      version='1.0',
      description='Rating system package',
      ext_modules=[rs_module])
