import sys


gettrace = getattr(sys, 'gettrace', None)

if gettrace is None:
    print('No sys.gettrace')
elif gettrace():
    print('Hmm, Big Debugger is watching me')
else:
    print("Let's do something interesting")
    print(1 / 0)