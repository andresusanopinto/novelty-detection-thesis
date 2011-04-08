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

import collections
import itertools

def NormalizedHistogram(data):
  count_total = 0
  count_value = collections.defaultdict(int)
  for sample in data:
    count_value[sample] += 1
    count_total += 1
  
  def prob(sample):
    return count_value[sample] / float(count_total)
  
  return prob

def ClassDependentEstimator(data, class_estimator, classifier = lambda x: (x[0], x[1])):
  class_data = collections.defaultdict(list)
  class_labels = []
  for sample in data:
    cname, cdata = classifier(sample)
    class_data[cname].append(cdata)
    class_labels.append(cname)
  class_prob = NormalizedHistogram(class_labels)
  class_estimator = dict([(cname, class_estimator(cdata)) for cname, cdata in class_data.items()])
  
  def prob(sample):
    p = 0
    for cname, cestimator in class_estimator.items():
      p += class_prob(cname)*cestimator(sample)
    return p
  return prob


def IndependentFeatureEstimator(data, feature_estimator, feature_iter = iter):
  feature_data = collections.defaultdict(list)
  for sample in data:
    for feature_id, feature_descriptor in feature_iter(sample):
      feature_data[feature_id].append(feature_descriptor)
  feature_prob = dict([(fid, feature_estimator(fdata)) for fid,fdata in feature_data.items()])
  
  def prob(sample):
    p = 1.0
    for fid, fsample in feature_iter(sample):
      p *= feature_prob[fid](fsample)
    return p
  
  return prob


'''
a = IndependentFeatureEstimator([
  ( ('label', 'kitchen'),  ('size', 'small') ),
  ( ('label', 'corridor'), ('size', 'long') ),
  ( ('label', 'kitchen'),  ('size', 'long') )], NormalizedHistogram)

print a( (('label', 'corridor'), ))
print a( (('size', 'small'), ))
print a( (('label', 'corridor'), ('size', 'small'), ))

import sys
sys.exit(0)
'''

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
## With perfect information
################################################
def perfect_conditional_prob(sample):
  return dataset.SampleProbability(known, sample)

def perfect_unconditional_prob(sample):
  return dataset.SampleProbability(world, sample)

def perfect_density_threshold(sample): return perfect_conditional_prob(sample)
def perfect_semi_threshold(sample):    return perfect_conditional_prob(sample)/perfect_unconditional_prob(sample)


test_data = dataset.LabelledSample(world, 10000)

p_roc = lambda title, func: plot_roc(threshold = func,
                                     samples = test_data,
                                     known_labels = known_labels,
                                     title = title)

p_roc('ROC for P(x|c) threshold', perfect_density_threshold)
p_roc('ROC for P(x|c)/P(x) threshold', perfect_semi_threshold)

graph.savefig('perfect-roc.pdf')

################################################
## With perfect information
################################################
known_samples = map(dataset.ExtractLabel, dataset.LabelledSample(known, 1000))
known_samples_without_label = list([x[1] for x in known_samples])
world_samples = dataset.UnlabelledSample(world, 1000)

estimated_conditional_prob = IndependentFeatureEstimator(known_samples_without_label, NormalizedHistogram)
estimated_unconditional_prob = IndependentFeatureEstimator(world_samples, NormalizedHistogram)
estimated_class_conditional_prob = ClassDependentEstimator(known_samples,
  lambda x: IndependentFeatureEstimator(x, NormalizedHistogram))


p_roc('ROC for estimated CD(x|c)/P(x) threshold',
      lambda sample: (0.0001+estimated_class_conditional_prob(sample)) / perfect_unconditional_prob(sample))

p_roc('ROC for estimated CI(x|c)/P(x) threshold',
      lambda sample: (0.0001+estimated_conditional_prob(sample)) / perfect_unconditional_prob(sample))

p_roc('ROC for estimated CD(x|c)/EP(x) threshold',
      lambda sample: (0.0001+estimated_class_conditional_prob(sample)) / (0.0001+estimated_unconditional_prob(sample)))

p_roc('ROC for estimated CI(x|c)/EP(x) threshold',
      lambda sample: (0.0001+estimated_conditional_prob(sample)) / (0.0001+estimated_unconditional_prob(sample)))

graph.savefig('roc-simple.pdf')


graph.show()
