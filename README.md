
[![Issues](https://img.shields.io/github/issues/ftdot/py_func_inject?style=for-the-badge)](https://github.com/ftdot/py_func_inject/issues)

---

# Python function injection experiment

I was thinking about the question `This is really to inject a
code into the exists function in python?`. This question is
really interestring. There is my first experimental solution!

My code isn't fully correct. There are a lot of nuances. For
example, injection is tested only on functions that contains
only "print()". You cannot inject a function that will be
contains a variables, positional\keyword arguments.

[![How it works](https://img.shields.io/badge/%23-How_it_works-green?style=for-the-badge)](#how-it-works)

[![Test environment](https://img.shields.io/badge/%23-Test_environment-blue?style=for-the-badge)](#test-environment)

---

🇺🇦 Made with ❤️ in Ukraine!

## How it works

This is code of function that injects a function into
another one:
```python
def inject_code_to_function(target, inject):
  # get bytecode of target function
  bytecode = target.__code__.co_code

  # concat constants
  co_consts = inject.__code__.co_consts + target.__code__.co_consts[1:]

  # strip "RESUME" and "LOAD_CONST", "RETURN_VALUE"
  to_inject = inject.__code__.co_code[2:-4]

  # save "RESUME" at the start of the bytecode
  bytecode = bytecode[:2] + to_inject + bytecode[2:]

  # count new constants
  new_consts_count = len(inject.__code__.co_consts[1:])

  # temporary convert bytecode to code to disassemble and
  # get opcodes
  temp = _get_code_from_bytecode(target.__code__, bytecode, co_consts)

  # count of skipped "LOAD_CONST"'s
  sc = 0

  # adjust constants
  for op in dis.Bytecode(temp):
    if op.opname == 'LOAD_CONST':

      # skip inject()'s constants function that has correct indexes
      if sc != new_consts_count:
        sc += 1
        continue

      bytecode = bytecode[:op.offset+1] + (bytecode[op.offset+1]+new_consts_count).to_bytes() + bytecode[op.offset+2:]

  # convert bytecode to code object
  new_code = _get_code_from_bytecode(target.__code__, bytecode, co_consts)

  # replace target's code to new code
  target.__code__ = new_code

  return new_code

```

Let's take it step by step:

```python
# get bytecode of target function
bytecode = target.__code__.co_code
```

In these lines we just get the bytecode of the function code.
See [bytecode](https://docs.python.org/3/glossary.html#term-bytecode).

```python
# concat constants
co_consts = inject.__code__.co_consts + target.__code__.co_consts[1:]
```

In this line we concat constants of the function to be
injected with the target function. Bytecode contain only
index of constant to load when opcode "LOAD_CONST" is used.
We also remove first value of the target's function contants.
This is required to remove None value that is used as
return value from the function by default. The function
to inject already contains this None as the first value.

This will be a key moment in adjusting an offset of the
constants in future code.

```python
# strip "RESUME" and "LOAD_CONST", "RETURN_VALUE"
to_inject = inject.__code__.co_code[2:-4]
```

In this line we defines a bytecode to be injected at the
start of the target function. We strip the first two
characters because this is "RESUME" opcode. I really
don't know how this opcode works. I can only tell u
that this opcode is required for "yield" functional.
See [this question at StackOverflow](https://stackoverflow.com/questions/77503140/what-does-resume-opcode-actually-do)
to get more information about this opcode.

After stripping the "RESUME" opcode, we remove last 2
opcodes: "LOAD_CONST", "RETURN_VALUE" that which are
responsible for returning a value from a function.

```python
# save "RESUME" at the start of the bytecode
bytecode = bytecode[:2] + to_inject + bytecode[2:]
```

We just concat the bytecode of the target function and
our bytecode to be injected. We also saves a "RESUME"
opcode at the beginning of bytecode.

```python
# count new constants
new_consts_count = len(inject.__code__.co_consts[1:])
```

We get a count of new constants for the function to
be injected. This is required to know the offset of
the constants. What? I already wrote that "LOAD_CONST"
opcodes loads the constants with index. That index is
index of a constant in the "co_consts" tuple. Because
of we inject a new code with new constants to the
function, we required to offset the indexes. The next
code is doing this:

```python
# adjust constants
for op in dis.Bytecode(temp):
  if op.opname == 'LOAD_CONST':

    # skip inject()'s constants function that has correct indexes
    if sc != new_consts_count:
      sc += 1
      continue
    bytecode = bytecode[:op.offset+1] + (bytecode[op.offset+1]+new_consts_count).to_bytes() + bytecode[op.offset+2:]
```

With these lines:

```python
# skip inject()'s constants function that has correct indexes
if sc != new_consts_count:
  sc += 1
  continue
```

We just skip the constants that already has correct
indexes, because of this constants is loaded from
the function to be injected.

```python
bytecode = bytecode[:op.offset+1] + (bytecode[op.offset+1]+new_consts_count).to_bytes() + bytecode[op.offset+2:]
```

At this line we adjusting a constant index from the
concatenated bytecode by the count of the new constants
from the function to be injected.

```python
  # convert bytecode to code object
  new_code = _get_code_from_bytecode(target.__code__, bytecode, co_consts)
```

```python
# replace target's code to new code
target.__code__ = new_code
```

In this line we replaces a code object of the target
function which is responsible for function code.

See `injector.py` to get full code.

See `test.py` to get example usage of this "injector".

## Test environment

- Code tested with Python 3.11
