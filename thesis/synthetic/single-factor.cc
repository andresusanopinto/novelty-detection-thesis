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
#include <fstream>
#include <algorithm>
#include <cmath>
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

void FilterVariable(const set<string> &allowed, VariableType *type) {
  type->values.clear();
  type->values.reserve(allowed.size());
  type->values.insert(type->values.end(), allowed.begin(), allowed.end());
}


void FilterFactor(int varid, const string &vartype, const VariableType &var, FactorData *data) {
  (*data).variables[varid].second = vartype;

  map<vector<string>, double> potential;
  typedef pair<vector<string>,double> iter;
  BOOST_FOREACH(const iter &it, data->potential)
    if (find(var.values.begin(), var.values.end(), it.first[varid]) != var.values.end())
      potential.insert(it);
  potential.swap(data->potential);
}


}

size_t room_types = 7;
size_t n_known_rooms = 5;
size_t property_types = 8;
int C = 1;

set<string> known_rooms;
set<string> novel_rooms;


GraphInformation gi;
// Real World
VariableType *type_real_room = NULL;
VariableType *type_real_prop = NULL;
FactorData *factor_rroom_rprop = NULL;

// Filtered Real Worlds
VariableType *type_real_kroom = NULL;
VariableType *type_real_nroom = NULL;
FactorData *factor_rkroom_rprop = NULL;
FactorData *factor_rnroom_rprop = NULL;

// Conditional Learning
VariableType *type_known_room = NULL;
FactorData *factor_kroom_kprop = NULL;

// Unconditional Learning
VariableType *type_any_room = NULL;
FactorData *factor_aroom_kprop = NULL;

void generate_real_distribution_vars_and_factors() {
  for (size_t i = 0; i < n_known_rooms; ++i)
    known_rooms.insert(room(i));
  for (size_t i = n_known_rooms; i < room_types; ++i)
    novel_rooms.insert(room(i));

  // Real room variable.
  {
    VariableType &type = *(type_real_room = gi.Add("real_room", VariableType()));
    type.values.insert(type.values.end(), known_rooms.begin(), known_rooms.end());
    type.values.insert(type.values.end(), novel_rooms.begin(), novel_rooms.end());
    sort(type.values.begin(), type.values.end());
  }
  // Real property variable.
  {
    VariableType &type = *(type_real_prop = gi.Add("real_prop", VariableType()));
    for (int i = 0; i < property_types; ++i)
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
      factor.potential[vector_of(room, prop)] = 0.1;
    BOOST_FOREACH(const string &room, type_real_room->values)
      factor.potential[vector_of(room, type_real_prop->values[random()%property_types])] = 0.3 + drand48();
  }

  // Make filtered versions of known and novel rooms to use to generate samples.
  type_real_kroom = gi.Add("known_room", *type_real_room);
  FilterVariable(known_rooms, type_real_kroom);

  type_real_nroom = gi.Add("novel_room", *type_real_room);
  FilterVariable(novel_rooms, type_real_nroom);

  factor_rkroom_rprop = gi.Add("f_real(room, property|room in known rooms)", *factor_rroom_rprop);
  FilterFactor(0, "known_room", *type_real_kroom, factor_rkroom_rprop);

  factor_rnroom_rprop = gi.Add("f_real(room, property|room in novel rooms)", *factor_rroom_rprop);
  FilterFactor(0, "novel_room", *type_real_nroom, factor_rnroom_rprop);
}

void generate_samples(vector<vector<string> > *output, VariableType *room, FactorData *factor, int size) {
  BOOST_FOREACH(vector<string> &sample, *output) {
    GraphStructure s;
    int n_properties = size;
    if (n_properties == -1)
      n_properties = 1 + (random() % 17);

    s.createRandom(1, n_properties, 0);
    MGraph g(s, room, type_real_prop, NULL, factor);
   
    Query q(&g);
    q.Sample(g.vars, &sample);
  }
}

