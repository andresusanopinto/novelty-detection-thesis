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
from collections import Counter
from Sampler import SampleN

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

# Test a distribution
def test_Distribution(dist, samples):
  hist = Normalize(Histogram(SampleN(samples, dist.Generator())))
  mse = 0
  for key in hist:
    mse += (dist.Probability(key) - hist[key])**2
  print("MSE = %f" % mse)
  assert mse < 0.005


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
  PlotConfusionMatrix(c)
  return c

def PlotConfusionMatrix(confusion):
  labels = set()
  for ((label,guess), count) in confusion.items():
    labels.add(label)
    labels.add(guess)
  print("%20s:" % "Confusion matrix")
  print("%20s:" % "", end = "")
  for label in labels:
    print("%12s" % label, end = "")
  print()
  for label in labels:
    print("%20s:" % label, end = "")
    for guess in labels:
      if label != guess:
        print("%12d" % confusion[(label,guess)], end = "")
      else:
        print("%12d" % 0, end = "")
    print()
  print("%f were correct." % Correctness(confusion))


