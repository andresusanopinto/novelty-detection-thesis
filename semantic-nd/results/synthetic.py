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
import bisect
import collections
import random
random.seed(0)

import ontology
import graph
import explain

FEATURES    = ontology.features
ALL_CLASSES = ontology.rooms.keys()
POTENTIAL   = ontology.potential
PROB        = dict()

out = explain.ExplainDistributions(sorted(ontology.features.items()),
                                   sorted(ontology.rooms.items()))

file = open("ontology-explain.tex", 'w')
file.write(out)
file.close()

KNOWN_CLASSES = """bathroom hallway kitchen robotlab singleoffice""".split()
for label in KNOWN_CLASSES: assert label in ALL_CLASSES

"""Make potentials normalized. And calculate probabilities for the synthetic distribution."""
for fid,fspace in FEATURES.items():
  for cat in ALL_CLASSES:
    S = sum([POTENTIAL[cat, fid, fvalue] for fvalue in fspace])
    for fvalue in fspace:
      POTENTIAL[cat, fid, fvalue] /= S
    PROB[cat, fid] = []
    acc_sum = 0.0
    for fvalue in fspace:
      PROB[cat,fid].append( (acc_sum, fvalue))
      acc_sum += POTENTIAL[cat, fid, fvalue]

def generate_samples(samples, labelled, classes, nfeatures):
  def generate_sample():
    label = random.choice(classes)
    nf    = random.choice(nfeatures)
    features = []
    for i in xrange(nf):
      feature = random.choice(FEATURES.keys())
      findex  = max(0, bisect.bisect_left( PROB[label, feature], (random.random(), ''))-1)
      fvalue  = PROB[label, feature][findex][1]
      features.append((feature, fvalue))
    if labelled:
      return label, features
    else:
      return features
      
  for i in xrange(samples):
    yield generate_sample()

def exact_conditional_prob(sample, known=KNOWN_CLASSES):
  p = 0.0
  for label in known:
    p_given_label = 1.0
    for fid, fvalue in sample:
      p_given_label *= POTENTIAL[label, fid, fvalue]
    p += p_given_label * 1.0 / len(KNOWN_CLASSES)
  return p

def exact_unconditional_prob(sample):
  return exact_conditional_prob(sample, ALL_CLASSES)


known_data = generate_samples(samples=100,
                              labelled=True,
                              classes = KNOWN_CLASSES,
                              nfeatures = [5, 7, 10, 15, 20, 50])

unlabelled_data = generate_samples(samples=1000,
                                   labelled=False,
                                   classes = ALL_CLASSES,
                                   nfeatures = [5, 7, 10, 15, 20, 50])


"""Train factors for conditional probability."""
c_ct = collections.defaultdict(int)

for label in KNOWN_CLASSES:
  for fid, fspace in FEATURES.items():
    for fvalue in fspace:
      c_ct[label, fid, fvalue] += 1
      c_ct[label, fid] += 1

for label, sample in known_data:
  for fid, descriptor in sample:
    c_ct[label, fid, descriptor] += 1
    c_ct[label, fid] += 1

def conditional_prob(sample):
  p = 0.0
  for label in KNOWN_CLASSES:
    p_given_class = 1.0
    for fid, fvalue in sample:
      p_given_class *= c_ct[label, fid, fvalue] / float(c_ct[label, fid])
    p += p_given_class * 1.0 / len(KNOWN_CLASSES)
  return p


"""With knowledge on the feature space define a uniform unconditional probability function."""
def uniform_unconditional_prob(sample):
  p = 1.0
  for fid, fvalue in sample:
    p *= 1.0/len(FEATURES[fid])
  return p

"""Use unlabelled data for model an independent distribution on the unconditional data."""
u_ct = collections.defaultdict(int)
for fid, fspace in FEATURES.items():
  for fvalue in fspace:
    c_ct[fid, fvalue] += 1
    c_ct[fid] += 1

for sample in unlabelled_data:
  for fid, fvalue in sample:
    u_ct[fid, fvalue] += 1
    u_ct[fid] += 1

def independent_unconditional_prob(sample):
  p = 1.0
  for fid, fvalue in sample:
    p *= u_ct[fid, fvalue] / float(u_ct[fid])
  return p


"""Define the novelty threshold functions and plot results."""
def exact_novelty_detector(x):
  return exact_conditional_prob(x)/float(exact_unconditional_prob(x))

def uniform_novelty_detector(x):
  return conditional_prob(x)/float(uniform_unconditional_prob(x))

def independent_novelty_detector(x):
  return conditional_prob(x)/float(independent_unconditional_prob(x))


def roc_performance(detector, data, known_labels):
  ct = collections.defaultdict(lambda: [0, 0])
  for label, sample in data:
    threshold = detector(sample)
    ct[threshold][label in known_labels] += 1
  
  roc_curve = []
  for threshold, score in sorted(ct.items(), key = lambda x: x[0], reverse=True):
    roc_curve.append(tuple(score))
  print roc_curve[0:10]
  return roc_curve
    


for output, nfeatures in [('synthetic-all.pdf', [5, 10, 15, 20, 35, 50]),
                          ('synthetic-3features.pdf',  [3]),
                          ('synthetic-5features.pdf',  [5]),
                          ('synthetic-10features.pdf', [10]),
                          ('synthetic-50features.pdf', [50])]:
  print "Generating ", output
  test_samples = list(generate_samples(classes = ALL_CLASSES,
                                  samples = 5000,
                                  labelled = True,
                                  nfeatures = nfeatures))
  R1 = roc_performance(exact_novelty_detector,       test_samples, KNOWN_CLASSES)
  R2 = roc_performance(uniform_novelty_detector,     test_samples, KNOWN_CLASSES)
  R3 = roc_performance(independent_novelty_detector, test_samples, KNOWN_CLASSES)
  
  graph.newfig()
  graph.roc(data = R1, style = 'g^-', label = 'exact')
  graph.roc(data = R2, style = 'b*-', label = 'uniform')
  graph.roc(data = R3, style = 'ro-', label = 'independent')
  graph.savefig(output)

