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

    out.append(feature_descriptor_label(name))
    for feature, feature_space in features:
      for descriptor in feature_space:
        out[-1] += ' & $%.2f\\%%$' % 0.23
    out[-1] += '\\\\ \\hline'
  map(lambda x: explain_distribution(x[0], x[1]), distributions)
  

  out.append('\\end{tabular}')
  return  '\n'.join(out)

'''
\begin{tabular}{|c|ccc|cc|}
\hline
Label & \multicolumn{3}{c}{Size} & \multicolumn{2}{c}{Shape} \\
      & \begin{sideways}small\end{sideways} & \begin{sideways}medium\end{sideways} & \begin{sideways}large\end{sideways} & square & round \\
\hline \\
kitchen & 0.4 & 0.3 & 0.4 & 0.2 & 0.8 \\
\hline
\end{tabular}


\begin{description}
\item[Label] Kitchen
\item[Room Size] 
\end{description}
'''
