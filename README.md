# simple_commandify
Convert a set of python functions into a command-line application.

## Features
- Arg names equivalent to python function args
- Type decorators preserved
- Unsafe mode enables evaluating args as valid python
- Auto help via doc-strings
- *just works*: regardless of how you make your function / docstring

## Usage

Step 1.
Install simple_commandify
```bash
pip install simple_commandify
```

Step 2.
```python
def your_functions(with_args: 'and decorators', of_all_types=None):
  ''' Your short description.
  Your long description / parameter annotations.
  '''
  # your actual process
  pass

# Add this to the bottom of your project
if __name__ == '__main__':
  import simple_commandify; simple_commandify.inject(globals())
```

Step 3. Profit

## Alternatives
- click: https://click.palletsprojects.com/en/7.x/
  Frankly what I use instead of this project, a bit more intrusive than I'd like but easy and fully featured.
- clize: https://clize.readthedocs.io/en/stable/
  More traditional command-line syntax, but more strict with the format of your function args and docstring.
- commandify: https://pypi.org/project/commandify/
  Uses a function decorator to specify commands (instead of automatically finding globals), uses argparse

## Future Direction
- Use `argparse` (and `argcomplete` for auto completions) for more nicer operation
