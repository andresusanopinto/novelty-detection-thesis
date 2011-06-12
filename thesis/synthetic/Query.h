// ==================================================================
// ROCS - Toolkit for Robots Comprehending Space
// Copyright (C) 2011  André Susano Pinto
//
// This file is part of ROCS.
//
// ROCS is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3
// of the License, or (at your option) any later version.
//
// ROCS is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with ROCS. If not, see <http://www.gnu.org/licenses/>.
// ==================================================================

/*!
 * \author André Susano Pinto
 * \file Query.h
 */

#ifndef _ROCS_CONCEPT_QUERY_H_
#define _ROCS_CONCEPT_QUERY_H_

#include <boost/scoped_ptr.hpp>
#include <vector>
#include <string>

class Graph;
class Variable;
class QueryInternal;

class Query {
 public:
	// This class does not takes ownership over Graph.
	// Graph and all associated variables have to outlive this instance.
	explicit Query(const Graph *graph);
	~Query();

	// Calculates probability for a given set of variables.
	//
	// Output is the probability for all combinations over the given variables.
	// Output is lexicographic ordered by the value of its variables.
	// This means:
	//   output[0] = P( Var1 = v0, Var2 = v0, ... VarN = v0]
	//   output[1] = P( Var1 = v0, var2 = v0, ... VarN = v1]
	//   ...
	//   output[last] = P( Var1 = vN, Var2 = vN, ... VarN = vN]
	void Marginalize(const std::vector<const Variable*> &variables,
	                 std::vector<double> *output);
    
    void Sample(const std::vector<const Variable*> &variables,
                std::vector<std::string> *output);
 protected:
	const Graph *graph_;
	boost::scoped_ptr<QueryInternal> internal_;

	void BuildInternal();

 private:
	// DISALLOW COPY AND ASSIGN
	Query(const Query&);
	void operator=(const Query&);
};

#endif  // _ROCS_CONCEPT_QUERY_H_
