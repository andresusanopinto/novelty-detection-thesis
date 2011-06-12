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

GraphInformation gi;
const VariableType* roomType;
const VariableType* senseType;
const FactorData* room_room;
const FactorData* room_sense;

const string ROOM_TYPE  = "ROOM";
const string SENSE_TYPE = "SENSE";


string room(int i)  { return "room" + to_string(i); }
string sense(int i) { return "sense" + to_string(i); }

// Initializes GI with a random real distribution.
void gi_init_random_real(int roomCats, int senseCats) {
  // Generate states for variables of type Room
  {
    VariableType roomCat;
    for (int i = 0; i < roomCats; ++i)
      roomCat.values.push_back(room(i));
    sort(roomCat.values.begin(), roomCat.values.end());
    roomType = gi.Add(ROOM_TYPE, roomCat);
  }

  // Generate states for sensed properties
  {
    VariableType senseCat;
    for (int i = 0; i < senseCats; ++i)
      senseCat.values.push_back(sense(i));
    sort(senseCat.values.begin(), senseCat.values.end());
    senseType = gi.Add(SENSE_TYPE, senseCat);
  }

  // Generate factors between Room Categories
  {
    // This factor is symmetric.
    // This is the approach that is taken on the room connectivity
    // otherwise a scheme to figure out on which direction to plug
    // the factor would need to be devised.
    FactorData rr;
    rr.variables.push_back(make_pair(string("room1"), ROOM_TYPE));
    rr.variables.push_back(make_pair(string("room2"), ROOM_TYPE));
    vector<string> index(2);
    for (int i = 0; i < roomCats; ++i)
    for (int j = i; j < roomCats; ++j) {
      double potential = random();
      index[0] = room(i);
      index[1] = room(j);
      rr.potential[index] = potential;
      swap(index[0], index[1]);
      rr.potential[index] = potential;
    }
    room_room = gi.Add("room-room", rr);
  }

  // Generate factors for Room Category and Sensed Property
  {
    FactorData rs;
    rs.variables.push_back(make_pair(string("room"), ROOM_TYPE));
    rs.variables.push_back(make_pair(string("sense"), SENSE_TYPE));
    vector<string> index(2);
    for (int i = 0; i < roomCats; ++i)
    for (int j = 0; j < senseCats; ++j) {
      index[0] = room(i);
      index[1] = sense(j);
      rs.potential[index] = random();
    }
    room_sense = gi.Add("room-sense", rs);
  }
}

struct GraphStructure {
  int rooms;
  int senses;
  set<pair<int,int> > edges;

  void createRandom(int rooms, int senses, int extra_conn) {
    this->rooms = rooms;
    this->senses = senses;
    // Creates a tree
    for (int i = 1; i < rooms; ++i) {
      int other = random() % i;
      edges.insert(make_pair(other, i));
    }
    // Tries to add extra room connectivity
    while (extra_conn--) {
      int a = random() % rooms;
      int b = random() % rooms;
      if (a == b) continue;
      if (a > b) swap(a, b);
      edges.insert(make_pair(a, b));
    }
    // Adds senses (they are randomly split by the rooms)
    for (int i = 0; i < senses; ++i) {
      int r = random() % rooms;
      edges.insert(make_pair(r, rooms+i));
    }
  }
};

class MGraph : public Graph {

public:
  vector<const Variable*> vars;

  MGraph(const GraphStructure &structure,
         const VariableType *room,
         const VariableType *sense,
         const FactorData *rrf,
         const FactorData *rsf) {
    // Build Graph
    for (int i = 0; i < structure.rooms; ++i)
      vars.push_back(CreateVariable(room));
    for (int i = 0; i < structure.senses; ++i)
      vars.push_back(CreateVariable(sense));
  
    typedef pair<int,int> Edge;
    BOOST_FOREACH(const Edge &e, structure.edges) {
      int a = e.first;
      int b = e.second;
      vector<const Variable*> nodes;
      nodes.push_back(vars[a]);
      nodes.push_back(vars[b]);
      CreateFactor(b < structure.rooms? rrf : rsf, nodes);
    }
  }

  void print(const vector<const Variable*> &obs_vars, const vector<string> &obs_vals) {
     map<const Variable*, string> id;
     BOOST_FOREACH(const Variable* var, vars)
       id[var] = "n" + to_string(id.size());

	 vector<const ::Factor*> factors;
     ListFactors(&factors);
     BOOST_FOREACH(const ::Factor* fac, factors)
       BOOST_FOREACH(const Variable* var, fac->variables_)
         if (id.count(var) == 0)
           id[var] = "n" + to_string(id.size());

     printf("graph sample {\n");
     printf(" node [shape=circle];\n");
     BOOST_FOREACH(const Variable* var, vars)
       printf("  %s;\n", id[var].c_str());

     for (size_t i = 0; i < obs_vars.size(); ++i)
       printf("  %s[label=%s];\n", id[obs_vars[i]].c_str(), obs_vals[i].c_str());

     int nf = 1;
     printf(" node [shape=square];\n");
     BOOST_FOREACH(const ::Factor* fac, factors) {
       string fid = "f" + to_string(nf++);
       printf("  %s;\n", fid.c_str());
       BOOST_FOREACH(const Variable* var, fac->variables_)
         printf("  %s -- %s;\n", fid.c_str(), id[var].c_str());
     }
     printf("}\n");
  }

};




int main() {
  gi_init_random_real(3, 6);
  assert(gi.CheckConsistency());

  GraphStructure s;
  s.createRandom(3, 10, 1);
  MGraph g(s, roomType, senseType, room_room, room_sense);

  Query q(&g);
  vector<string> output;
  q.Sample(g.vars, &output);
  g.print(g.vars, output);

  return 0;
}

