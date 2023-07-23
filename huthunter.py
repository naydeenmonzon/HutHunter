import os
from pathlib import PurePath,Path
from posixpath import normpath
import sys,sysconfig
from os import environ

p = Path(os.getcwd())

list(p.glob('**/*.py'))
PurePath('setup.py') 
# print(p)

# environ['HOME'] = os.getcwd()

print(environ)