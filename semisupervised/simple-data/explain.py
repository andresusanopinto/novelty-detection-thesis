import dataset

def ExplainDistributions(features, distributions):
  out = []

  def feature_descriptor_label(descriptor):
    return '\\begin{sideways}%s\\end{sideways}' % descriptor
  
  table_format = '|c'
  for feature, feature_space in features:
    table_format += '|' + ''.join(['c' for x in range(len(feature_space))])
  table_format += '|'
  
  out.append('\\begin{tabular}{%s}' % table_format)
  out.append('\\hline')
  '''Print Header'''
  out.append('')
  for feature, feature_space in features:
    out[-1] += ' & \\multicolumn{%d}{|c|}{%s}' % (len(feature_space),feature)
  out[-1] += '\\\\ \\hline'

  out.append('')
  for feature, feature_space in features:
    for descriptor in feature_space:
      out[-1] += ' & %s' % feature_descriptor_label(descriptor)
  out[-1] += '\\\\ \\hline'
  
  def explain_distribution(name, definition):
    feature_distrib = dict([(f, d) for (f,d) in definition if f != 'label'])
    out.append(feature_descriptor_label(name))
    for feature, feature_space in features:
      assert feature in feature_distrib
      potential = dict([(k,p) for (p, k) in feature_distrib[feature].IterDistributions()])
      for descriptor in feature_space:
        out[-1] += ' & $%.1f\\%%$' % (potential[descriptor]*100.0)
    out[-1] += '\\\\ \\hline'
  map(lambda x: explain_distribution(x[0], x[1]), distributions)
  

  out.append('\\end{tabular}')
  return '\n'.join(out)



def SortThresholds(title, inputs, func, columns = 1):
  out = []
  col = ''.join(['l' for c in range(columns)])
  out.append('\\begin{tabular}{%sr}' % col)
  #out.append('\\hline \\multicolumn{2}{c}{'+title+'}\\\\ \\hline')
  out.append('\\multicolumn{%d}{c}{sample} & threshold \\\\ \\hline' % columns)
  for threshold, sample in sorted(map(lambda x: (func(x[1]), x[0]), inputs), reverse=True):
    out.append('%s & %.3f \\\\' % (sample, threshold))
  out.append('\\end{tabular}')
  return '\n'.join(out)
