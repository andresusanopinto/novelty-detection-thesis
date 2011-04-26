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
import dataset
import graph
import collections
import ml
import numpy as np

TEST_SAMPLES = int(script.option('TEST_SAMPLES'))
OUTPUT       = script.option('OUTPUT')

features = ontology.features
rooms = ontology.rooms

world = dataset.DiscreteDistribution([(1, dist) for cat,dist in rooms.items()])
test_samples = dataset.LabelledSample(world, TEST_SAMPLES)
#############################################################################

def map_classifier(sample):
  best = max([(dataset.SampleProbability(dist, sample), label) for label, dist in rooms.items()])
  return best[1]


confusion = collections.defaultdict(int)
for label, sample in map(dataset.ExtractLabel, test_samples):
  guess = map_classifier(sample)
  confusion[label, guess] += 1


'''Plot confusion matrix.'''
labels = set()
for ((label,guess), count) in confusion.items():
  labels.add(label)
  labels.add(guess)
labels = list(sorted(labels))
def correct(a, b):
  return 1 if a == b else -1
mat = [[confusion[labels[i],labels[j]]*correct(i, j) for j in range(len(labels))] for i in range(len(labels))]
graph.hinton(np.array(mat), title="Confusion matrix", vlabels=labels, hlabels=labels)

graph.savefig(OUTPUT)


