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
import ml
import graph
import dataset
import util
import explain 

def Label(label):  return ('label', label)
def Appearance(d): return ('Appearance', dataset.DiscreteDistribution(d))
def Shape(d):      return ('Shape',      dataset.DiscreteDistribution(d))

features = [ ('Appearance', ['kitchen', 'office', 'corridor']),
             ('Shape', ['square', 'elongated'])]

input_space_size = reduce(lambda x,y:x*y, map(len, [x[1] for x in features]))

input_space = [[]]
for feature, descriptors in features:
  tmp = []
  for descriptor in descriptors:
    for input in input_space:
      tmp.append(input + [(feature,descriptor)])
  input_space = tmp

input_space = map(tuple, input_space)

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

all_classes = [(0.4, corridor), (0.4, kitchen), (0.4, office)]
known_labels = ['corridor', 'kitchen']
known_classes = [all_classes[0], all_classes[1]]

all_classes   = dataset.DiscreteDistribution(all_classes)
known_classes = dataset.DiscreteDistribution(known_classes)


unlabelled_data = dataset.UnlabelledSample(all_classes, samples = 10000)
labelled_data   = dataset.LabelledSample(known_classes, samples = 1000)
test_data       = dataset.LabelledSample(all_classes, samples = 1000)

unconditional_prob = ml.DiscreteProbabilityEstimator(unlabelled_data, state_size = input_space_size)
conditional_prob   = ml.DiscreteProbabilityEstimator(map(dataset.FilterLabel, labelled_data), state_size = input_space_size)

def density_threshold(sample):
  return conditional_prob(sample)

def semi_threshold(sample):
  print 'Sample = ', sample
  return conditional_prob(sample) / unconditional_prob(sample)


util.WriteFile('explain.tex',
    explain.ExplainDistributions(features,
                                 [('office', office),
                                  ('corridor', corridor),
                                  ('kitchen', kitchen)]))

def PrintSample(sample):
  return ' - '.join(map(lambda x:x[1], sample))

pretty_input_space = map(lambda x: (PrintSample(x), x), input_space)

for filename, title, threshold_func in [
    ('density_threshold.tex', '$P(x|class \in known)$',        density_threshold),
    ('semi_threshold.tex',    '$P(x|class \in known) / P(x)$', semi_threshold)]:
  util.WriteFile(filename,
            explain.SortThresholds(title, pretty_input_space, threshold_func, columns = 1))
