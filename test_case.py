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
import Classifier
from collections import Counter

# TODO(andresp): Histogram class on top of collections.Counter
# Histogram comparison measures
def Histogram(data):
  return Counter(data)

def Normalize(histogram):
  sum = 0
  for key in histogram:
    sum += histogram[key]
  out = Counter()
  for key in histogram:
    out[key] = histogram[key]/float(sum);
  return out


# TODO(andressp): create something like this in sampler module.
def SampleN(max_samples, data):
  for x in range(max_samples):
    yield next(data)

# Test a distribution
def test_Distribution(dist, samples):
  hist = Normalize(Histogram(SampleN(samples, dist.Generator())))
  mse = 0
  for key in hist:
    mse += (dist.Probability(key) - hist[key])**2
  print(hist)
  print("MSE = %f" % mse)
  assert mse < 0.005

test_Distribution(UniqueDistribution('value'), 100)
test_Distribution(BooleanDistribution(0.5), 1000)
test_Distribution(DiscreteDistribution(['kitchen', 'office', 'sample']), 1000)

room_categories = {
  'kitchen': IndependentFeaturesDistribution([
                 HistogramDistribution({'looks_kitchen':0.90, 'looks_office':0.10}),
                 HistogramDistribution({'big_room':0.3, 'small_room':0.6}),
                 HistogramDistribution({'has_apple': 0.8, 'no_apple':0.2})]),
  'corridor': IndependentFeaturesDistribution([
                 HistogramDistribution({'looks_corridor':0.98, 'looks_kitchen':0.01, 'looks_kitchen':0.01}),
                 HistogramDistribution({'big_room':0.9, 'small_room':0.1}),
                 HistogramDistribution({'has_apple': 0.01, 'no_apple':0.99})]),
  'office':  IndependentFeaturesDistribution([
                 HistogramDistribution({'looks_office':0.90, 'looks_kitchen': 0.010}),
                 HistogramDistribution({'big_room':0.9, 'small_room':0.1}),
                 HistogramDistribution({'has_apple': 0.2, 'no_apple':0.8})])
}
room_distrib = ClassDistribution(DiscreteDistribution(room_categories.keys()), room_categories)
test_Distribution(room_distrib, 1000)

room_classifier = Classifier.MAP(room_distrib)


def Correctness(confusion_matrix):
  correct = 0
  total = 0
  for ((label,guess),count) in confusion_matrix.items():
    if label == guess: correct += count
    total += count
  return correct/float(total)



def TestClassifier(classifier, labelled_data):
  """Returns confusion matrix."""
  c = Counter()
  for (label, sample) in labelled_data:
    guess = classifier.Classify(sample)
    c[label,guess] += 1
  print(c)
  print(Correctness(c))
  return c

TestClassifier(room_classifier, SampleN(1000, room_distrib.ClassGenerator()))
IndependentFeaturesDistribution
