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
from Utils import Histogram
from Sampler import SampleN
import numpy as np
import graph

def Normalize(histogram):
  sum = 0
  for key in histogram:
    sum += histogram[key]
  out = Histogram()
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
  c = Histogram()
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
  labels = [x for x in labels]
  def correct(a, b):
    return 1 if a == b else -1
  mat = [[confusion[labels[i],labels[j]]*correct(i, j) for j in range(len(labels))] for i in range(len(labels))]
  graph.hinton(np.array(mat), title="Confusion matrix", vlabels=labels, hlabels=labels)

