from Classifier import *
from util import Histogram

def DiscreteProbabilityEstimator(samples, input_state_size = 0):
  counter = Histogram(samples)
  total = input_state_size + sum(map(lambda x: x[1], counter.items()), 0)
  def Density(sample):
    if sample in counter:
      return (counter[sample]+1.0) / total 
    else:
      return 1.0 / total
  return Density
