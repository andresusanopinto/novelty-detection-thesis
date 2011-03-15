# -*- coding: utf-8 -*-
# 
# Based on: http://scikit-learn.sourceforge.net/auto_examples/plot_roc_crossval.html
#
import numpy as N
import pylab as P

def ROC(data):
  """Plots a ROC curve."""
  
  def acc(data, value):
    sum = 0
    for v in data:
      if v == value:
        sum += float(1)
      yield sum
  
  fpr = N.array(list(acc(data, False)))
  tpr = N.array(list(acc(data, True)))
  if fpr[-1] != 0: fpr /= fpr[-1]
  if tpr[-1] != 0: tpr /= tpr[-1]
  
  P.figure()
  P.plot(fpr, tpr)
  P.xlim([-0.05,1.05])
  P.ylim([-0.05,1.05])
  P.xlabel('False Positive Rate')
  P.ylabel('True Positive Rate')
  P.title('Receiver operating characteristic')

