# -*- coding: utf-8 -*-
#
# Novelty Detection Scripts
#
# Copyright 2011: André Susano Pinto
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
import numpy as np
import pylab as pl
import scipy.special as special
import math
import random


def model(m):
  while True:
    yield random.random() < m

def sample(m, n):
  for x in range(n):
    yield next(m)

def count(data):
  [positive, negative, total] = sum(map(lambda x: np.array([x == True, x == False, 1]), data))
  return [positive, negative, total]

def beta(a, b):
  return special.beta(a, b)

dp_fac = {}
def fac(n):
  return math.factorial(n)
  if n in dp_fac: return dp_fac[n]
  dp_fac[n] = math.factorial(n)
  return dp_fac[n]

def comb(n, k):
  return fac(n)/fac(k)/fac(n-k);

def train(traindata):
  [t_pos, t_neg, t_size] = count(traindata)
  factor = comb(t_size, t_pos)
  def novelty(sample):
    """Measure probability the sample cames from the same distirbution as the train data."""
    [s_pos, s_neg, s_size] = count(sample)
    return np.float64(factor)*np.float64(comb(s_size, s_pos))*beta(t_pos+s_pos+1, (t_size-t_pos)+(s_size-s_pos)+1)
  
  def log_novelty(sample):
    [s_pos, s_neg, s_size] = count(sample)
#print("%d-%d - %d-%d" % (t_pos, t_neg, s_pos, s_neg))
    fac = math.factorial
    num = fac(t_size)+fac(s_size)+fac(t_pos+s_pos)+fac(t_neg+s_neg)
    den = fac(t_pos)+fac(t_neg)+fac(s_pos)+fac(s_neg)+fac(t_size+s_size)
    return num-den
  return novelty

def plot_model_prob(samples, realmodel=None, quality=1000.0):
  pl.xlabel('Model parameter (m)')
  pl.ylabel('Output Probability P(x|m)')
  pl.title('Model probability for a set of samples extracted from m=%f.' % realmodel)
  pl.xlim([-0.05,1.05])
  pl.ylim([-0.05,1.05])
  if realmodel: pl.errorbar(realmodel, 0.25, 0.25, 0.0)

  all_samples = []
  for sample in samples: all_samples += sample
  print len(all_samples)
  samples.append(all_samples)

  x = np.arange(0, 1+1/quality, 1/quality)
  ya = x*0

  def plot_sample(i, sample, plot=True, xf = 1.0):
    [pos, neg, total] = count(sample)
    factor = comb(total, pos)
    y = xf * factor * (x**pos) * ((1-x)**neg)
    print("Sample %s: %d positives in %d => prob sum to: %f" % (i, pos, total, sum(y/(quality+1))))
    if plot:
      pl.plot(x, y, label="P(X=%s)"%i)
    return y

  for (i, sample) in enumerate(samples):
    ya += plot_sample(i, sample)

  plot_sample('all_join', all_samples, xf = len(samples))

  pl.plot(x, ya, color='red', label='Sum of the %d samples' % len(samples))
  pl.legend(loc = "upper left")
  pl.show()
  

def test():
    traindata = sample(model(0.5), 10000)
    novelty = train(traindata)
    testdata = sample(model(0.5), 100)
    print novelty(testdata)

def test1(rmodel=0.75, samples=5, samplesize=5):
  """Draws N samples of a given size from a given model.
  And plots the probability of P(Si|m) for each of those samples.
  Plots P(x=S1+S2+S3+S4|m) and avg(P(si|m)).

  As possible to see experimentaly the model should be approximated with: P(x=S1...SN|m)."""

  traindata = [list(sample(model(rmodel), samplesize)) for x in range(samples)]
  plot_model_prob(traindata, realmodel=rmodel)

def test2(rmodel=0.95, traindata=None, trainsamples=500, testsamplesize=50, quality=50.0, precision=100):
  """Plots probability that a sample from a given model is considered to come from the
  same model as a given training data."""
  if traindata == None: traindata = sample(model(rmodel), trainsamples)
  psm = train(traindata)
  x = np.arange(0, 1+1/quality, 1/quality)
  y = x*0
  boxdata = [[] for i in range(len(x))]
  for (i, m) in enumerate(x):
    md = model(m)
    boxdata[i] = list(psm( sample(md, testsamplesize) ) for x in range(precision))
    nv = sum(boxdata[i])/precision
    y[i] = nv
    print(m,nv)
  print("Area = %f", sum(y)/quality)
  
  pl.xlabel('Model parameter (m)')
  pl.ylabel('P(traindata,sample from m of size %d)' % testsamplesize)
  pl.title('Probability a sample from a given model comes from the same model as the training data.'
           ' Training data is a sample of size=%d from m=%f' % (trainsamples, rmodel))
  pl.xlim([-0.05,1.05])
  for i in range(len(x)):
    boxdata[i] = sorted(boxdata[i])
  for perc in [0.05, 0.25, 0.5, 0.75, 0.95]:
    p5  = pl.plot(x, list(x[int(perc*precision)] for x in boxdata), label="Percentil %f"%perc)
#p5 = pl.plot(x, boxdata[:][int(precision*0.05)])
  pl.plot(x, y)
  pl.legend()

  pl.show()
    


test2()
