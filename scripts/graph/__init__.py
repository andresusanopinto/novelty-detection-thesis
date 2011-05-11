import matplotlib
matplotlib.use('Agg')

import pylab as pl
from .HintonDiagrams import hinton
from .ROC import ROC as roc


def show():
  pl.show()

def savefig(path):
  pl.savefig(path)

def newfig():
  pl.figure()
