from typing import List

def adder(*V: List[float]) -> float:
  ''' Compute the sum of a set of values
  '''
  return sum(V)

def product(*V: List[float]) -> float:
  ''' Compute the product of a set of values.
  '''
  import functools
  return functools.reduce(lambda acc, val: acc * val, V, 1)

if __name__ == '__main__':
  import simple_commandify; simple_commandify.inject(globals())
