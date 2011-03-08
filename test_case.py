#!/usr/bin/python3
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
from Sampler import *
from Test import *
import Classifier

test_Distribution(UniqueDistribution('value'), 100)
test_Distribution(BooleanDistribution(0.5), 1000)
test_Distribution(DiscreteDistribution(['kitchen', 'office', 'sample']), 1000)



Room = DefineIndependentPropertySet({
  'Apperance': DefineProperty('appearance', ['kitchen', 'office', 'corridor']),
  'RoomShape': DefineProperty('room_shape', ['square', 'elongated']),
  'RoomSize' : DefineProperty('room_size',  ['small', 'medium', 'large']),
  'HasBook'  : DefineProperty('found_book', ['yes', 'no']),
  'HasMilk'  : DefineProperty('found_milk', ['yes', 'no']),
  'HasScreen': DefineProperty('found_screen', ['yes', 'no'])
})


room_categories = {
  'kitchen': Room({
                 'Appearance': {'kitchen': 0.70,    'office': 0.29, 'corridor':0.01},
                 'RoomShape' : {'square':  0.60, 'elongated': 0.4},
                 'RoomSize'  : {'small': 0.30, 'medium': 0.6, 'large': 0.2},
                 'HasBook'   : {'yes': 0.4, 'no': 0.6},
                 'HasMilk'   : {'yes': 0.7, 'no': 0.3},
                 'HasScreen' : {'yes': 0.2, 'no': 0.8}
             }),
  'corridor': Room({
                 'Appearance':{'kitchen': 0.01,    'office': 0.01, 'corridor':0.9},
                 'RoomShape' :{'square':  0.05, 'elongated': 0.95},
                 'RoomSize'  :{'small': 0.50, 'medium': 0.5, 'large': 0.2},
                 'HasBook'   :{'yes': 0.1, 'no': 0.9},
                 'HasMilk'   :{'yes': 0.05, 'no': 0.95},
                 'HasScreen' :{'yes': 0.05, 'no': 0.95}
             }),
  'office':  Room({
                 'Appearance':{'kitchen': 0.30,   'office': 0.69, 'corridor':0.01},
                 'RoomShape' :{'square':  0.6, 'elongated': 0.4},
                 'RoomSize'  :{'small': 0.20, 'medium': 0.5, 'large': 0.5},
                 'HasBook'   :{'yes': 0.7, 'no': 0.3},
                 'HasMilk'   :{'yes': 0.2, 'no': 0.8},
                 'HasScreen' :{'yes': 0.89, 'no': 0.11},
             }),
}
room_distrib = ClassDistribution(DiscreteDistribution(room_categories.keys()), room_categories)
test_Distribution(room_distrib, 10000)

room_classifier = Classifier.MAP(room_distrib)

TestClassifier(room_classifier, SampleN(5000, room_distrib.ClassGenerator()))

print(Histogram(x for y in SampleN(100, room_distrib.Generator()) for x in y))


