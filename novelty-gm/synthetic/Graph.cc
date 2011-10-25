#include <boost/foreach.hpp>
#include <cstdio>
#include "Graph-internal.h"
using namespace std;

#define ROCS_DEBUG_STRINGIFY(x) #x
#define ROCS_DEBUG_TO_STRING(x) ROCS_DEBUG_STRINGIFY(x)

#define ROCS_DEBUG(...) { \
  printf("[" __FILE__ ":" ROCS_DEBUG_TO_STRING(__LINE__) "] " __VA_ARGS__); \
  printf("\n"); \
}

#define rocsDebug2(...) ROCS_DEBUG(__VA_ARGS__)
#define rocsDebug1(...) ROCS_DEBUG(__VA_ARGS__)

namespace {

// Unfortunaly is_sorted is a SGI extension.
// Therefore we need to define it.
template<typename T>
bool is_sorted(T begin, T end)
{
	if (begin == end)
		return true;

	T next = begin;
	for (++next; next != end; begin = next, ++next)
		if(*next < *begin)
			return false;
	return true;
}

// Builds a vector with the variable types of the given FactorData.
// Returns false in case not all variables types are defined.
bool GetVariableTypes(const FactorData &data,
                      const map<string, VariableType> &known_types,
                      vector<const VariableType*> *vartypes)
{
	typedef pair<string, string> PSS;
	BOOST_FOREACH(const PSS &v, data.variables)
	{
		map<string, VariableType>::const_iterator it = known_types.find(v.second);
		if (it == known_types.end())
		{
			rocsDebug2("Invalid FactorData: Unknown variable type '%s'",
					v.second.c_str());
			return false;
		}
		vartypes->push_back(&it->second);
	}
	return true;
}
}  // end namespace anonymous

FactorData* GraphInformation::Add(const string &name, const FactorData &factor)
{
	rocsDebug2("Add factor type: '%s'", name.c_str());
	if (factors.insert(make_pair(name, factor)).second == false)
		rocsDebug1("Dropped factor: there is already a factor with that name '%s'",
				name.c_str());
    return &factors[name];
}

VariableType* GraphInformation::Add(const string &name, const VariableType &type)
{
	rocsDebug2("Add variable type: '%s'", name.c_str());
	if (types.insert(make_pair(name, type)).second == false)
		rocsDebug1("Dropped type: there is already a type with that name '%s'",
				name.c_str());
    return &types[name];
}

bool GraphInformation::CheckVarTypeConsistency(const string &name,
                                               const VariableType &type) const
{
	bool consistent = true;
	if (type.values.size() == 0)
	{
		rocsDebug2("VariableType '%s' has no defined possible values.", name.c_str());
		consistent = false;
	}

	if (!is_sorted(type.values.begin(), type.values.end()))
	{
		rocsDebug2("VariableType '%s' values are not sorted.", name.c_str());
		consistent = false;
	}
	return consistent;
}

bool GraphInformation::CheckFactorConsistency(const string &name,
                                              const FactorData &factor) const
{
	if (factor.variables.size() == 0)
	{
		rocsDebug2("FactorData '%s' does not has any variable.", name.c_str());
		return false;
	}

	vector<const VariableType*> vartypes;
	if (!GetVariableTypes(factor, types, &vartypes))
	{
		rocsDebug2("FactorData '%s' has undefined variable types.", name.c_str());
		return false;
	}

	// Variables types are correct, check potentials consistency
	bool consistent = true;

	typedef pair<vector<string>, double> PotentialIt;
	BOOST_FOREACH(const PotentialIt &p, factor.potential)
	{
		// Non-negative potentials only.
		if (p.second < 0)
		{
			rocsDebug2("FactorData '%s': found negative potential.", name.c_str());
			consistent = false;
		}

		// Check potential index.
		if (p.first.size() != vartypes.size())
		{
			rocsDebug2("FactorData '%s': found potential that does not agrees in"
			           " number of variables", name.c_str());
			consistent = false;
			continue;
		}

		for (size_t i = 0; i != vartypes.size(); ++i)
		{
			// Considering we have the indexes sorted and the variables sorted this
			// is inefficient. Though it does not matters since this code is mainly
			// for helping debugging.
			if (find(vartypes[i]->values.begin(), vartypes[i]->values.end(),
					p.first[i]) == vartypes[i]->values.end())
			{
				rocsDebug2("FactorData '%s': potential with incorrect value"
						"'%s' for variable %s.", name.c_str(),
						p.first[i].c_str(), factor.variables[i].first.c_str());
				consistent = false;
			}
		}
	}

	// Check if all potentials were defined.
	size_t total_size = 1;
	BOOST_FOREACH(const VariableType *type, vartypes)
		total_size *= type->values.size();

	if (total_size != factor.potential.size())
	{
		rocsDebug2("FactorData '%s': not all potentials are defined.", name.c_str());
		consistent = false;
	}

	return consistent;
}

bool GraphInformation::CheckConsistency() const
{
	bool consistent = true;

	// Check VariableType consistency
	typedef pair<string, VariableType> VarTypeIt;
	BOOST_FOREACH(const VarTypeIt &vartype, types)
		consistent &= CheckVarTypeConsistency(vartype.first, vartype.second);

	// Check FactorData consistency
	typedef pair<string, FactorData> FactorDataIt;
	BOOST_FOREACH(const FactorDataIt &factor, factors)
		consistent &= CheckFactorConsistency(factor.first, factor.second);

	return consistent;
}

Graph::Graph()
{}

Graph::~Graph()
{}

const Variable* Graph::CreateVariable(const VariableType *type)
{
	Variable *variable = new Variable(type);
	variables_.push_back(variable);
	return variable;
}

const Factor* Graph::CreateFactor(const FactorData *data,
                           const vector<const Variable*> &variables)
{
	Factor* factor = new Factor(data, variables);
	factors_.push_back(factor);
	return factor;
}

void Graph::ListFactors(vector<const Factor*> *output) const {
	output->reserve(output->size() + factors_.size());
	BOOST_FOREACH(const Factor &f, factors_)
	  output->push_back(&f);
}