void generate_unconditional_samples(vector<vector<string> > *output, int size = -1) {
  generate_samples(output, type_real_room, factor_rroom_rprop, size);
}
void generate_conditional_ksamples(vector<vector<string> > *output, int size = -1) {
  generate_samples(output, type_real_kroom, factor_rkroom_rprop, size);
}
void generate_conditional_nsamples(vector<vector<string> > *output, int size = -1) {
  generate_samples(output, type_real_nroom, factor_rnroom_rprop, size);
}


void learn_known_room_distribution(const vector<vector<string> > samples) {
  type_known_room = type_real_kroom;

  // Learn factor(room, property | room in known_rooms) from labelled data.
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


void learn_any_room_distribution(const vector<vector<string> > &samples) {
  // Create variable type for any room states.
  type_any_room = gi.Add("any_room", VariableType());
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
    
    map<vector<string>,double>::iterator iter;
    for (iter = factor.potential.begin(); iter != factor.potential.end(); ++iter) {
//      iter->second *= exp(-4.86222);
//      iter->second *= exp(0.399);
    }
  }

}

void compare_real_normalization_factors() {
  for (size_t i = 1; i < 100; ++i) {
    GraphStructure s;
    int n_properties = i; //1 + (random() % 15);
    s.createRandom(1, n_properties, 0);
    
    MGraph real_g(s, type_real_room, type_real_prop, NULL, factor_rroom_rprop);
    MGraph any_g (s, type_any_room,  type_real_prop, NULL, factor_aroom_kprop);

    Query rq(&real_g);
    Query aq(&any_g);

    // Absolute difference:
    vector<const Variable*> var;
    vector<string> var_clamp;

    double abs_rlogz = rq.LogZ(var, var_clamp);
    double abs_alogz = aq.LogZ(var, var_clamp);
    cout << n_properties << ": total_abs_diff = " << exp(abs_rlogz - abs_alogz) << endl;
    cout << n_properties << ": total_rel_diff = " << (abs_rlogz - abs_alogz)/n_properties << endl;
  }
}

double junk() { return 0.1 + drand48()/5; }

