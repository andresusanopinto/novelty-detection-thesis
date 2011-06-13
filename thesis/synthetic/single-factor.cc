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
#include <iostream>
#include <algorithm>
using namespace std;

#include <boost/foreach.hpp>
#include <boost/scoped_ptr.hpp>
using namespace boost;

/**
 * This experiment tries to approach a graph where variable
 * a is only connected with a single type of factor \phi.
 * 
 */
namespace {
string room(int i) { return "r" + to_string(i); }
string prop(int i) { return "p" + to_string(i); }

vector<string> vector_of(const string &a, const string &b) {
  vector<string> t(2);
  t[0] = a, t[1] = b;
  return t;
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

}

void example_single_factor(int room_types, int property_types,
                           int n_known_rooms) {
  int C = 1;
  GraphInformation gi;
  set<string> known_rooms;

  for (size_t i = 0; i < n_known_rooms; ++i)
    known_rooms.insert(room(i));

  // Real room variable.
  VariableType *type_real_room = gi.Add("real_room", VariableType());
  {
    VariableType &type = *type_real_room;
    for (int i = 0; i < room_types; ++i)
      type.values.push_back(room(i));
    sort(type.values.begin(), type.values.end());
  }

  // Real property variable.
  VariableType *type_real_prop = gi.Add("real_prop", VariableType());
  {
    VariableType &type = *type_real_prop;
    for (int i = 0; i < room_types; ++i)
      type.values.push_back(prop(i));
    sort(type.values.begin(), type.values.end());
  }
  
  // Real factor(room, property).
  FactorData *factor_rroom_rprop = gi.Add("f(room, property)", FactorData());
  {
    FactorData &factor = *factor_rroom_rprop;
    factor.variables.push_back(make_pair("room", "real_room"));
    factor.variables.push_back(make_pair("prop", "real_prop"));
    BOOST_FOREACH(const string &room, type_real_room->values)
    BOOST_FOREACH(const string &prop, type_real_prop->values)
      factor.potential[vector_of(room, prop)] = drand48();
  }

  assert(type_real_room);
  assert(type_real_prop);
  assert(factor_rroom_rprop);
  assert(gi.CheckConsistency());

  // Generate samples where room is known.
  vector< vector<string> > conditional_samples(100);
  for (size_t i = 0; i < conditional_samples.size();) {
    GraphStructure s;
    int n_properties = 1 + (random() % 15);
    s.createRandom(1, n_properties, 0);
    MGraph g(s, type_real_room, type_real_prop, NULL, factor_rroom_rprop);
   
    Query q(&g);
    q.Sample(g.vars, &conditional_samples[i]);
    if (known_rooms.count(conditional_samples[i][0])) ++i;
    else conditional_samples[i].clear();
  }

  // Create variable type for known room states.
  VariableType *type_known_room = gi.Add("known_room", VariableType());
  {
    VariableType &type = *type_known_room;
    type.values.insert(type.values.end(), known_rooms.begin(), known_rooms.end());
    sort(type.values.begin(), type.values.end());
  }

  // Learn factor(room, property | room in known_rooms) from labelled data.
  FactorData *factor_kroom_kprop = gi.Add("f(room, prop|room in known rooms)", FactorData());
  {
    FactorData &factor = *factor_kroom_kprop;
    factor.variables.push_back(make_pair("room", "known_room"));
    factor.variables.push_back(make_pair("prop", "real_prop"));
    BOOST_FOREACH(const vector<string> &sample, conditional_samples) {
      const string room = sample[0];
      for (size_t f = 1; f < sample.size(); ++f) {
        const string prop = sample[f];
        factor.potential[vector_of(room, prop)]++;
      }
    }
   
    // Added smoothing factor.
    BOOST_FOREACH(const string &room, known_rooms)
    BOOST_FOREACH(const string &prop, type_real_prop->values)
      factor.potential[vector_of(room, prop)]++;

    factor_kroom_kprop = gi.Add("f(room, prop|room in known_rooms)", factor);
  }
  
  // Generate unconditional samples.
  vector< vector<string> > unconditional_samples(1000);
  BOOST_FOREACH(vector<string> &sample, unconditional_samples) {
    GraphStructure s;
    int n_properties = 1 + (random() % 15);
    s.createRandom(1, n_properties, 0);
    MGraph g(s, type_real_room, type_real_prop, NULL, factor_rroom_rprop);
   
    Query q(&g);
    q.Sample(g.vars, &sample);
  }

  // Create variable type for any room states.
  VariableType *type_any_room = gi.Add("any_room", VariableType());
  type_any_room->values.push_back("any");

  // Learn factor(room, property | room is any room) form unlabelled data.
  FactorData *factor_aroom_kprop = gi.Add("f(room, prop|room is any room)", FactorData());
  {
    FactorData &factor = *factor_aroom_kprop;
    factor.variables.push_back(make_pair("room", "any_room"));
    factor.variables.push_back(make_pair("prop", "real_prop"));
    BOOST_FOREACH(vector<string> &sample, unconditional_samples)
      for (size_t f = 1; f < sample.size(); ++f)
        factor.potential[vector_of("any", sample[f])]++;

    BOOST_FOREACH(const string &prop, type_real_prop->values)
      factor.potential[vector_of("any", prop)] += C;
  }
  gi.CheckConsistency();
}
  
/*
  // Try to approach unconditional distribution where room
  // is a single state variable.
  VariableType type_uroom;
  type_uroom.values.push_back("any_room");
  
  // Learn unconditional room-property factor from unlabelled data.
  FactorData factor_uroom_kprop;
  {
    FactorData &factor = factor_uroom_kprop;
    factor.variables.push_back(make_pair("room", "any_room"));
    factor.variables.push_back(make_pair("prop", "known_prop_cat"));
    for (size_t i = 0; i < unla
  int counter[known_rooms][sense_categories];
  // Init with a uniform distribution.
  for (size_t i = 0; i < known_rooms; ++i)
    for (size_t j = 0; j < sense_categories; ++j)
      counter[i][j] += C;
  // Accumulate labelled information.
    int room_label = conditional_samples[i][0];
      counter[make_pair(i, conditional_samples[i][f])]++;
  }


}
*/



