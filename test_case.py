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

def test_Distribution(dist, samples):
  gen = dist.Generator()
  hist = Counter(next(gen) for x in range(samples))
  for key in hist:
    assert dist.Probability(key) == hist[key]/float(samples)


test_Distribution(UniqueDistribution('value'), 100)


# TODO(andresp): Histogram class on top of collections.Counter
# Histogram comparison measures
def Histogram(data):
  return Counter(x for x in data)

# TODO(andressp): create something like this in sampler module.
def SampleN(max_samples, data):
  for x in range(max_samples):
    yield next(data)


print(Histogram(SampleN(100, BooleanDistribution(0.5).Generator() )))
print(Histogram(SampleN(100, DiscreteDistribution(['kitchen', 'office', 'sample']).Generator() )))

