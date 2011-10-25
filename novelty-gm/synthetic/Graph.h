#ifndef _GRAPH_H_
#define _GRAPH_H_

#include <algorithm>
#include <boost/ptr_container/ptr_vector.hpp>
#include <map>
#include <string>
#include <vector>

struct VariableType {
	// This vector must be sorted. This allows to use it in a simple
	// way to calculate variable indexs.
	std::vector<std::string> values;
};

struct FactorData {
	std::vector<std::pair<std::string, std::string> > variables;
	std::map<std::vector<std::string>, double> potential;
};

class GraphInformation {
 public:
	std::map<std::string, VariableType> types;
	std::map<std::string, FactorData>   factors;

	VariableType* Add(const std::string &name, const VariableType &type);
	FactorData*   Add(const std::string &name, const FactorData &factor);

	// Returns true if the defined types and factors are consistent.
	// Debug information is produced in the negative case.
	bool CheckConsistency() const;

	bool CheckVarTypeConsistency(const std::string &name,
	                             const VariableType &type) const;

	bool CheckFactorConsistency(const std::string &name,
	                            const FactorData &factor) const;
};


class Variable;  // This class definition is never exposed externaly.
class Factor;    // This class definition is never exposed externaly.
class Query;

class Graph {
 public:
	Graph();
	virtual ~Graph();

	// Creates a new variable of the given type.
	// Returns a reference to the newly created variable.
	// VariableType must exist for the lifetime of this Graph.
	// Graph maintains ownership on the returned variable.
	virtual const Variable* CreateVariable(const VariableType* type);

	// Creates a factor between the given variables.
	// FactorData must exist for the lifetime of this Graph.
	// Graph maintains ownership on the returned factor.
	virtual const Factor* CreateFactor(const FactorData *factorData,
	                           const std::vector<const Variable*> &vars);

    // Appends all factors of this graph to the given output vector.
	virtual void ListFactors(std::vector<const Factor*> *output) const;

 protected:
	boost::ptr_vector<Variable> variables_;
	boost::ptr_vector<Factor> factors_;

 private:
	// DISALLOW COPY AND ASSIGN
	Graph(const Graph &);
	void operator = (const Graph &);
};

#endif  // _GRAPH_H_


