#!/usr/bin/python3
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
# This module loads the ontology and creates distributions defined by:
# default_knowledge-semmap.xml and defaultprobs-semmap.txt
#
import script
import re
import math
import dataset
from collections import defaultdict

POISSON_EXPANSION = 3
DEFAULT_KNOWLEDGE = script.option('ONTOLOGY_DEFAULT_KNOWLEDGE')
DEFAULT_OBJ_PROBS = script.option('ONTOLOGY_DEFAULT_OBJ_PROBS')
DROP_FEATURES     = script.option('ONTOLOGY_DROP_FEATURES').split()


potential = dict()
roomcats  = set()
features  = set()
feature_space = defaultdict(set)

def Load():
  print("Loading default knowledge...")
  for line in open(DEFAULT_KNOWLEDGE):
    match = re.match('^\s+<item\s+room_category1="(?P<roomcat>\w+)"\s+' + 
                     '(?P<proptype>\w+)="(?P<propval>\w+)"\s+' + 
                     '(?:potential|probability)="(?P<potential>\S+)"\s*\/>\s*$', line)
    if match:
      roomcat, feature, descriptor, prob = match.groups()
      potential[roomcat, feature, descriptor] = float(prob)
      roomcats.add(roomcat)
      features.add(feature)
      feature_space[feature].add(descriptor)
    elif line.strip() == '':
      pass
    else:
      print "Ignored line: ", line,

  
  print('Loading object probabilities...')
  for line in open(DEFAULT_OBJ_PROBS):
    match = re.match('^INROOM (?P<object>\w+) (?P<roomcat>\w+) (?P<gamma>\S+)\n$', line)
    if match:
      obj, roomcat, p_at_least_one = match.groups()
      feature = 'object_%s' % obj
      gamma = - math.log(1.0 - float(p_at_least_one))
      """Unzip the poisson distribution for up to the given number of samples"""
      features.add(feature)
      t_sum = 0.0
      for k in range(0, POISSON_EXPANSION):
        descriptor = str(k)
        prob = gamma**k * math.exp(-gamma) / math.factorial(k)
        potential[roomcat, feature, descriptor] = prob
        t_sum += prob
        feature_space[feature].add(descriptor)
      potential[roomcat, feature, '%d+' % POISSON_EXPANSION] = 1.0-t_sum
      feature_space[feature].add('%d+' % POISSON_EXPANSION)
    elif line.strip() == '':
      pass
    else:
      print "Ignored line: %s" % line,

def DebugValues():
  print('Loaded %d room categories: %s' % (len(roomcats), roomcats))
  print('Loaded %d feature types: %s' % (len(features), features))
  print('Total input space size: %d (%s)' % (reduce(lambda x,y: x*y, map(len, feature_space.values())), map(len, feature_space.values())))
  print('Feature space is: %s' % feature_space)


room = {}
def MakeDistributions():
  global room
  def MakeDistribution(roomcat):
    out = []
    out.append(('label', roomcat))
    for feature in feature_space:
      f_dist = []
      for descriptor in feature_space[feature]:
        try:
          pot = potential[roomcat, feature, descriptor]
        except KeyError:
          pot = 0.0
          print('Missing potential for: %s, using 0.0' % ((roomcat, feature, descriptor),))
        f_dist.append( (pot, descriptor) )
      
      f_dist = dataset.DiscreteDistribution(f_dist)
      out.append((feature, f_dist))
    return tuple(out)
  
  room_d = {}
  for roomcat in roomcats: room_d[roomcat] = MakeDistribution(roomcat)
  room = room_d
  return room_d
  

'''Generate ontology distributions.'''
Load()
for feature in DROP_FEATURES:
  del feature_space[feature]

features = feature_space
for f in features:
  features[f] = sorted(features[f])

rooms = MakeDistributions()

