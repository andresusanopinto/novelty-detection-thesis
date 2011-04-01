from Sampler import *

def ExtractLabel(samples):
  for sample in samples:
    yield sample[0], sample[1]

