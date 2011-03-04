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
import random
import collections

class Distribution:
  def Probability(self, sample):
    """Returns probability of the given input be generated by this distribution."""
    raise NotImplemented
  
  def Generator(self):
    """Returns an infinity iterator that generates samples for this distribution."""
    raise NotImplemented

class UniqueDistribution(Distribution):
  """Defines a distribution that always returns the same value."""
  
  def __init__(self, value):
    self.value = value
  
  def Probability(self, sample):
    if sample == self.value:
      return 1.0
    return 0.0
  
  def Generator(self):
    """Returns an iterator that always yield the same value."""
    def sampler(value):
      while True:
        yield value
    return sampler(self.value)


class HistogramDistribution(Distribution):
  """Defines a discrete distribution according to a given histogram."""
  
  def __init__(self, histogram, normalize = True):
    accumulate = 0.0
    self.distributions = []
    for (key, value) in histogram.items():
      accumulate += value
      self.distributions.append((accumulate, key))
    
    if normalize:
      """Normalize the histogram."""
      for i in range(len(self.distributions)):
        (acc, value) = self.distributions[i]
        self.distributions[i] = (acc/accumulate, value)
      self.distributions[-1] = (1.0, self.distributions[-1][1])
      """Make sure it sums up to one and there is no rounding errors."""

  
  def Probability(self, sample):
    last = 0.0
    prob = 0.0
    for (acc, value) in self.distributions:
      if value == sample:
        prob += acc-last
      last = acc
    return prob
  
  def Generator(self):
    def sampler(acc_list):
      while True:
        x = random.random()
        for (acc, value) in acc_list:
          if x <= acc:
            yield value
            break
    return sampler(self.distributions)


class ClassDistribution:
  """Defines a class distribution."""
  def __init__(self, class_distribution, class_description):
    self.class_distribution = class_distribution
    self.class_description  = class_description
  
  def Probability(self, sample):
    prob = 0.0
    for key in self.class_description:
      prob += (self.class_distribution.Probability(key)*
               self.class_description[key].Probability(sample))
    return prob
  
  def ClassProbability(self, sample):
    for key in self.class_description:
      yield (self.class_distribution.Probability(key)*self.class_description[key].Probability(sample), key)
  
  def ClassGenerator(self):
    def sampler(class_generator, classes_gens):
      while True:
        key = next(class_generator)
        yield (key, next(classes_gens[key]))
    return sampler(self.class_distribution.Generator(),
                  {c: d.Generator() for (c, d) in self.class_description.items()})
  
  def Generator(self):
    def drop_label(gen):
      while True:
        (key, value) = next(gen)
        yield value
    return drop_label(self.ClassGenerator())

def BooleanDistribution(prob):
  """Defines a boolean distribution with the given probability of returning True."""
  assert prob >= 0.0 and prob <= 1.0
  return HistogramDistribution({True:float(prob), False:1.0-float(prob)})

def DiscreteDistribution(distribs):
  """Defines a uniform distribution over the list of distributions."""
  return HistogramDistribution(collections.Counter(distribs))




