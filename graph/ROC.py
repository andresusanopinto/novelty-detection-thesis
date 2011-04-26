# -*- coding: utf-8 -*-
# 
# Based on: http://scikit-learn.sourceforge.net/auto_examples/plot_roc_crossval.html
#
import numpy as N
import pylab as P

def ROC(data, style = 'ro-', label = None):
  """Plots a ROC curve."""
  
  def acc(data):
    sum = 0.0
    for v in data:
      sum += v
      yield sum
  
  fpr = N.array([0.0] + list(acc(map(lambda x:x[0], data))))
  tpr = N.array([0.0] + list(acc(map(lambda x:x[1], data))))
  if fpr[-1] != 0: fpr /= fpr[-1]
  if tpr[-1] != 0: tpr /= tpr[-1]
  
  P.plot(fpr, tpr, style, markevery=(len(fpr)/10, len(fpr)/10), label = label)
  P.xlim([-0.05,1.05])
  P.ylim([-0.05,1.05])
  P.xlabel('False Positive Rate')
  P.ylabel('True Positive Rate')
  P.legend(loc = 'best')

