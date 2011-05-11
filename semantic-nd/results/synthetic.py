#!/usr/bin/python
# -*- coding: utf-8 -*-
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
# ####################################################################
#
# This file contains code that generates the synthetic experiment described on the paper.
#
# The following experiments want to be show:
#  - The presented probability ratio is suitable for novelty detection,
#  - Approximating the unconditional probability improves detection performance.
#  - Measure effect of approximating unconditional probability as the available information increases.
#

import graph
import ontology

def generate_data(samples, classes, with_label):
  while True:
    raise NotImplemented

def exact_conditional_prob(sample):
  raise NotImplemented

def exact_unconditional_prob(sample):
  raise NotImplemented

known_data = """"""
unlabelled_data = """"""


"""Train factors for conditional probability."""
for label, sample in known_data:
  for fid, descriptor in iter_features(sample):
    ct[label][fid][descriptor] += 1

for feature in features:
  for value in feature.value_space:

def conditional_prob(sample):
  for fid, descriptor in iter_features(sample):
    

"""With knowledge on the feature space define a uniform unconditional probability function."""
def uniform_unconditional_prob(sample):
  p = 1.0
  for fid, descriptor in iter_features(sample):
    p *= 1.0/feature_space_size(fid)
  return p

"""Use unlabelled data for model an independent distribution on the unconditional data."""
for sample in unlabelled_data:
  for fid, descriptor in iter_features(sample):
    ct[fit][descriptor] += 1

def independent_unconditional_prob(sample):
  raise NotImplemented


"""Define the novelty threshold functions and plot results."""
def exact_novelty_detector(x):
  return exact_conditional_prob(x)/float(exact_unconditional_prob(x))

def uniform_novelty_detector(x):
  return conditional_prob(x)/float(uniform_unconditional_prob(x))

def independent_novelty_detector(x):
  return conditional_prob(x)/float(independent_unconditional_prob(x))

for output, nfeatures in [('synthetic-all.pdf', -1),
                          ('synthetic-3features.pdf', 3),
                          ('synthetic-5features.pdf', 5),
                          ('synthetic-10features.pdf', 10),
                          ('synthetic-50features.pdf', 50)]:
  data = generate_samples(classes = CLASSES,
                          samples = 10000,
                          nfeatures = nfeatures)
  graph.newfig()
  graph.roc(
    roc_performance(exact_novelty_detector, data),
    roc_performance(uniform_novelty_detector, data),
    roc_performance(independent_novelty_detector, data))
  graph.save(output)

