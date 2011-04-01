from Sampler import *

def ExtractLabel(samples):
  for sample in samples:
    yield sample['label'], sample

