#!/usr/bin/python
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
import ontology
import util
import explain
import random
random.seed(0)


ontology.Load()

rooms = ontology.MakeDistributions()
features = ontology.feature_space
for f in features:
  features[f] = sorted(features[f])
del features['room_category2']

util.WriteFile('explain.tex',
    explain.ExplainDistributions(sorted(features.items()),
                                 sorted(rooms.items())))
