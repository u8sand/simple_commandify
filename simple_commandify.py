''' simple_commandify: Convert a set of python functions into a command-line application.
'''

__version__ = '1.0'

def func_to_spec(func):
  ''' Convert a function into a command-line style option specification.
  '''
  import inspect
  spec = func.__name__
  argspec = inspect.getfullargspec(func)
  args_req = len(argspec.args or []) - len(argspec.defaults or [])
  args_opt = len(argspec.args or []) - args_req
  kwargs_defaults = dict(zip(argspec.args[args_req:], argspec.defaults or []), **(argspec.kwonlydefaults or {}))
  if args_req > 0:
    spec += ' <'
    for ind, arg in enumerate(argspec.args[:args_req]):
      if ind > 0:
        spec += ' '
      spec += arg
      annot = (argspec.annotations or {}).get(arg)
      if annot and getattr(annot, '__name__', None) is not None:
        spec += ':' + annot.__name__
    spec += '>'
  if args_opt > 0:
    spec += ' ['
    for ind, arg in enumerate(argspec.args[args_req:]):
      if ind > 0:
        spec += ' '
      spec += arg
      annot = (argspec.annotations or {}).get(arg)
      if annot and getattr(annot, '__name__', None) is not None:
        spec += ':' + annot.__name__
      spec += '=' + repr(argspec.defaults[ind])
    spec += ']'
  if argspec.varargs:
    spec += ' [*'
    spec += argspec.varargs
    annot = (argspec.annotations or {}).get(argspec.varargs)
    if annot and getattr(annot, '__name__', None) is not None:
      spec += ':' + annot.__name__
    spec += ']'
  if kwargs_defaults:
    spec += ' ['
    for ind, (kwarg, kwarg_default) in enumerate(kwargs_defaults.items()):
      if ind > 0:
        spec += ' '
      spec += '--'
      spec += kwarg
      annot = (argspec.annotations or {}).get(kwarg)
      if annot and getattr(annot, '__name__', None) is not None:
        spec += ':' + annot.__name__
      spec += '=' + repr(kwarg_default)
    spec += ']'
  if argspec.varkw:
    spec += ' [**'
    spec += argspec.varkw
    annot = (argspec.annotations or {}).get(argspec.varkw)
    if annot and getattr(annot, '__name__', None) is not None:
      spec += ':' + annot.__name__
    spec += ']'
  return spec

def arg_to_py_unsafe(arg, ctx={}):
  ''' [NOT SECURE]: In the case of a resolvable python object, resolve it as such
  NOTICE: This is not secure or safe and should not be used in environments that are not
   isolated--arbitrary arguments **will** be evaluated as valid python.
  '''
  try:
    return eval(arg, ctx)
  except:
    pass
  return arg

def arg_to_py_safe(arg, ctx={}):
  ''' Resolve valid json as primitive python object(s).
  '''
  import json
  try:
    return json.loads(arg)
  except:
    pass
  return arg

def argv_to_py(argv, ctx={}, arg_to_py=arg_to_py_safe):
  ''' Quick and dirty python-functions-to-command-line.
  '''
  import re
  name = argv[0]
  if len(argv) < 2:
    print('usage: {} [command] [<kargs ...> [opt_kargs ...] [--kwarg_key=kwarg_val ...]]'.format(name))
    print('command:')
    for funcname, func in ctx.items():
      if funcname.startswith('_') or not callable(func) or getattr(func, '__name__', None) is None:
        continue
      print('', func_to_spec(func), (func.__doc__ or '').split('\n')[0].strip(), sep='\t')
    return
  func, args = ctx[argv[1]], argv[2:]
  kargs = [arg_to_py(arg, ctx) for arg in args if not arg.startswith('--')]
  wargs = [arg for arg in args if arg.startswith('--')]
  kwargs = {key[2:]: arg_to_py(val, ctx) for key, val in map(lambda s: s.split('='), wargs)}
  result = func(*kargs, **kwargs)
  if result is not None:
    print(repr(result))

def _help(func, ctx={}):
  ''' View the full docstring for a function
  '''
  if type(func) == str:
    func = ctx.get(func, func)
  if not callable(func):
    print('Unrecognized command `{}`'.format(func))
  import textwrap
  print('usage:', func_to_spec(func))
  print(textwrap.dedent(func.__doc__.strip('\n')))

def inject(ctx={}):
  ''' Usage:
  if __name__ == '__main__':
    import simple_commandify; simple_commandify.inject(globals())
  '''
  import sys, functools
  def help(func):
    _help(func, ctx=ctx)
  ctx[help.__name__] = help
  argv_to_py(sys.argv, ctx, arg_to_py=arg_to_py_safe)

def inject_unsafe(ctx={}):
  ''' Usage:
  if __name__ == '__main__':
    import simple_commandify; simple_commandify.inject_unsafe(globals())
  '''
  import sys, functools
  def help(func):
    _help(func, ctx=ctx)
  ctx[help.__name__] = help
  argv_to_py(sys.argv, ctx, arg_to_py=arg_to_py_unsafe)
