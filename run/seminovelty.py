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
import ml
import dataset


show_data_samples = 10


Room = dataset.DefineIndependentPropertySet({
  'Appearance': dataset.DefineProperty('place_appearance_property', ['kitchen', 'office', 'corridor']),
  'RoomShape': dataset.DefineProperty('place_shape_property', ['square', 'elongated']),
})

kitchen = Room({
             'Appearance': {'kitchen': 0.70,    'office': 0.29, 'corridor':0.01},
             'RoomShape' : {'square':  0.60, 'elongated': 0.4},
         })

corridor = Room({
             'Appearance':{'kitchen': 0.01,    'office': 0.01, 'corridor':0.9},
             'RoomShape' :{'square':  0.05, 'elongated': 0.95},
         })
office = Room({
             'Appearance':{'kitchen': 0.30,   'office': 0.69, 'corridor':0.01},
             'RoomShape' :{'square':  0.6, 'elongated': 0.4},
         })


def UnlabelledData(samples = 1000):
  room_categories = {
    'kitchen': kitchen,
    'corridor': corridor,
    'office': office
  }
  world = dataset.ClassDistribution(dataset.DiscreteDistribution(room_categories.keys()), room_categories)
  return list(dataset.SampleN(100, world.Generator()))

def LabelledData(samples = 1000):
  room_categories = {
    'office': office,
#    'kitchen': kitchen,
#    'corridor': corridor
  }
  world = dataset.ClassDistribution(dataset.DiscreteDistribution(room_categories.keys()), room_categories)
  return list(dataset.SampleN(100, world.ClassGenerator()))

def TestData():
  """This data represents the 12 places present on rocs/data/sample/ConceptualGraph/sample2 logs"""
  data = [
   [('roomId', 0), ('placeId', 0), ('place_appearance_property', 'office'), ('place_shape_property', 'elongated')],
   [('roomId', 0), ('placeId', 1), ('place_appearance_property', 'corridor'), ('place_shape_property', 'square')],
   [('roomId', 0), ('placeId', 2), ('place_appearance_property', 'office'), ('place_shape_property', 'elongated')],
   [('roomId', 1), ('placeId', 4), ('place_appearance_property', 'corridor'), ('place_shape_property', 'elongated')],
   [('roomId', 2), ('placeId', 6), ('place_appearance_property', 'kitchen'), ('place_shape_property', 'square')],
   [('roomId', 2), ('placeId', 7), ('place_appearance_property', 'kitchen'), ('place_shape_property', 'square')],
   [('roomId', 2), ('placeId', 8), ('place_appearance_property', 'office'), ('place_shape_property', 'square')],
   [('roomId', 2), ('placeId', 9), ('place_appearance_property', 'office'), ('place_shape_property', 'square')],
   [('roomId', 2), ('placeId', 10), ('place_appearance_property', 'kitchen'), ('place_shape_property', 'square')],
   [('roomId', 2), ('placeId', 11), ('place_appearance_property', 'office'), ('place_shape_property', 'square')],
   [('roomId', 2), ('placeId', 12), ('place_appearance_property', 'office'), ('place_shape_property', 'square')]]
  
  roomCat = { 0: 'office' , 1: 'corridor', 2: 'office' }
  test = []
  for sample in data:
    roomId, appearance, shape = sample[0][1], sample[2], sample[3]
    test.append( (roomCat[roomId], (appearance, shape)))
  return test



unlabelled_data = UnlabelledData()
labelled_data   = LabelledData()
test_data       = TestData()

if show_data_samples:
  print('# Unlabelled Data is like:')
  for x in dataset.SampleN(show_data_samples, unlabelled_data): print(x)
  print('# Labelled Data is like:')
  for x in dataset.SampleN(show_data_samples, labelled_data): print(x)
  print('# Test Data is like:')
  for x in dataset.SampleN(show_data_samples, test_data): print(x)



unconditional_prob = ml.DiscreteProbabilityEstimator(unlabelled_data)
conditional_prob   = ml.DiscreteProbabilityEstimator([sample for label,sample in dataset.ExtractLabel(labelled_data)])

def threshold(sample):
  return conditional_prob(sample) / unconditional_prob(sample)

ct_p = {}
ct_n = {}
for key in ['kitchen', 'corridor', 'office']:
  ct_p[key] = 0
  ct_n[key] = 0

for label, sample in dataset.ExtractLabel(test_data):
  t = threshold(sample)
  print t
  if t > 1.0:
    ct_p[label] += 1
  else:
    ct_n[label] += 1

print ct_p
print ct_n
