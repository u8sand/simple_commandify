from distutils.core import setup
import simple_commandify

setup(
  name='simple_commandify',
  version=simple_commandify.__version__,
  author='Daniel J. B. Clarke',
  author_email='u8sand@gmail.com',
  url='https://github.com/u8sand/simple_commandify',
  py_modules=['simple_commandify'],
  description='Convert a set of python functions into a command-line application',
  long_description=open('README.md', 'r').read(),
  license='MIT',
  classifiers=[
    'Programming Language :: Python :: 3',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
  ],
)
