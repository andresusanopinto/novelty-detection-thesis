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

int room_types = 10;
int n_known_rooms = 5;
int property_types = 8;
int C = 1;

set<string> known_rooms;


GraphInformation gi;
VariableType *type_real_room = NULL;
VariableType *type_real_prop = NULL;
FactorData *factor_rroom_rprop = NULL;

VariableType *type_known_room = NULL;
FactorData *factor_kroom_kprop = NULL;

VariableType *type_any_room = NULL;
FactorData *factor_aroom_kprop = NULL;

void generate_real_distribution_vars_and_factors() {
  for (size_t i = 0; i < n_known_rooms; ++i)
    known_rooms.insert(room(i));

  // Real room variable.
  {
    VariableType &type = *(type_real_room = gi.Add("real_room", VariableType()));
    for (int i = 0; i < room_types; ++i)
      type.values.push_back(room(i));
    sort(type.values.begin(), type.values.end());
  }

  // Real property variable.
  {
    VariableType &type = *(type_real_prop = gi.Add("real_prop", VariableType()));
    for (int i = 0; i < room_types; ++i)
      type.values.push_back(prop(i));
    sort(type.values.begin(), type.values.end());
  }
  
  // Real factor(room, property).
  {
    FactorData &factor = *(factor_rroom_rprop = gi.Add("f(room, property)", FactorData()));
    factor.variables.push_back(make_pair("room", "real_room"));
    factor.variables.push_back(make_pair("prop", "real_prop"));
    BOOST_FOREACH(const string &room, type_real_room->values)
    BOOST_FOREACH(const string &prop, type_real_prop->values)
      factor.potential[vector_of(room, prop)] = drand48();
  }
}

void generate_conditional_samples(vector<vector<string> > *output) {
  for (size_t i = 0; i < output->size();) {
    GraphStructure s;
    int n_properties = 1 + (random() % 15);
    s.createRandom(1, n_properties, 0);
    MGraph g(s, type_real_room, type_real_prop, NULL, factor_rroom_rprop);
   
    Query q(&g);
    vector<string> sample;
    q.Sample(g.vars, &sample);
    if (known_rooms.count(sample[0]))
      (*output)[i++].swap(sample);
  }
}

void learn_known_room_distribution(const vector<vector<string> > samples) {
  // Create variable type for known room states.
  {
    VariableType &type = *(type_known_room = gi.Add("known_room", VariableType()));
    type.values.insert(type.values.end(), known_rooms.begin(), known_rooms.end());
    sort(type.values.begin(), type.values.end());
  }

  // Learn factor(room, property | room in known_rooms) from labelled data.
  {
    FactorData &factor = *(factor_kroom_kprop = gi.Add("f(room, prop|room in known rooms)", FactorData()));
    factor.variables.push_back(make_pair("room", "known_room"));
    factor.variables.push_back(make_pair("prop", "real_prop"));
    BOOST_FOREACH(const vector<string> &sample, samples) {
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
  }
}

void generate_unconditional_samples(vector<vector<string> > *output) {
  BOOST_FOREACH(vector<string> &sample, *output) {
    GraphStructure s;
    int n_properties = 1 + (random() % 15);
    s.createRandom(1, n_properties, 0);
    MGraph g(s, type_real_room, type_real_prop, NULL, factor_rroom_rprop);
   
    Query q(&g);
    q.Sample(g.vars, &sample);
  }
}

void learn_any_room_distribution(const vector<vector<string> > &samples) {
  // Create variable type for any room states.
  type_any_room->values.push_back("any");

  // Learn factor(room, property | room is any room) form unlabelled data.
  {
    FactorData &factor = *(factor_aroom_kprop = gi.Add("f(room, prop|room is any room)", FactorData()));
    factor.variables.push_back(make_pair("room", "any_room"));
    factor.variables.push_back(make_pair("prop", "real_prop"));
    BOOST_FOREACH(const vector<string> &sample, samples)
      for (size_t f = 1; f < sample.size(); ++f)
        factor.potential[vector_of("any", sample[f])]++;

    BOOST_FOREACH(const string &prop, type_real_prop->values)
      factor.potential[vector_of("any", prop)] += C;
  }
}

void compare_real_normalization_factors() {
  int n = 100;
  while (n--) {
    GraphStructure s;
    int n_properties = 1 + (random() % 15);
    s.createRandom(1, n_properties, 0);
    
    MGraph real_g(s, type_real_room, type_real_prop, NULL, factor_rroom_rprop);
    MGraph any_g (s, type_any_room,  type_real_prop, NULL, factor_aroom_kprop);
   
  }
}

void example_single_factor() {
  generate_real_distribution_vars_and_factors();

  vector<vector<string> > conditional_samples(100);
  generate_conditional_samples(&conditional_samples);
  learn_known_room_distribution(conditional_samples);
 
  vector<vector<string> > unconditional_samples(100);
  generate_unconditional_samples(&unconditional_samples);
  learn_any_room_distribution(unconditional_samples);

  assert(gi.CheckConsistency());

  compare_real_normalization_factors();
}
  



