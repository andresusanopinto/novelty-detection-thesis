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
class Classifier:
  """This class is a prototype for implementing classifiers to be
  tested under the developed scripts."""
  
  def Classify(self, sample):
    """Returns the classification of the given sample."""
    raise NotImplemented
  
  def ClassifyThreshold(self, sample):
    """Returns a pair (threshold, class) containing the threshold at which
    classification with the given class would occur."""
    raise NotImplemented


class MAP:
  def __init__(self, class_distribution):
    self.distribution = class_distribution
  
  def ClassifyThreshold(self, sample):
    return sorted(self.distribution.ClassProbability(sample, normalize=True))[-1]
  
  def Classify(self, sample):
    return self.ClassifyThreshold(sample)[1]
  

class SemiNoveltyThreshold:
  def __init__(self, known_distribution, input_distribution, label='known'):
    self.distribution = input_distribution
    self.known_distribution = known_distribution
    self.label = label
  
  def ClassifyThreshold(self, sample):
    p_known = self.known_distribution.Probability(sample)
    density = self.distribution.Probability(sample)
    threshold = p_known/float(density)
    return (threshold, self.label)

