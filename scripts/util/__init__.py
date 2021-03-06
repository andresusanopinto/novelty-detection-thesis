# -*- coding: utf-8 -*-
#
# Novelty Detection Scripts
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
from collections import defaultdict

# TODO(andresp): Histogram class on top of collections.Counter
# Histogram comparison measures
def Histogram(data = None):
  h = defaultdict(float)
  if data:
    for sample in data:
      h[sample] += 1
  return h

def WriteFile(filename, output):
  print 'Writting:', filename
  file = open(filename, 'w')
  file.write(output)
  file.close()
