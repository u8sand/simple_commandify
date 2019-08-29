''' simple_commandify: Convert a set of python functions into a command-line application.
'''

__version__ = '1.0'

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

def func_to_parser(func, parser):
  ''' Convert a function into a command-line style option specification.
  '''
  import inspect, argparse
  spec = func.__name__
  argspec = inspect.getfullargspec(func)
  args_req = len(argspec.args or []) - len(argspec.defaults or [])
  args_opt = len(argspec.args or []) - args_req
  kwargs_defaults = dict(zip(argspec.args[args_req:], argspec.defaults or []), **(argspec.kwonlydefaults or {}))
  if args_req > 0:
    for ind, arg in enumerate(argspec.args[:args_req]):
      annot = (argspec.annotations or {}).get(arg)
      if annot and getattr(annot, '__name__', None) is not None:
        parser.add_argument(arg, type=annot)
      else:
        parser.add_argument(arg)
  if args_opt > 0:
    for ind, arg in enumerate(argspec.args[args_req:]):
      annot = (argspec.annotations or {}).get(arg)
      if annot and getattr(annot, '__name__', None) is not None:
        parser.add_argument(dest=arg, metavar=arg + ':' + annot.__name__, nargs='?', default=repr(argspec.defaults[ind]))
      else:
        parser.add_argument(dest=arg, metavar=arg, nargs='?', default=repr(argspec.defaults[ind]))
  if argspec.varargs:
    annot = (argspec.annotations or {}).get(argspec.varargs)
    if annot and getattr(annot, '__name__', None) is not None:
      parser.add_argument(metavar='*' + argspec.varargs + annot.__name__, dest=argspec.varargs, nargs=argparse.REMAINDER, default=[], action='append')
    else:
      parser.add_argument(metavar='*' + argspec.varargs, dest=argspec.varargs, nargs=argparse.REMAINDER, default=[], action='append')
  if kwargs_defaults:
    for ind, (kwarg, kwarg_default) in enumerate(kwargs_defaults.items()):
      annot = (argspec.annotations or {}).get(kwarg)
      if annot and getattr(annot, '__name__', None) is not None:
        parser.add_argument('--' + kwarg, metavar=kwarg + ':' + annot.__name__, dest=kwarg, default=repr(kwarg_default))
      else:
        parser.add_argument('--' + kwarg, dest=kwarg, default=repr(kwarg_default))
  if argspec.varkw:
    annot = (argspec.annotations or {}).get(argspec.varkw)
    if annot and getattr(annot, '__name__', None) is not None:
      parser.add_argument(metavar='**' + argspec.varkw + ':' + annot, dest=argspec.varkw, nargs=argparse.REMAINDER)
    else:
      parser.add_argument(metavar='**' + argspec.varkw, dest=argspec.varkw, nargs=argparse.REMAINDER)
  return spec

def func_eval(func, args, ctx={}, arg_to_py=arg_to_py_safe):
  import inspect, argparse
  spec = func.__name__
  argspec = inspect.getfullargspec(func)
  print(args, (args[argspec.varargs][0] if argspec.varargs else args[argspec.varkw][0]))
  if argspec.varargs:
    vargs = [arg_to_py(arg, ctx) for arg in args[argspec.varargs][0] if not arg.startswith('--')]
    args.update({ argspec.varargs: vargs })
  if argspec.varkw:
    kwargs = {}
    for arg in ((args[argspec.varargs][0]) if argspec.varargs else (args[argspec.varkw][0])):
      if not arg.startswith('--'):
        continue
      k, v = arg[2:].split('=')
      if kwargs.get(k) is None:
        kwargs[k] = arg_to_py(v, ctx)
      elif type(kwargs[k]) == list:
        kwargs[k].append(arg_to_py(v, ctx))
      else:
        kwargs[k] = [kwargs[k], arg_to_py(v, ctx)]
    args.update({ argspec.varkw: kwargs })
  return func(**args)

def argv_to_py(argv, ctx={}, arg_to_py=arg_to_py_safe):
  ''' Quick and dirty python-functions-to-command-line.
  '''
  import re, argparse
  parser = argparse.ArgumentParser()
  commands_parsers = parser.add_subparsers(dest='__command', help='commands')
  for funcname, func in ctx.items():
    if funcname.startswith('_') or not callable(func) or getattr(func, '__name__', None) is None:
      continue
    command_parser = commands_parsers.add_parser(funcname, description=(func.__doc__ or '').split('\n')[0].strip())
    func_to_parser(func, command_parser)
  try:
    import argcomplete; argcomplete.autocomplete(parser)
  except:
    pass
  args = parser.parse_args()
  result = func_eval(
    ctx[args.__command],
    {k: v for k, v in args.__dict__.items() if k != '__command'},
    ctx=ctx,
    arg_to_py=arg_to_py,
  )
  if result is not None:
    print(repr(result))
  # func, args = ctx[argv[1]], argv[2:]
  # kargs = [arg_to_py(arg, ctx) for arg in args if not arg.startswith('--')]
  # wargs = [arg for arg in args if arg.startswith('--')]
  # kwargs = {key[2:]: arg_to_py(val, ctx) for key, val in map(lambda s: s.split('='), wargs)}

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
