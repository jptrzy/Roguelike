# Unnamed Roguelike Project

## Overview
This is a currently unnamed roguelike game project. So far, the game has no goal or theme.

I started this roguelike game project in the summer of 2015. I wanted to learn programming by working on my own project, so I decided to try and program my own roguelike game. The project originally used the windows terminal for display, then ncurses, and now uses BearLibTerminal. Since the project was started when I had very little programming experience, some portions of code are really ugly. I am working on revising these areas of code to make the project more readable and efficient.

Currently the project can be successfully packaged using cx_Freeze and run on computers without Python, BearLibTerminal, etc. I will likely upload a download link for the game soon.

My YouTube channel where I sometimes showcase features of the game: https://www.youtube.com/user/SZSIZZ

## Features completed so far:

* Chunk-based render and loading system (currently working on making world infinite)
* Basic mob AI (A* pathfinding, random wander, hostile attacks)
* Dynamic lighting, Day/Night cycles, Obstruction lighting, Ambient lighting
* Windows overhaul, including: panels, pop-ups, scroll bar, text wrapping, escape characters
* Time-based action system (actions take time to prepare, execute, and recover)
* Save/Load game saves using Python's shelve module

## Currently working on:

* Using JSON files to store data instead of hard-coding
* Map generation using the OpenSimplex noise library
* Inventory and items

## Acknowledgments:

### Code used:

* Bresenham's Line Algorithm implementation in Python taken from http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm

* Travis Moy's Python implementation of "Restrictive Precise Angle Shadowcasting" (https://github.com/MoyTW/roguebasin_rpas)

### Libraries used:

* BearLibTerminal: http://foo.wyrd.name/en:bearlibterminal
* OpenSimplex: https://github.com/lmas/opensimplex
