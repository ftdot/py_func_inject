
import injector


def target():
  print('Hello, world!')
  print('This function just prints "Hello, world!" on screen :)')


def inject():
  print('this code will be injected to target()')

injector.inject_code_to_function(target, inject)
target()
