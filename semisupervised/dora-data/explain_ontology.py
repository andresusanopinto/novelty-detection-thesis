import script
import explain
from ontology import features, rooms

out = explain.ExplainDistributions(sorted(features.items()),
                                   sorted(rooms.items()))

script.WriteFile(script.option('OUTPUT'), out)
