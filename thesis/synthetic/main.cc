/**
 * Novelty Detection Scripts
 *
 * Copyright 2011: André Susano Pinto
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */
#include "Graph.h"
#include "Graph-internal.h"
#include "Query.h"
#include "util.h"

#include <cassert>
#include <cstdio>
#include <set>
#include <algorithm>
using namespace std;

#include <boost/foreach.hpp>
#include <boost/scoped_ptr.hpp>
using namespace boost;

#include <dai/factorgraph.h>
#include <dai/gibbs.h>
#include <dai/properties.h>
using namespace dai;

void example_single_factor(int room_types = 10, int property_types = 15,
                           int known_rooms = 5);

int main() {
  example_single_factor();
  return 0;
}

