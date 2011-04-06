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
import dataset
import graph

random.seed(0)

def plot_roc(threshold, samples, known_labels, title=''):
  def ThresholdAndLabel(sample):
    label, sample = dataset.ExtractLabel(sample)
    return threshold(sample), label

  roc_curve = []
  #for threshold, label in sorted(map(ThresholdAndLabel, samples), key = lambda x: x[0], reverse=True):
  for threshold, label in sorted(map(ThresholdAndLabel, samples), key = lambda x: x, reverse=True):
    roc_curve.append( label in known_labels )
  graph.roc(roc_curve, label = title)
  pass



ontology.Load()
rooms = ontology.MakeDistributions()
features = ontology.feature_space
for f in features:
  features[f] = sorted(features[f])
del features['room_category2']

util.WriteFile('explain.tex',
    explain.ExplainDistributions(sorted(features.items()),
                                 sorted(rooms.items())))

known_labels = set(['kitchen', 'robotlab', 'singleoffice'])
world = dataset.DiscreteDistribution([(1, dist) for cat,dist in rooms.items()])
known = dataset.DiscreteDistribution([(1, dist) for cat,dist in rooms.items() if cat in known_labels])

def perfect_conditional_prob(sample):
  return dataset.SampleProbability(known, sample)

def perfect_unconditional_prob(sample):
  return dataset.SampleProbability(world, sample)

def perfect_density_threshold(sample): return perfect_conditional_prob(sample)
def perfect_semi_threshold(sample):    return perfect_conditional_prob(sample)/perfect_unconditional_prob(sample)


test_data = dataset.LabelledSample(world, 5000)
plot_roc(threshold = perfect_density_threshold,
         samples   = test_data,
         known_labels = known_labels,
         title= 'ROC for P(x|c) threshold')

plot_roc(threshold = perfect_semi_threshold,
         samples   = test_data,
         known_labels = known_labels,
         title= 'ROC for P(x|c)/P(x) threshold')

graph.savefig('perfect-roc.tex')
graph.show()

