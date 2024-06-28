
import dis
import types

def _get_code_from_bytecode(fn_code, bytecode, new_consts):
  # this code get from: https://stackoverflow.com/questions/33348067/modifying-python-bytecode
  return types.CodeType(
    fn_code.co_argcount,
    fn_code.co_kwonlyargcount,
    fn_code.co_posonlyargcount,
    fn_code.co_nlocals,
    fn_code.co_stacksize,
    fn_code.co_flags,
    bytecode,
    new_consts,
    fn_code.co_names,
    fn_code.co_varnames,
    fn_code.co_filename,
    fn_code.co_name,
    fn_code.co_qualname,
    fn_code.co_firstlineno,
    fn_code.co_lnotab,
    fn_code.co_exceptiontable,
    fn_code.co_freevars,
    fn_code.co_cellvars
  )


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

  # temporary convert bytecode to code to get opcodes
  temp = _get_code_from_bytecode(target.__code__, bytecode, co_consts)

  # count of skip "LOAD_CONST"'s
  sc = 0

  # adjust constants
  for op in dis.Bytecode(temp):
    if op.opname == 'LOAD_CONST':

      # skip constants of inject() function
      if sc != new_consts_count:
        sc += 1
        continue
      bytecode = bytecode[:op.offset+1] + (bytecode[op.offset+1]+new_consts_count).to_bytes() + bytecode[op.offset+2:]

  # convert bytecode to code object
  new_code = _get_code_from_bytecode(target.__code__, bytecode, co_consts)

  # replace target's code to new code
  target.__code__ = new_code

  return new_code
