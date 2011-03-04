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
from collections import Counter

# TODO(andresp): Histogram class on top of collections.Counter
# Histogram comparison measures
def Histogram(data):
  return Counter(x for x in data)

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
  'kitchen': HistogramDistribution({'looks_kitchen':0.90, 'looks_office':0.10}),
  'corridor': HistogramDistribution({'looks_corridor':0.98, 'looks_kitchen':0.01, 'looks_kitchen':0.01}),
  'office':  HistogramDistribution({'looks_office':0.90, 'looks_kitchen': 0.10})
}
test_Distribution(ClassDistribution(DiscreteDistribution(room_categories.keys()), room_categories), 1000)
