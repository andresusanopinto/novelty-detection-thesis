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
from Classifier import *
from util import Histogram
import collections
import itertools

def NormalizedHistogram(data):
  count_total = 0
  count_value = collections.defaultdict(int)
  for sample in data:
    count_value[sample] += 1
    count_total += 1
  
  def prob(sample):
    return count_value[sample] / float(count_total)
  
  return prob

def ClassDependentEstimator(data, class_estimator, classifier = lambda x: (x[0], x[1])):
  class_data = collections.defaultdict(list)
  class_labels = []
  for sample in data:
    cname, cdata = classifier(sample)
    class_data[cname].append(cdata)
    class_labels.append(cname)
  class_prob = NormalizedHistogram(class_labels)
  class_estimator = dict([(cname, class_estimator(cdata)) for cname, cdata in class_data.items()])
  
  def prob(sample):
    p = 0
    for cname, cestimator in class_estimator.items():
      p += class_prob(cname)*cestimator(sample)
    return p
  return prob

def IndependentFeatureEstimator(data, feature_estimator, feature_iter = iter):
  feature_data = collections.defaultdict(list)
  for sample in data:
    for feature_id, feature_descriptor in feature_iter(sample):
      feature_data[feature_id].append(feature_descriptor)
  feature_prob = dict([(fid, feature_estimator(fdata)) for fid,fdata in feature_data.items()])
  
  def prob(sample):
    p = 1.0
    for fid, fsample in feature_iter(sample):
      p *= feature_prob[fid](fsample)
    return p
  
  return prob
