#ifndef _GRAPH_INTERNAL_H_
#define _GRAPH_INTERNAL_H_

#include <vector>
#include "Graph.h"

class Variable {
 public:
	explicit Variable(const VariableType *type):type_(type) {}

	const VariableType *type_;
};

class Factor {
 public:
	Factor(const FactorData *data, const std::vector<const Variable*> &variables)
			:data_(data), variables_(variables) {}

	const FactorData *data_;
	std::vector<const Variable*> variables_;
};

#endif // _GRAPH_INTERNAL_H
