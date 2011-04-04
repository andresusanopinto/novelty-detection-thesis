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
import graph
import dataset

show_data_samples = 0

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

all_classes = [(0.2, corridor), (0.4, kitchen), (0.4, office)]
known_labels = ['kitchen', 'corridor']
known_classes = [all_classes[1], all_classes[0]]

all_classes   = dataset.DiscreteDistribution(all_classes)
known_classes = dataset.DiscreteDistribution(known_classes)


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



unlabelled_data = dataset.UnlabelledSample(all_classes, samples = 10000)
labelled_data   = dataset.LabelledSample(known_classes, samples = 1000)
test_data       = dataset.LabelledSample(all_classes, samples = 1000)
#test_data       = TestData()

if show_data_samples:
  print('# Unlabelled Data is like:')
  for x in dataset.SampleN(show_data_samples, unlabelled_data): print(x)
  print('# Labelled Data is like:')
  for x in dataset.SampleN(show_data_samples, labelled_data): print(x)
  print('# Test Data is like:')
  for x in dataset.SampleN(show_data_samples, test_data): print(x)



unconditional_prob = ml.DiscreteProbabilityEstimator(unlabelled_data, state_size = state_size)
conditional_prob   = ml.DiscreteProbabilityEstimator(map(dataset.FilterLabel, labelled_data), state_size = state_size)

def density_threshold(sample):
  return conditional_prob(sample)

def semi_threshold(sample):
  return conditional_prob(sample) / unconditional_prob(sample)


def plot_roc(threshold, samples, known_labels = known_labels, title=''):
  def ThresholdAndLabel(sample):
    label, sample = dataset.ExtractLabel(sample)
    return threshold(sample), label

  roc_curve = []
  #for threshold, label in sorted(map(ThresholdAndLabel, samples), key = lambda x: x[0], reverse=True):
  for threshold, label in sorted(map(ThresholdAndLabel, samples), key = lambda x: x, reverse=True):
    roc_curve.append( label in known_labels )
  graph.roc(roc_curve, label = title)
  pass

plot_roc(threshold = density_threshold,
         samples   = test_data,
         title= 'ROC for P(x|c) threshold')

plot_roc(threshold = semi_threshold,
         samples   = test_data,
         title= 'ROC for P(x|c)/P(x) threshold')

graph.savefig('example1.pdf')
graph.show()

"""Input space is small, so we can analyze it."""
def analyse(threshold, samples):
  for a in sorted(zip(map(threshold, samples), samples), reverse=True):
    print(a)

inputs = list(set(unlabelled_data))
print('P(x|c) Threshold')
analyse(density_threshold, inputs)

print('P(x|c)/P(x) Threshold')
analyse(semi_threshold, inputs)

