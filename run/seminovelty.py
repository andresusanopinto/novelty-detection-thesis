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
import ml
import dataset


Room = dataset.DefineIndependentPropertySet({
  'Appearance': dataset.DefineProperty('appearance', ['kitchen', 'office', 'corridor']),
  'RoomShape': dataset.DefineProperty('room_shape', ['square', 'elongated']),
})

kitchen = Room({
             'Appearance': {'kitchen': 0.70,    'office': 0.29, 'corridor':0.01},
             'RoomShape' : {'square':  0.60, 'elongated': 0.4},
         })

corridor = Room({
             'Appearance':{'kitchen': 0.01,    'office': 0.01, 'corridor':0.9},
             'RoomShape' :{'square':  0.05, 'elongated': 0.95},
         })
office = Room({
             'Appearance':{'kitchen': 0.30,   'office': 0.69, 'corridor':0.01},
             'RoomShape' :{'square':  0.6, 'elongated': 0.4},
         })

room_categories = {
  'kitchen': kitchen,
  'corridor': corridor,
  'office': office
}


world_distrib = dataset.ClassDistribution( dataset.DiscreteDistribution(room_categories.keys()), room_categories)



known_labels = {}

unlabelled_data = []
labelled_data = []
test_data = []

unconditional_prob = ml.DiscreteProbabilityEstimator(unlabelled_data)
conditional_prob = ml.DiscreteProbabilityEstimator(
  [sample for label, sample in dataset.ExtractLabel(labelled_data)])


def threshold(sample):
  return conditional_prob(sample) / unconditional_prob(sample)


threshold_for_acceptance = sorted(map(threshold, labelled_data))

