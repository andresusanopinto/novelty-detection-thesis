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

def Label(label):  return ('label', label)
def Appearance(d): return ('place_appearance_property', dataset.DiscreteDistribution(d))
def Shape(d):      return ('place_shape_property',      dataset.DiscreteDistribution(d))
state_size = 6


kitchen = ( Label('kitchen'),
            Appearance([(0.70, 'kitchen'),
                        (0.29, 'office' ),
                        (0.01, 'corridor')]),
            Shape([(0.60, 'square'),
                   (0.40, 'elongated')])
          )

corridor = ( Label('corridor'),
             Appearance([(0.05, 'kitchen'),
                         (0.05, 'office'),
                         (0.90, 'corridor')]),
             Shape([(0.05, 'square'),
                    (0.95, 'elongated')])
           )

office   = ( Label('office'),
             Appearance([(0.30, 'kitchen'),
                         (0.69, 'office'),
                         (0.01, 'corridor')]),
             Shape([(0.6, 'square'),
                    (0.4, 'elongated')])
           )

print list(dataset.SampleN(2, dataset.Generator(kitchen)))

all_classes = [corridor, kitchen, office]
known_classes = [ corridor, kitchen ]



def UnlabelledData(samples = 10000, classes = all_classes):
  distribution = dataset.DiscreteDistribution([(1, c) for c in classes])
  gen = dataset.Generator(distribution)
  return list(map(dataset.FilterLabel, dataset.SampleN(100, gen)))

def LabelledData(samples = 10000, classes = known_classes):
  distribution = dataset.DiscreteDistribution([(1, c) for c in classes])
  gen = dataset.Generator(distribution)
  return list(dataset.SampleN(100, gen))

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
    test.append( (('label', roomCat[roomId]), appearance, shape) )
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



unconditional_prob = ml.DiscreteProbabilityEstimator(unlabelled_data, state_size = state_size)
conditional_prob   = ml.DiscreteProbabilityEstimator(map(dataset.FilterLabel, labelled_data), state_size = state_size)

def threshold(sample):
  return conditional_prob(sample) / unconditional_prob(sample)

ct_p = {}
ct_n = {}
for key in ['kitchen', 'corridor', 'office']:
  ct_p[key] = 0
  ct_n[key] = 0

for label, sample in map(dataset.ExtractLabel, test_data):
  t = threshold(sample)
  print t
  if t > 1.0:
    ct_p[label] += 1
  else:
    ct_n[label] += 1

print ct_p
print ct_n
