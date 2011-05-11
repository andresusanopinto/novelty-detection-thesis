#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright 2011: André Susano Pinto
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# This module loads the ontology and creates distributions defined by:
# default_knowledge-semmap.xml and defaultprobs-semmap.txt
#
# This module has some utils used to create python scripts to be called
# from other programs and keep consistent results.
#
# Always use it has the first import on a module.
'''Seed the random generator, we want stable results.'''
import random
random.seed(0)

'''Argument parsing.'''
import collections
args = collections.defaultdict(list)

import sys
import os

for arg in sys.argv[1:]:
  a, b = arg.split('=', 1)
  args[a].append(b)

def arg(argname):
  assert argname in args
  assert len(args[argname]) == 1
  return args[argname][0]

def default_arg(argname, value):
  if argname not in args:
    args[argname].append(value)

'''Control file as options.'''
files_as_option = set()
def declare_file(filename):
  default_arg(filename, filename)
  files_as_option.add(filename)

def WriteFile(filename, content):
  if filename in files_as_option:
    filename = arg(filename)
  f = open(filename, 'w')
  f.write(content)
  f.close()

def option(opt):
  return os.environ[opt]
