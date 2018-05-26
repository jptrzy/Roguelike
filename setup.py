# -*- coding: utf-8 -*- 
# setup file for cx_Freeze

import sys
from cx_Freeze import setup, Executable

executables = [
    Executable(script='main.py')
]

includefiles = ['FSEX300.ttf', 'saves', 'data', 'bearlibterminal']
includes = []
excludes = []
packages = []

setup(name='roguelike test',
      version='0.1',
      description='roguelike test',
      options = {'build_exe': {'includes':includes,'excludes':excludes,'packages':packages,'include_files':includefiles}},
      executables=executables
      )
