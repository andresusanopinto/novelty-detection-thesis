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
from distribution import DiscreteDistribution, GenerateSample, Generator, SampleProbability

def SampleN(max_samples, data):
  data = iter(data)
  for x in range(max_samples):
    yield next(data)


def ExtractLabel(sample):
  assert sample[0][0] == 'label'
  return sample[0][1], tuple(list(sample)[1:])

def FilterLabel(sample):
  label, sample = ExtractLabel(sample)
  return sample

def UnlabelledSample(distribution, samples = 1000):
  gen = Generator(distribution)
  return list(map(FilterLabel, SampleN(samples, gen)))

def LabelledSample(distribution, samples = 1000):
  gen = Generator(distribution)
  return list(SampleN(samples, gen))

def FeatureFilter(accept=set(), block=set()):
  def filter(sample):
    out = []
    print sample
    for feature in sample:
      fname, fvalue = feature
      if accept and fname in accept:
        out.append(feature)
        continue
      elif block and fname in block:
        continue
      else:
        out.append(feature)
    return tuple(out)
  return filter
