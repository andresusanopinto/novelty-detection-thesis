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
import ml

random.seed(0)

#############################################################################
def plot_roc(threshold, samples, known_labels, title=''):
  def ThresholdAndLabel(sample):
    label, sample = dataset.ExtractLabel(sample)
    return threshold(sample), label

  roc_curve = []
  for threshold, label in sorted(map(ThresholdAndLabel, samples), key = lambda x: x, reverse=True):
    roc_curve.append( label in known_labels )
  graph.roc(roc_curve, label = title)
  pass



ontology.Load()
del ontology.feature_space['room_category2']

features = ontology.feature_space
for f in features:
  features[f] = sorted(features[f])

rooms = ontology.MakeDistributions()

util.WriteFile('explain.tex',
    explain.ExplainDistributions(sorted(features.items()),
                                 sorted(rooms.items())))

known_labels = set(['kitchen', 'robotlab', 'singleoffice'])
world = dataset.DiscreteDistribution([(1, dist) for cat,dist in rooms.items()])
known = dataset.DiscreteDistribution([(1, dist) for cat,dist in rooms.items() if cat in known_labels])

################################################
## Generate training data
################################################
known_samples = map(dataset.ExtractLabel, dataset.LabelledSample(known, 1000))
known_samples_without_label = list([x[1] for x in known_samples])
world_samples = dataset.UnlabelledSample(world, 1000)

################################################
## Create probability functions
################################################
def perfect_conditional_prob(sample):
  return dataset.SampleProbability(known, sample)

def perfect_unconditional_prob(sample):
  return dataset.SampleProbability(world, sample)

estimated_conditional_prob = ml.IndependentFeatureEstimator(known_samples_without_label, ml.NormalizedHistogram)
estimated_unconditional_prob = ml.IndependentFeatureEstimator(world_samples, ml.NormalizedHistogram)
estimated_class_conditional_prob = ml.ClassDependentEstimator(known_samples,
  lambda x: ml.IndependentFeatureEstimator(x, ml.NormalizedHistogram))


################################################
## Plotting
################################################
test_data = dataset.LabelledSample(world, 10000)

p_roc = lambda title, func: plot_roc(threshold = func,
                                     samples = test_data,
                                     known_labels = known_labels,
                                     title = title)

graph.newfig()
p_roc('ROC for P(x|c) threshold',
      lambda sample: perfect_conditional_prob(sample))

p_roc('ROC for P(x|c)/P(x) threshold',
      lambda sample: perfect_conditional_prob(sample)/perfect_unconditional_prob(sample))
graph.savefig('roc-perfect.pdf')


graph.newfig()
p_roc('ROC for optimal threshold',
      lambda sample: perfect_conditional_prob(sample)/perfect_unconditional_prob(sample))

p_roc('ROC for CD(x|c)/P(x) threshold',
      lambda sample: (0.0001+estimated_class_conditional_prob(sample)) / perfect_unconditional_prob(sample))

p_roc('ROC for CD(x|c) threshold',
      lambda sample: 0.0001+estimated_conditional_prob(sample))

p_roc('ROC for estimated CD(x|c)/EP(x) threshold',
      lambda sample: (0.0001+estimated_class_conditional_prob(sample)) / (0.0001+estimated_unconditional_prob(sample)))

p_roc('ROC for estimated CI(x|c)/EP(x) threshold',
      lambda sample: (0.0001+estimated_conditional_prob(sample)) / (0.0001+estimated_unconditional_prob(sample)))
graph.savefig('roc-simple.pdf')
