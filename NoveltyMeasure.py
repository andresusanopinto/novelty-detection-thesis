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
  [positive, negative, total] = sum(map(lambda x: np.array([x == True, x == False, 1]), data), np.array([0, 0, 0]))
  return [positive, negative, total]


dp_fac = {}
def fac(n):
  return math.factorial(n)

def beta(a, b):
  return special.beta(a, b)

dp_log_fac = {}
dp_log_fac[0] = math.log(1)
for i in range(1, 10000):
  dp_log_fac[i] = dp_log_fac[i-1] + math.log(i)

def log_fac(n):
  return dp_log_fac[n]

def log_beta(a, b):
  return log_fac(a-1)+log_fac(b-1)-log_fac(a+b-1)

def comb(n, k):
  return fac(n)/fac(k)/fac(n-k);

def train(traindata):
  [t_pos, t_neg, t_size] = count(traindata)
  factor = comb(t_size, t_pos)
  
  def novelty2(sample):
    """This one has normalization factors on it."""
    [s_pos, s_neg, s_size] = count(sample)
    return beta(t_pos+s_pos+1, t_neg+s_neg+1)/beta(t_pos+1, t_neg+1)/beta(s_pos+1, s_neg+1)

  def log_novelty2(sample):
    [s_pos, s_neg, s_size] = count(sample)
    return log_beta(t_pos+s_pos+1, t_neg+s_neg+1) - log_beta(t_pos+1, t_neg+1) -log_beta(s_pos+1, s_neg+1)

  def novelty3(sample):
    return math.exp(log_novelty2(sample))
  
  def deb_novelty(sample):
    sample = list(sample)
    [s_pos, s_neg, s_size] = count(sample)
    novel2 = novelty2(sample)
    novel3 = novelty3(sample)
    diff = abs(novel3-novel2)
    if diff > 0.000001:
      print diff
    return novel3

  return novelty3

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

def test1_1(rmodel=0.75, numsamples=1, samplesize=10, quality=100.0):
  """Plots P(m | x)."""
  for s in range(numsamples):
    [sp, sn, ss] = count(list(sample(model(rmodel), samplesize)))
    x = np.arange(0, 1+1/quality, 1/quality)
    y = x*0
    denom = beta(sp+1, sn+1)
    for i in range(quality): y[i] = (x[i]**sp)*((1.0-x[i])**sn)/denom
    pl.plot(y, label="P(m | Sp=%d, Sn=%d) | (Area = %f)" % (sp, sn, sum(y)/quality))

  pl.title("Model probability given sample.")
  pl.legend()


def test2(rmodel=0.95, traindata=None, trainsamples=500, testsamplesize=50, quality=50.0, precision=100,
          percentils = [0.05, 0.25, 0.5, 0.75, 0.95]):
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
    nv = sum(boxdata[i])/len(boxdata[i])
    y[i] = nv
    print(m,nv)
  print("Area = %f" % (sum(y)/quality))
  
  pl.xlabel('Model parameter (m)')
  pl.ylabel('P(m1=m2 | Train, Sample)' )
  pl.title('Probability a sample from a given model comes from the same model as the training data.'
           ' Training data is a sample of size=%d from m=%f' % (trainsamples, rmodel))
  pl.xlim([-0.05,1.05])
  for i in range(len(x)):
    boxdata[i] = sorted(boxdata[i])
  plot_perc = []
  for perc in percentils:
    plot_perc.append(list(x[int(perc*precision)] for x in boxdata)) 
    pl.plot(x, plot_perc[-1], label="Percentil %f"%perc)
  for i in range(0, len(plot_perc)-1):
    pl.fill_between(x, plot_perc[i], plot_perc[i+1], alpha=0.25)
  
  pl.plot(x, y, label="Expected P(m1=m2|T=train,S=sample(m=m,s=%d))"%testsamplesize)
  pl.legend()


random.seed(0)    
if False:
  pl.figure()
  test1()

if False:
  pl.figure()
  test1_1()

if True:
  pl.figure()
  test2(rmodel=0.25,trainsamples=500, testsamplesize=500,percentils=[0.05, 0.95])

pl.show()
