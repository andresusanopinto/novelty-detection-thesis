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
import script
import ontology
import explain
import random
import dataset
import graph
import ml

KNOWN_LABELS       = script.option('KNOWN_LABELS').split()
LABELLED_SAMPLES   = int(script.option('LABELLED_SAMPLES'))
UNLABELLED_SAMPLES = int(script.option('UNLABELLED_SAMPLES'))
TEST_SAMPLES       = int(script.option('TEST_SAMPLES'))
PLOT         = script.option('PLOT').split()
OUTPUT       = script.option('OUTPUT')


features = ontology.features
rooms = ontology.rooms

#############################################################################



all_labels = rooms.keys()
world = dataset.DiscreteDistribution([(1, dist) for cat,dist in rooms.items()])
known = dataset.DiscreteDistribution([(1, dist) for cat,dist in rooms.items() if cat in KNOWN_LABELS])

################################################
## Generate training data
################################################
known_samples = map(dataset.ExtractLabel, dataset.LabelledSample(known, LABELLED_SAMPLES))
known_samples_without_label = list([x[1] for x in known_samples])
world_samples = dataset.UnlabelledSample(world, UNLABELLED_SAMPLES)
test_samples = dataset.LabelledSample(world, TEST_SAMPLES)

################################################
## Create probability functions
################################################
def perfect_conditional_prob(sample):
  return dataset.SampleProbability(known, sample)

def perfect_unconditional_prob(sample):
  return dataset.SampleProbability(world, sample)

estimated_unconditional_prob = None
estimated_class_conditional_prob = None

if 'P(G)' in PLOT or 'P(G)/P(G\')' in PLOT:
  estimated_unconditional_prob = ml.IndependentFeatureEstimator(world_samples, ml.NormalizedHistogram)
  estimated_class_conditional_prob = ml.ClassDependentEstimator(known_samples,
    lambda x: ml.IndependentFeatureEstimator(x, ml.NormalizedHistogram))


################################################
## Plotting
################################################
def p_roc(threshold, title, style, samples = test_samples, known_labels = KNOWN_LABELS):
  def ThresholdAndLabel(sample):
    label, sample = dataset.ExtractLabel(sample)
    return threshold(sample), label

  roc_curve = []
  for threshold, label in sorted(map(ThresholdAndLabel, samples), key = lambda x: x, reverse=True):
    roc_curve.append( label in KNOWN_LABELS)
  graph.roc(roc_curve, style, label = title)


plots = {
  'P(G)':
      lambda: p_roc(lambda sample: 0.0001+estimated_class_conditional_prob(sample),
                    'P(G)',
                    'g^-'),
  'P(G)/P(G\')':
      lambda: p_roc(lambda sample: (0.0001+estimated_class_conditional_prob(sample)) / (0.0001+estimated_unconditional_prob(sample)),
                    'P(G)/P(G\')',
                    'b*-'),
  'P(x|k)/P(x)':
      lambda: p_roc(lambda sample: perfect_conditional_prob(sample)/perfect_unconditional_prob(sample),
                    'P(x|k)/P(x)',
                    'ko-'),
  'P(x|k)':
      lambda: p_roc(lambda sample: perfect_conditional_prob(sample),
                    'P(x|k)',
                    'rv-')
}

graph.newfig()
for plot in PLOT:
  plots[plot]()
graph.savefig(OUTPUT)