void compare_performance(const vector<vector<string> > &samples) {
  vector<pair<pair<int,double>,bool> > result_fix;
  vector<pair<pair<int,double>,bool> > result_dyn;
  vector<pair<pair<int,double>,bool> > result_opt;

  BOOST_FOREACH(const vector<string> &sample, samples) {
    int n_properties = sample.size()-1;
    
    GraphStructure s;
    s.createRandom(1, n_properties, 0);
    MGraph known_g(s, type_known_room, type_real_prop, NULL, factor_kroom_kprop);
    MGraph any_g  (s, type_any_room,   type_real_prop, NULL, factor_aroom_kprop);
    MGraph real_g (s, type_real_room,  type_real_prop, NULL, factor_rroom_rprop);

    Query kq(&known_g);
    Query aq(&any_g);
    Query rq(&real_g);

    vector<const Variable*> k_prop(known_g.vars.begin()+1, known_g.vars.end());
    vector<const Variable*> a_prop(any_g.vars.begin()+1,   any_g.vars.end());
    vector<const Variable*> r_prop(real_g.vars.begin()+1,  real_g.vars.end());
    vector<string> clamp(sample.begin()+1, sample.end());

    double klogZ = kq.LogZ(k_prop, clamp);
    double alogZ = aq.LogZ(a_prop, clamp);
    
    // log(2) + log(\phi_k(x)) < k_i log(s_i) + log(\phi_a(x))
    // log(s_i) > (log(2) + log(\phi_k(x)) - log(\phi_a(x))) / k_i
    double dyn_threshold = (klogZ - alogZ)/n_properties;
    result_dyn.push_back(make_pair(make_pair(n_properties, exp(dyn_threshold)), known_rooms.count(sample[0]) == 1));

    // Assuming a constant probability of drawing a novel sample.
    vector<const Variable*> no_prop;
    vector<string> no_clamp;
    double t_klogZ = kq.LogZ(no_prop, no_clamp);
    double t_alogZ = aq.LogZ(no_prop, no_clamp);
    double fix_threshold = (klogZ - t_klogZ) - (alogZ - t_alogZ);
    result_fix.push_back(make_pair(make_pair(n_properties, exp(fix_threshold)), known_rooms.count(sample[0]) == 1));
    //result_dyn.push_back(make_pair(make_pair(n_properties, fix_threshold/n_properties), known_rooms.count(sample[0]) == 1));

    // Real distribution
    double notnovel_p = 0.0;
    double novel_p    = 0.0;
    double r_logZ = rq.LogZ(r_prop, clamp);
    BOOST_FOREACH(const string room, type_real_room->values) {
      vector<string> aclamp;
      aclamp.push_back(room);
      aclamp.insert(aclamp.end(), clamp.begin(), clamp.end());
      double prob = exp( rq.LogZ(real_g.vars, aclamp) - r_logZ );
      if (known_rooms.count(room)) notnovel_p += prob;
      else novel_p += prob;
    }
    result_opt.push_back(make_pair(make_pair(n_properties,  notnovel_p), known_rooms.count(sample[0]) == 1));
  }
  sort(result_dyn.begin(), result_dyn.end());
  sort(result_fix.begin(), result_fix.end());

  {
    ofstream os_known("result_dyn_threshold_known.data");
    ofstream os_novel("result_dyn_threshold_novel.data");
    for (size_t i = 0; i < result_dyn.size(); ++i)
      if (result_dyn[i].second)
        os_known << fixed << result_dyn[i].first.first + junk() << " " << fixed << result_dyn[i].first.second << endl;
      else
        os_novel << fixed << result_dyn[i].first.first - junk() << " " << fixed << result_dyn[i].first.second << endl;
  }

  {
    ofstream os_known("result_fix_threshold_known.data");
    ofstream os_novel("result_fix_threshold_novel.data");
    for (size_t i = 0; i < result_fix.size(); ++i)
      if (result_fix[i].second)
        os_known << fixed << result_fix[i].first.first + junk() << " " << fixed << result_fix[i].first.second << endl;
      else
        os_novel << fixed << result_fix[i].first.first - junk() << " " << fixed << result_fix[i].first.second << endl;
  }

  {
    ofstream os_known("result_opt_threshold_known.data");
    ofstream os_novel("result_opt_threshold_novel.data");
    for (size_t i = 0; i < result_opt.size(); ++i)
      if (result_opt[i].second)
        os_known << fixed << result_opt[i].first.first + junk() << " " << fixed << result_opt[i].first.second << endl;
      else
        os_novel << fixed << result_opt[i].first.first - junk() << " " << fixed << result_opt[i].first.second << endl;
  }

}

void example_single_factor() {
  generate_real_distribution_vars_and_factors();

  vector<vector<string> > conditional_samples(100);
  generate_conditional_ksamples(&conditional_samples);
  learn_known_room_distribution(conditional_samples);
 
  vector<vector<string> > unconditional_samples(1000);
  generate_unconditional_samples(&unconditional_samples);
  learn_any_room_distribution(unconditional_samples);

  assert(gi.CheckConsistency());

//  compare_real_normalization_factors();

  vector<vector<string> > test_data;
  for (size_t i = 1; i < 18; ++i) {
    {
      vector<vector<string> > data(50);
      generate_conditional_ksamples(&data, i);
      test_data.insert(test_data.end(), data.begin(), data.end());
    }
    {
      vector<vector<string> > data(50);
      generate_conditional_nsamples(&data, i);
      test_data.insert(test_data.end(), data.begin(), data.end());
    }
  }
  compare_performance(test_data);
}
  



