

# This file exports the ontology defined on:
# http://teambox.pronobis.pro/projects/iros-paper/pages/data
#
import dataset

labels = set('''
             anteroom bathroom computerlab conferencehall doubleoffice
             hallway kitchen meetingroom professorsoffice robotlab office
             singleoffice
             '''.split())

objects = set('''
              book cerealbox computer robot stapler toiletpaper
              '''.split())

shapes = set('''
             elongated rectangular square
             '''.split())

appearances = set('''
                  bathroom-like hallway-like office-like kitchen-like
                  lab-like meetingroom-like anteroom-like
                  '''.split())

sizes = set('''
            small medium large
            '''.split())

def Label(label):
  assert label in labels
  return ('label', label)

def Object(obj, gamma):
  assert 
  return ('object_%s'%obj, dataset.DiscreteDistribution(d))

def Shape(d):
  assert
  return ('room_size', dataset.DiscreteDistribution(d))

def Appearance(d):
  assert
  return ('room_size', dataset.DiscreteDistribution(d))

def Size(d):
  assert Valid(d, size)
  return ('room_size', dataset.DiscreteDistribution(d))

