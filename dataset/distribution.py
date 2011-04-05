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
'''This is a very small python module to define distributions over python data.
Those definitions can then be used to draw samples from them.

Example.:
dA = DiscreteDistribution( [ (10, 'A'), (30, 'B'), (20, ('C')) ] )
GenerateSample(dA) is expected to return:
  10/60 'A's, 30/60 'B's, 20/60 'C's

dB = DiscreteDistribution( [ (10, "hello"), (40, "bye")] )
dist = [dA, dB]
GenerateSample(dist) will return [a, b] where a and b have been draw from dA, dB.
'''

import random

def GenerateSample(definition):
  '''Generates a samples according to a given distribution definition.'''
  if hasattr(definition, 'GenerateSample'):
    return definition.GenerateSample()
  if type(definition) == type([]):
    return map(GenerateSample, definition)
  if type(definition) == type(()):
    return tuple(map(GenerateSample, list(definition)))
  return definition

def Generator(definition):
  '''Creates an infinite iterator over samples from the given distribution.'''
  while True:
    yield GenerateSample(definition)

class DiscreteDistribution:
  def __init__(self, dist_list):
    '''Creates a discrete distribution over a list of distribution.'''
    self.acc_dists  = []
    self.total_prob = 0.0
    for prob, dist in sorted(iter(dist_list), reverse=True):
      assert prob >= 0.0
      self.acc_dists.append((self.total_prob, dist))
      self.total_prob += prob
  
  def GenerateSample(self):
    x = random.random()*self.total_prob
    # TODO: use lower bound (log N)
    prev = None
    for prob, dist in self.acc_dists:
      if prob > x: break
      prev = dist
    return GenerateSample(prev)

  def IterDistributions(self):
    probs = map(lambda x:x[0], self.acc_dists[1:]) + [self.total_prob]
    dists = map(lambda x:x[1], self.acc_dists)
    return zip(probs, dists)

