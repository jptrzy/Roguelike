# -*- coding: utf-8 -*- 
# setup file for cx_Freeze

import sys
from cx_Freeze import setup, Executable

executables = [
    Executable(script='main.py')
]

includefiles = ['FSEX300.ttf', 'saves', 'data']
includes = []
excludes = []
packages = []

for dbmodule in ['dbhash', 'gdbm', 'dbm', 'dumbdbm']:
    try:
        __import__(dbmodule)
    except ImportError:
        pass
    else:
        # If we found the module, ensure it's copied to the build directory.
        packages.append(dbmodule)

setup(name='roguelike test',
      version='0.1',
      description='roguelike test',
      options = {'build_exe': {'includes':includes,'excludes':excludes,'packages':packages,'include_files':includefiles}},
      executables=executables
      )
